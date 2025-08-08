"""
Output writer module for writing final dataframe to output file.
Follows OOP, SOLID principles, and separation of concerns.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import os
from services.file_handler import write_file
from validation.exceptions import OutputWritingError, InvalidConfigurationError
from validation.contracts import (
    IOutputWriter,
    IOutputConfigValidator,
    IOutputConfigExtractor,
    IDataFormatter,
    IFileWriter,
    IOutputResultValidator
)
from constants import DEFAULT_OUTPUT_SHEET, DEFAULT_FILE1_SHEET1, DEFAULT_FILE2_SHEET


class OutputConfigValidator(IOutputConfigValidator):
    """Concrete implementation of output configuration validation"""
    
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validate output configuration"""
        output_path = config.get('output_path')
        
        if not output_path:
            raise InvalidConfigurationError("Output path is required")
        
        if not isinstance(output_path, str):
            raise InvalidConfigurationError("Output path must be a string")
        
        # Check if output directory exists or can be created
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                raise InvalidConfigurationError(f"Cannot create output directory: {str(e)}")


class OutputConfigExtractor(IOutputConfigExtractor):
    """Concrete implementation of output configuration extraction"""
    
    def extract_output_settings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract output settings from configuration"""
        return {
            'output_path': config.get('output_path'),
            'output_sheet': config.get('output_sheet', DEFAULT_OUTPUT_SHEET),
            'null_value': config.get('null_value', ''),
            'file1_path': config.get('file1_path', ''),
            'file2_path': config.get('file2_path', ''),
            'file1_sheet1': config.get('file1_sheet1', DEFAULT_FILE1_SHEET1),
            'file2_sheet': config.get('file2_sheet', DEFAULT_FILE2_SHEET)
        }


class DataFormatter(IDataFormatter):
    """Concrete implementation of data formatting"""
    
    def format_dataframe(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Format dataframe for output with organized column structure"""
        formatted_df = df.copy()
        
        # Handle null values
        null_value = config.get('null_value', '')
        if null_value:
            # Convert categorical columns to object type first to avoid category issues
            categorical_columns = formatted_df.select_dtypes(include=['category']).columns
            for col in categorical_columns:
                formatted_df[col] = formatted_df[col].astype('object')
            
            # Fill null values
            formatted_df = formatted_df.fillna(null_value)
        
        # Reorganize columns in the desired order
        formatted_df = self._reorganize_columns(formatted_df, config)
        
        return formatted_df
    
    def _reorganize_columns(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Reorganize columns: file1 columns first, then file2 columns, then validation columns"""
        if 'JoinKeys' not in df.columns:
            return df
        
        # Get join keys and aggregation info from configuration
        join_keys = config.get('join_keys', {})
        column_mapping = config.get('column_mapping', {})
        aggregation = config.get('aggregation', {})
        
        # Determine join keys (use join_keys if available, otherwise use column_mapping)
        if join_keys and join_keys != 'NA' and isinstance(join_keys, dict) and len(join_keys) > 0:
            left_keys = list(join_keys.keys())
            right_keys = list(join_keys.values())
        else:
            left_keys = list(column_mapping.keys())
            right_keys = list(column_mapping.values())
        
        # Get metric columns from aggregation configuration
        metric_columns = self._get_metric_columns_from_config(aggregation, left_keys, right_keys)
        
        # Get all columns
        all_columns = list(df.columns)
        
        # 1. JoinKeys column (status indicator)
        join_keys_col = ['JoinKeys'] if 'JoinKeys' in all_columns else []
        
        # 2. Organize file1 columns: join keys first, then others, then metrics
        # First, get all file1 columns (those ending with _file1)
        all_file1_cols = [col for col in all_columns if col.endswith('_file1')]
        
        # Categorize file1 columns
        file1_join_keys = [col for col in all_file1_cols if col[:-6] in left_keys]
        file1_metrics = [col for col in all_file1_cols if col[:-6] in metric_columns]
        file1_others = [col for col in all_file1_cols if col not in file1_join_keys and col not in file1_metrics]
        

        
        # 3. Organize file2 columns: join keys first, then others, then metrics (same order as file1)
        # First, get all file2 columns (those ending with _file2)
        all_file2_cols = [col for col in all_columns if col.endswith('_file2')]
        
        file2_join_keys = []
        file2_others = []
        file2_metrics = []
        
        # First, organize by join keys (same order as file1)
        for file1_col in file1_join_keys:
            base_col = file1_col[:-6]  # Remove '_file1' suffix
            file2_col = base_col + '_file2'
            if file2_col in all_file2_cols:
                file2_join_keys.append(file2_col)
        
        # Then, organize others and metrics (same order as file1)
        for file1_col in file1_others:
            base_col = file1_col[:-6]  # Remove '_file1' suffix
            file2_col = base_col + '_file2'
            if file2_col in all_file2_cols:
                file2_others.append(file2_col)
        
        for file1_col in file1_metrics:
            base_col = file1_col[:-6]  # Remove '_file1' suffix
            file2_col = base_col + '_file2'
            if file2_col in all_file2_cols:
                file2_metrics.append(file2_col)
        
        # Note: We only include file2 columns that have corresponding file1 columns to maintain strict order
        # Any remaining file2 columns without file1 counterparts will be in remaining_cols
        
        # 4. Organize validation columns: join keys first, then others, then metrics (same order as file1)
        validation_join_keys = []
        validation_others = []
        validation_metrics = []
        
        # For join keys
        for file1_col in file1_join_keys:
            base_col = file1_col[:-6]  # Remove '_file1' suffix
            comparison_col = base_col + '_vs_' + base_col + '_comparison'
            delta_col = base_col + '_vs_' + base_col + '_delta'
            
            if comparison_col in all_columns:
                validation_join_keys.append(comparison_col)
            if delta_col in all_columns:
                validation_join_keys.append(delta_col)
        
        # For others
        for file1_col in file1_others:
            base_col = file1_col[:-6]  # Remove '_file1' suffix
            comparison_col = base_col + '_vs_' + base_col + '_comparison'
            delta_col = base_col + '_vs_' + base_col + '_delta'
            
            if comparison_col in all_columns:
                validation_others.append(comparison_col)
            if delta_col in all_columns:
                validation_others.append(delta_col)
        
        # For metrics
        for file1_col in file1_metrics:
            base_col = file1_col[:-6]  # Remove '_file1' suffix
            comparison_col = base_col + '_vs_' + base_col + '_comparison'
            delta_col = base_col + '_vs_' + base_col + '_delta'
            
            if comparison_col in all_columns:
                validation_metrics.append(comparison_col)
            if delta_col in all_columns:
                validation_metrics.append(delta_col)
        
        # Add any remaining validation columns that don't follow the pattern
        remaining_validation = [col for col in all_columns if '_vs_' in col and ('_comparison' in col or '_delta' in col) and col not in validation_join_keys + validation_others + validation_metrics]
        validation_others.extend(remaining_validation)
        
        # 5. Join status columns (any other JoinKeys related columns)
        join_status_columns = [col for col in all_columns if 'JoinKeys' in col and col != 'JoinKeys']
        
        # 6. Remaining columns (those not categorized above)
        categorized_cols = (join_keys_col + file1_join_keys + file1_others + file1_metrics + 
                           file2_join_keys + file2_others + file2_metrics + 
                           validation_join_keys + validation_others + validation_metrics + 
                           join_status_columns)
        remaining_cols = [col for col in all_columns if col not in categorized_cols]
        
        # Create the new column order - ALL VALIDATION COLUMNS AT THE END
        new_column_order = (
            join_keys_col +           # 1. JoinKeys status column
            file1_join_keys +         # 2. File1 join keys
            file1_others +            # 3. File1 other columns
            file1_metrics +           # 4. File1 metrics
            file2_join_keys +         # 5. File2 join keys (same order as file1)
            file2_others +            # 6. File2 other columns (same order as file1)
            file2_metrics +           # 7. File2 metrics (same order as file1)
            join_status_columns +     # 8. Join status columns
            remaining_cols +          # 9. Any remaining columns
            validation_join_keys +    # 10. Validation join keys (same order as file1)
            validation_others +       # 11. Validation other columns (same order as file1)
            validation_metrics        # 12. Validation metrics (same order as file1)
        )
        
        # Filter to only include columns that exist in the dataframe
        new_column_order = [col for col in new_column_order if col in df.columns]
        
        # Reorder the dataframe
        reorganized_df = df[new_column_order]
        
        return reorganized_df
    
    def _get_metric_columns_from_config(self, aggregation: Dict[str, Any], left_keys: List[str], right_keys: List[str]) -> List[str]:
        """Get metric columns from aggregation configuration"""
        metric_columns = []
        
        if not aggregation or aggregation == 'NA':
            return metric_columns
        
        # Get metric columns from file1_columns aggregation
        file1_columns = aggregation.get('file1_columns', {})
        if isinstance(file1_columns, dict):
            for agg_type, columns in file1_columns.items():
                if columns and columns != 'NA':
                    if isinstance(columns, list):
                        metric_columns.extend(columns)
                    elif isinstance(columns, str):
                        metric_columns.append(columns)
        
        # Get metric columns from file2_columns aggregation
        file2_columns = aggregation.get('file2_columns', {})
        if isinstance(file2_columns, dict):
            for agg_type, columns in file2_columns.items():
                if columns and columns != 'NA':
                    if isinstance(columns, list):
                        # Map file2 column names to file1 column names for consistency
                        for col in columns:
                            if col in right_keys:
                                # Find corresponding left key
                                for left_key, right_key in zip(left_keys, right_keys):
                                    if right_key == col:
                                        metric_columns.append(left_key)
                                        break
                            else:
                                metric_columns.append(col)
                    elif isinstance(columns, str):
                        if columns in right_keys:
                            # Find corresponding left key
                            for left_key, right_key in zip(left_keys, right_keys):
                                if right_key == columns:
                                    metric_columns.append(left_key)
                                    break
                        else:
                            metric_columns.append(columns)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_metrics = []
        for col in metric_columns:
            if col not in seen:
                seen.add(col)
                unique_metrics.append(col)
        
        return unique_metrics


class FileWriter(IFileWriter):
    """Concrete implementation of file writing"""
    
    def write_file(self, df: pd.DataFrame, output_path: str, output_sheet: str) -> None:
        """Write dataframe to file"""
        try:
            write_file(df, output_path, output_sheet)
        except Exception as e:
            raise OutputWritingError(f"Failed to write file: {str(e)}")


class OutputResultValidator(IOutputResultValidator):
    """Concrete implementation of output result validation"""
    
    def validate_result(self, df: pd.DataFrame, output_path: str) -> None:
        """Validate output result"""
        if df is None:
            raise OutputWritingError("Dataframe is None")
        
        if df.empty:
            print("⚠️  Warning: Output dataframe is empty")
        
        if not os.path.exists(output_path):
            raise OutputWritingError(f"Output file was not created: {output_path}")


class OutputWriter(IOutputWriter):
    """Concrete implementation of output writing"""
    
    def __init__(self):
        self._config_validator = OutputConfigValidator()
        self._config_extractor = OutputConfigExtractor()
        self._data_formatter = DataFormatter()
        self._file_writer = FileWriter()
        self._result_validator = OutputResultValidator()
    
    def write_output(self, df: pd.DataFrame, config: Dict[str, Any]) -> None:
        """
        Write dataframe to output file based on configuration
        
        Args:
            df: Final dataframe to write
            config: Configuration dictionary containing output settings
            
        Raises:
            OutputWritingError: If writing fails
            InvalidConfigurationError: If configuration is invalid
        """
        try:
            self._ensure_dataframe_valid(df)
            
            # Validate configuration
            self._config_validator.validate_configuration(config)
            
            # Extract configuration parameters
            output_settings = self._config_extractor.extract_output_settings(config)
            output_path = output_settings['output_path']
            output_sheet = output_settings['output_sheet']
            
            # Format dataframe
            formatted_df = self._data_formatter.format_dataframe(df, output_settings)
            
            # Write file
            self._file_writer.write_file(formatted_df, output_path, output_sheet)
            
            # Validate result
            self._result_validator.validate_result(formatted_df, output_path)
            
            # Print success information
            self._print_success_info(formatted_df, output_path, output_sheet)
            
        except (InvalidConfigurationError, OutputWritingError):
            raise
        except Exception as e:
            raise OutputWritingError(f"Failed to write output file: {str(e)}")
    
    def _ensure_dataframe_valid(self, df: pd.DataFrame) -> None:
        if df is None:
            raise OutputWritingError("Input dataframe cannot be None")
        
        if not isinstance(df, pd.DataFrame):
            raise OutputWritingError("Input must be a pandas DataFrame")
    
    def _print_success_info(self, df: pd.DataFrame, output_path: str, output_sheet: str) -> None:
        """Print success information"""
        print(f"✓ Output file written successfully!")
        print(f"  File: {output_path}")
        print(f"  Sheet: {output_sheet}")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Columns: {list(df.columns)}") 