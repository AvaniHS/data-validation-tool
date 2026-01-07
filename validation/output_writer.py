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
    
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        output_path = config.get('output_path')
        
        if not output_path:
            raise InvalidConfigurationError("Output path is required")
        
        if not isinstance(output_path, str):
            raise InvalidConfigurationError("Output path must be a string")
        
        output_directory = os.path.dirname(output_path)
        if output_directory and not os.path.exists(output_directory):
            try:
                os.makedirs(output_directory, exist_ok=True)
            except Exception as e:
                raise InvalidConfigurationError(f"Cannot create output directory: {str(e)}")


class OutputConfigExtractor(IOutputConfigExtractor):
    
    def extract_output_settings(self, config: Dict[str, Any]) -> Dict[str, Any]:
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
    
    def _get_column_suffixes(self, df: pd.DataFrame, config: Dict[str, Any] = None) -> Tuple[str, str]:
        """Get column suffixes from dataframe attrs or generate from config."""
        if hasattr(df, 'attrs') and 'left_suffix' in df.attrs and 'right_suffix' in df.attrs:
            return df.attrs['left_suffix'], df.attrs['right_suffix']
        
        if config:
            import os
            number_of_files = config.get('number_of_files', 2)
            
            if number_of_files == 1:
                sheet1 = config.get('file1_sheet1', 'Sheet1')
                sheet2 = config.get('file1_sheet2', 'Sheet2')
                left_suffix = f"_{self._sanitize_name(sheet1)}"
                right_suffix = f"_{self._sanitize_name(sheet2)}"
            else:
                sheet1 = config.get('file1_sheet1', '')
                sheet2 = config.get('file2_sheet', '')
                
                if sheet1 and sheet2:
                    left_suffix = f"_{self._sanitize_name(sheet1)}"
                    right_suffix = f"_{self._sanitize_name(sheet2)}"
                else:
                    file1_path = config.get('file1_path', '')
                    file2_path = config.get('file2_path', '')
                    file1_name = os.path.splitext(os.path.basename(file1_path))[0] if file1_path else 'file1'
                    file2_name = os.path.splitext(os.path.basename(file2_path))[0] if file2_path else 'file2'
                    left_suffix = f"_{self._sanitize_name(file1_name)}"
                    right_suffix = f"_{self._sanitize_name(file2_name)}"
            
            return left_suffix, right_suffix
        
        return '_file1', '_file2'
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize file/sheet name for use as column suffix."""
        if not name:
            return 'file'
        sanitized = name.replace(' ', '_').replace('-', '_').replace('.', '_')
        sanitized = ''.join(c if c.isalnum() or c == '_' else '_' for c in sanitized)
        sanitized = sanitized.strip('_')[:50]
        return sanitized if sanitized else 'file'
    
    def format_dataframe(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Intelligently optimized dataframe formatting for performance."""
        # Performance optimization: Smart formatting based on dataset size
        null_value = config.get('null_value', '')
        
        if len(df) < 5000:
            # Small datasets: Full formatting
            formatted_dataframe = df.copy()
            if null_value:
                categorical_columns = formatted_dataframe.select_dtypes(include=['category']).columns
                if len(categorical_columns) > 0:
                    formatted_dataframe[categorical_columns] = formatted_dataframe[categorical_columns].astype('object')
                formatted_dataframe = formatted_dataframe.fillna(null_value)
            return formatted_dataframe
        elif len(df) < 20000:
            # Medium datasets: Minimal formatting
            if null_value:
                df = df.fillna(null_value)
            return df
        else:
            # Large datasets: No formatting, direct pass-through
            return df
    
    def _reorganize_columns(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        if 'JoinKeys' not in df.columns:
            return df
        
        # Check if detailed delta analysis is enabled
        detailed_delta_analysis = config.get('detailed_metric_delta_analysis', '').lower() == 'yes'
        
        # Get suffixes from dataframe attrs or generate from config
        left_suffix, right_suffix = self._get_column_suffixes(df, config)
        
        # Use the same join key extraction logic as the joiner
        from validation.data_joiner import JoinKeyExtractor
        extractor = JoinKeyExtractor()
        left_keys, right_keys = extractor.extract_join_keys(config)
        
        column_mapping = config.get('column_mapping', {})
        aggregation = config.get('aggregation', {})
        
        metric_columns = self._get_metric_columns_from_config(aggregation, left_keys, right_keys)
        
        all_columns = list(df.columns)
        
        join_keys_column = ['JoinKeys'] if 'JoinKeys' in all_columns else []
        
        all_file1_columns = [col for col in all_columns if col.endswith(left_suffix)]
        
        file1_join_key_columns = [col for col in all_file1_columns if col[:-len(left_suffix)] in left_keys]
        file1_metric_columns = [col for col in all_file1_columns if col[:-len(left_suffix)] in metric_columns]
        file1_other_columns = [col for col in all_file1_columns if col not in file1_join_key_columns and col not in file1_metric_columns]
        
        all_file2_columns = [col for col in all_columns if col.endswith(right_suffix)]
        
        file2_join_key_columns = []
        file2_other_columns = []
        file2_metric_columns = []
        
        for file1_column in file1_join_key_columns:
            base_column = file1_column[:-len(left_suffix)]
            file2_column = base_column + right_suffix
            if file2_column in all_file2_columns:
                file2_join_key_columns.append(file2_column)
        
        for file1_column in file1_other_columns:
            base_column = file1_column[:-len(left_suffix)]
            file2_column = base_column + right_suffix
            if file2_column in all_file2_columns:
                file2_other_columns.append(file2_column)
        
        for file1_column in file1_metric_columns:
            base_column = file1_column[:-len(left_suffix)]
            file2_column = base_column + right_suffix
            if file2_column in all_file2_columns:
                file2_metric_columns.append(file2_column)
        
        validation_join_key_columns = []
        validation_other_columns = []
        validation_metric_columns = []
        
        for file1_column in file1_join_key_columns:
            base_column = file1_column[:-len(left_suffix)]
            # Find corresponding file2 column name from column mapping
            file2_column_name = column_mapping.get(base_column, base_column)
            # Construct comparison column name with suffixes
            comparison_column = f"{base_column}{left_suffix}_vs_{file2_column_name}{right_suffix}_comparison"
            
            if comparison_column in all_columns:
                validation_join_key_columns.append(comparison_column)
            
            # Only add delta columns if detailed_metric_delta_analysis is enabled
            if detailed_delta_analysis:
                delta_column = f"{base_column}{left_suffix}_vs_{file2_column_name}{right_suffix}_delta"
                percentage_delta_column = f"{base_column}{left_suffix}_vs_{file2_column_name}{right_suffix}_delta%"
                if delta_column in all_columns:
                    validation_join_key_columns.append(delta_column)
                if percentage_delta_column in all_columns:
                    validation_join_key_columns.append(percentage_delta_column)
        
        for file1_column in file1_other_columns:
            base_column = file1_column[:-len(left_suffix)]
            # Find corresponding file2 column name from column mapping
            file2_column_name = column_mapping.get(base_column, base_column)
            # Construct comparison column name with suffixes
            comparison_column = f"{base_column}{left_suffix}_vs_{file2_column_name}{right_suffix}_comparison"
            
            if comparison_column in all_columns:
                validation_other_columns.append(comparison_column)
            
            # Only add delta columns if detailed_metric_delta_analysis is enabled
            if detailed_delta_analysis:
                delta_column = f"{base_column}{left_suffix}_vs_{file2_column_name}{right_suffix}_delta"
                percentage_delta_column = f"{base_column}{left_suffix}_vs_{file2_column_name}{right_suffix}_delta%"
                if delta_column in all_columns:
                    validation_other_columns.append(delta_column)
                if percentage_delta_column in all_columns:
                    validation_other_columns.append(percentage_delta_column)
        
        for file1_column in file1_metric_columns:
            base_column = file1_column[:-len(left_suffix)]
            # Find corresponding file2 column name from column mapping
            file2_column_name = column_mapping.get(base_column, base_column)
            # Construct comparison column name with suffixes
            comparison_column = f"{base_column}{left_suffix}_vs_{file2_column_name}{right_suffix}_comparison"
            
            if comparison_column in all_columns:
                validation_metric_columns.append(comparison_column)
            
            # Only add delta columns if detailed_metric_delta_analysis is enabled
            if detailed_delta_analysis:
                delta_column = f"{base_column}{left_suffix}_vs_{file2_column_name}{right_suffix}_delta"
                percentage_delta_column = f"{base_column}{left_suffix}_vs_{file2_column_name}{right_suffix}_delta%"
                if delta_column in all_columns:
                    validation_metric_columns.append(delta_column)
                if percentage_delta_column in all_columns:
                    validation_metric_columns.append(percentage_delta_column)
        
        # Find remaining validation columns (only comparison columns, or include delta if enabled)
        if detailed_delta_analysis:
            remaining_validation_columns = [col for col in all_columns if '_vs_' in col and ('_comparison' in col or '_delta' in col or '_delta%' in col) and col not in validation_join_key_columns + validation_other_columns + validation_metric_columns]
        else:
            remaining_validation_columns = [col for col in all_columns if '_vs_' in col and '_comparison' in col and col not in validation_join_key_columns + validation_other_columns + validation_metric_columns]
        validation_other_columns.extend(remaining_validation_columns)
        
        join_status_columns = [col for col in all_columns if 'JoinKeys' in col and col != 'JoinKeys']
        
        categorized_columns = (join_keys_column + file1_join_key_columns + file1_other_columns + file1_metric_columns + 
                           file2_join_key_columns + file2_other_columns + file2_metric_columns + 
                           validation_join_key_columns + validation_other_columns + validation_metric_columns + 
                           join_status_columns)
        remaining_columns = [col for col in all_columns if col not in categorized_columns]
        
        new_column_order = (
            join_keys_column +
            file1_join_key_columns +
            file1_other_columns +
            file1_metric_columns +
            file2_join_key_columns +
            file2_other_columns +
            file2_metric_columns +
            join_status_columns +
            remaining_columns +
            validation_join_key_columns +
            validation_other_columns +
            validation_metric_columns
        )
        
        new_column_order = [col for col in new_column_order if col in df.columns]
        
        reorganized_dataframe = df[new_column_order]
        
        return reorganized_dataframe
    
    def _get_metric_columns_from_config(self, aggregation: Dict[str, Any], left_keys: List[str], right_keys: List[str]) -> List[str]:
        metric_columns = []
        
        if not aggregation or aggregation == 'NA':
            return metric_columns
        
        file1_columns = aggregation.get('file1_columns', {})
        if isinstance(file1_columns, dict):
            for aggregation_type, columns in file1_columns.items():
                if columns and columns != 'NA':
                    if isinstance(columns, list):
                        metric_columns.extend(columns)
                    elif isinstance(columns, str):
                        metric_columns.append(columns)
        
        file2_columns = aggregation.get('file2_columns', {})
        if isinstance(file2_columns, dict):
            for aggregation_type, columns in file2_columns.items():
                if columns and columns != 'NA':
                    if isinstance(columns, list):
                        for column in columns:
                            if column in right_keys:
                                for left_key, right_key in zip(left_keys, right_keys):
                                    if right_key == column:
                                        metric_columns.append(left_key)
                                        break
                            else:
                                metric_columns.append(column)
                    elif isinstance(columns, str):
                        if columns in right_keys:
                            for left_key, right_key in zip(left_keys, right_keys):
                                if right_key == columns:
                                    metric_columns.append(left_key)
                                    break
                        else:
                            metric_columns.append(columns)
        
        seen_columns = set()
        unique_metric_columns = []
        for column in metric_columns:
            if column not in seen_columns:
                seen_columns.add(column)
                unique_metric_columns.append(column)
        
        return unique_metric_columns


class FileWriter(IFileWriter):
    
    def write_file(self, df: pd.DataFrame, output_path: str, output_sheet: str) -> None:
        try:
            write_file(df, output_path, output_sheet)
        except Exception as e:
            raise OutputWritingError(f"Failed to write file: {str(e)}")


class OutputResultValidator(IOutputResultValidator):
    
    def validate_result(self, df: pd.DataFrame, output_path: str) -> None:
        if df is None:
            raise OutputWritingError("Dataframe is None")
        
        if df.empty:
            print("⚠️  Warning: Output dataframe is empty")
        
        if not os.path.exists(output_path):
            raise OutputWritingError(f"Output file was not created: {output_path}")


class OutputWriter(IOutputWriter):
    
    def __init__(self):
        self._config_validator = OutputConfigValidator()
        self._config_extractor = OutputConfigExtractor()
        self._data_formatter = DataFormatter()
        self._file_writer = FileWriter()
        self._result_validator = OutputResultValidator()
    
    def write_output(self, df: pd.DataFrame, config: Dict[str, Any]) -> None:
        try:
            # Performance optimization: Smart validation based on dataset size
            if len(df) < 10000:
                # Small-medium datasets: Full validation
                self._ensure_dataframe_valid(df)
                self._config_validator.validate_configuration(config)
            else:
                # Large datasets: Essential validation only
                if df is None or df.empty:
                    raise OutputWritingError("Dataframe is None or empty")
            
            output_settings = self._config_extractor.extract_output_settings(config)
            output_path = output_settings['output_path']
            output_sheet = output_settings['output_sheet']
            
            formatted_dataframe = self._data_formatter.format_dataframe(df, output_settings)
            
            self._file_writer.write_file(formatted_dataframe, output_path, output_sheet)
            
            # Performance optimization: Smart result validation
            if len(formatted_dataframe) < 10000:
                # Small-medium datasets: Full validation
                self._result_validator.validate_result(formatted_dataframe, output_path)
            else:
                # Large datasets: Essential validation only
                if not os.path.exists(output_path):
                    raise OutputWritingError(f"Output file was not created: {output_path}")
            
            self._print_success_info(formatted_dataframe, output_path, output_sheet)
            
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
        # Performance optimization: Minimal console output
        print(f"✓ Output written: {os.path.basename(output_path)} ({len(df)} rows)") 