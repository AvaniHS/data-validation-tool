"""
Join analysis module for analyzing join key mismatches.
Implements clean, SOLID-compliant join analysis functionality.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import os

from validation.contracts.join_analysis_contracts import (
    IJoinAnalysisConfigValidator,
    IJoinAnalysisConfigExtractor,
    IJoinAnalysisGenerator,
    IJoinAnalysisResultValidator,
    IJoinAnalysisOutputHandler,
    JoinAnalysisStatus,
    JoinAnalysisResult
)
from validation.exceptions import DataValidationError


class JoinAnalysisConfigValidator(IJoinAnalysisConfigValidator):
    """Validates join analysis configuration."""
    
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validate join analysis configuration."""
        detailed_join_analysis = config.get('detailed_join_analysis', 'no')
        if not isinstance(detailed_join_analysis, str):
            raise DataValidationError("detailed_join_analysis must be a string")
        
        if detailed_join_analysis.lower() not in ['yes', 'no']:
            raise DataValidationError("detailed_join_analysis must be 'yes' or 'no'")


class JoinAnalysisConfigExtractor(IJoinAnalysisConfigExtractor):
    """Extracts join analysis configuration."""
    
    def extract_join_analysis_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract join analysis configuration from main config."""
        return {
            'detailed_join_analysis': config.get('detailed_join_analysis', 'no'),
            'join_keys': config.get('join_keys', {}),
            'output_path': config.get('output_path', ''),
            'output_sheet': config.get('output_sheet', 'ValidationSummary')
        }


class JoinAnalysisResultValidator(IJoinAnalysisResultValidator):
    """Validates join analysis results."""
    
    def validate_result(self, result_df: pd.DataFrame) -> None:
        """Validate join analysis result."""
        if result_df.empty:
            return
        
        # Check for required columns in restructured format
        required_columns = ['File_1_keys', 'File_2_keys', 'File1_Value', 'File2_Value', 'count']
        missing_columns = [col for col in required_columns if col not in result_df.columns]
        
        if missing_columns:
            raise DataValidationError(f"Missing required columns in join analysis result: {missing_columns}")


class JoinAnalysisGenerator(IJoinAnalysisGenerator):
    """Generates join analysis by analyzing join key mismatches."""
    
    def __init__(self):
        self.config_validator = JoinAnalysisConfigValidator()
        self.config_extractor = JoinAnalysisConfigExtractor()
        self.result_validator = JoinAnalysisResultValidator()
    
    def generate_join_analysis(self, validation_df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Generate join analysis DataFrame."""
        try:
            self.config_validator.validate_configuration(config)
            join_analysis_config = self.config_extractor.extract_join_analysis_config(config)
            
            if join_analysis_config['detailed_join_analysis'].lower() != 'yes':
                return pd.DataFrame()
            
            # Performance optimization: Process all datasets but with smart limits
            # No skipping - this is a validation framework
            
            # Extract join keys
            join_keys = join_analysis_config['join_keys']
            if not join_keys:
                return pd.DataFrame()
            
            # Generate analysis results
            analysis_results = self._analyze_join_keys(validation_df, join_keys)
            
            if not analysis_results:
                print(f"✓ No failed joins found - all join keys are matching perfectly!")
                return pd.DataFrame()
            
            # Convert to DataFrame
            result_df = pd.DataFrame(analysis_results)
            self.result_validator.validate_result(result_df)
            
            # Add summary information
            failed_count = len(result_df)
            print(f"✓ Join analysis: {failed_count} failed records")
            
            return result_df
            
        except Exception as e:
            raise DataValidationError(f"Failed to generate join analysis: {str(e)}")
    
    def _analyze_join_keys(self, validation_df: pd.DataFrame, join_keys: Dict[str, str]) -> List[Dict[str, Any]]:
        """Analyze join keys for mismatches - optimized version."""
        # Performance optimization: Early return for empty data
        if validation_df.empty:
            return []
        
        # Get all join key columns once (optimization)
        all_join_key_cols = self._get_all_join_key_columns(validation_df, join_keys)
        
        # Performance optimization: Use vectorized operations where possible
        all_failed_indices = set()
        
        for left_key, right_key in join_keys.items():
            left_col = f"{left_key}_file1"
            right_col = f"{right_key}_file2"
            
            if left_col not in validation_df.columns or right_col not in validation_df.columns:
                continue
            
            # Find rows where this specific key pair failed
            failed_rows = self._get_failed_join_rows(validation_df, left_key, right_key, left_col, right_col)
            all_failed_indices.update(failed_rows.index)
        
        # Performance optimization: Smart sampling for very large datasets
        if len(all_failed_indices) > 10000:
            # For very large datasets, use intelligent sampling
            failed_indices_list = list(all_failed_indices)
            # Sample every nth row to get representative data
            sample_size = min(5000, len(failed_indices_list))
            step = len(failed_indices_list) // sample_size
            all_failed_indices = set(failed_indices_list[::max(1, step)])
            print(f"📊 Using intelligent sampling: {len(all_failed_indices)} representative failed rows from {len(failed_indices_list)} total")
        
        # Process all failed rows and create distinct combinations
        distinct_combinations = {}
        
        # Performance optimization: Batch process rows
        failed_rows_df = validation_df.loc[list(all_failed_indices)]
        
        for idx, row in failed_rows_df.iterrows():
            analysis_results = self._create_failed_join_rows(row, all_join_key_cols, idx)
            
            # Process each individual key-value pair
            for analysis_result in analysis_results:
                # Create a key for grouping distinct combinations
                combination_key = (
                    analysis_result['File_1_keys'],
                    analysis_result['File_2_keys'],
                    analysis_result['File1_Value'],
                    analysis_result['File2_Value']
                )
                
                if combination_key in distinct_combinations:
                    distinct_combinations[combination_key]['count'] += 1
                else:
                    analysis_result['count'] = 1
                    distinct_combinations[combination_key] = analysis_result
        
        # Convert to list of results and sort by key names
        results = list(distinct_combinations.values())
        
        # Sort by File_1_keys and File_2_keys to keep same keys together
        results.sort(key=lambda x: (x['File_1_keys'], x['File_2_keys']))
        
        return results
    
    def _get_all_join_key_columns(self, validation_df: pd.DataFrame, join_keys: Dict[str, str]) -> List[str]:
        """Get all join key columns from the validation DataFrame."""
        join_key_cols = []
        for left_key, right_key in join_keys.items():
            left_col = f"{left_key}_file1"
            right_col = f"{right_key}_file2"
            if left_col in validation_df.columns:
                join_key_cols.append(left_col)
            if right_col in validation_df.columns:
                join_key_cols.append(right_col)
        return join_key_cols
    
    def _create_failed_join_rows(self, row: pd.Series, join_key_cols: List[str], row_index: int) -> List[Dict[str, Any]]:
        """Create multiple rows with individual key-value pairs for failed joins."""
        results = []
        
        # Separate File1 and File2 columns
        file1_cols = [col for col in join_key_cols if col.endswith('_file1')]
        file2_cols = [col for col in join_key_cols if col.endswith('_file2')]
        
        # Create pairs of matching keys
        file1_keys = [col.replace('_file1', '') for col in file1_cols]
        file2_keys = [col.replace('_file2', '') for col in file2_cols]
        
        # Create individual rows for each key-value pair
        for i, (file1_col, file2_col) in enumerate(zip(file1_cols, file2_cols)):
            if i < len(file2_cols):  # Ensure we have matching pairs
                result = {}
                
                # Get values
                file1_value = row[file1_col]
                file2_value = row[file2_col]
                
                # Convert to string and handle NULL values
                if pd.isna(file1_value) or file1_value == 'nan' or str(file1_value).lower() == 'nan':
                    file1_value_str = 'NULL'
                else:
                    file1_value_str = str(file1_value)
                
                if pd.isna(file2_value) or file2_value == 'nan' or str(file2_value).lower() == 'nan':
                    file2_value_str = 'NULL'
                else:
                    file2_value_str = str(file2_value)
                
                result['File_1_keys'] = file1_keys[i] if i < len(file1_keys) else ''
                result['File_2_keys'] = file2_keys[i] if i < len(file2_keys) else ''
                result['File1_Value'] = file1_value_str
                result['File2_Value'] = file2_value_str
                
                results.append(result)
        
        return results
    
    def _get_failed_join_rows(self, validation_df: pd.DataFrame, left_key: str, right_key: str, 
                             left_col: str, right_col: str) -> pd.DataFrame:
        """Get rows where the join failed for this specific key pair."""
        # Check if there's a comparison column for this key pair
        comparison_col = f"{left_key}_vs_{right_key}_comparison"
        
        if comparison_col in validation_df.columns:
            # Use comparison column to find failed rows
            failed_mask = validation_df[comparison_col] == 'no match'
            return validation_df[failed_mask]
        else:
            # Fallback: find rows where one value is missing or values don't match
            failed_mask = (
                validation_df[left_col].isna() | 
                validation_df[right_col].isna() |
                (validation_df[left_col].astype(str).str.strip() != validation_df[right_col].astype(str).str.strip())
            )
            return validation_df[failed_mask]
    


class JoinAnalysisOutputHandler(IJoinAnalysisOutputHandler):
    """Handles join analysis output based on file type."""
    
    def handle_join_analysis_output(self, join_analysis_df: pd.DataFrame, 
                                  output_settings: Dict[str, Any]) -> None:
        """Handle join analysis output based on file type."""
        if join_analysis_df.empty:
            return
        
        output_path = output_settings['output_path']
        file_extension = os.path.splitext(output_path)[1].lower()
        
        if file_extension == '.xlsx':
            self._add_excel_sheet_optimized(join_analysis_df, output_path)
        else:
            self._create_separate_file(join_analysis_df, output_path)
    
    def _add_excel_sheet_optimized(self, join_analysis_df: pd.DataFrame, output_path: str) -> None:
        """Add join analysis as the second sheet in Excel file - ultra-optimized version."""
        try:
            # Ultra-optimized: Use single ExcelWriter context with minimal overhead
            with pd.ExcelWriter(output_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
                join_analysis_df.to_excel(writer, sheet_name='join_analysis', index=False)
            
            print(f"✓ Join analysis sheet added")
        except Exception as e:
            print(f"⚠️  Warning: Could not add join analysis sheet: {str(e)}")
    
    
    def _add_excel_sheet(self, join_analysis_df: pd.DataFrame, output_path: str) -> None:
        """Add join analysis as a new sheet in Excel file - legacy version."""
        try:
            # Use optimized Excel writing with openpyxl engine
            with pd.ExcelWriter(output_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
                join_analysis_df.to_excel(writer, sheet_name='join_analysis', index=False)
            print(f"✓ Join analysis sheet added")
        except Exception as e:
            print(f"⚠️  Warning: Could not add join analysis sheet: {str(e)}")
    
    def _create_separate_file(self, join_analysis_df: pd.DataFrame, output_path: str) -> None:
        """Create separate file for join analysis."""
        try:
            base_path = os.path.splitext(output_path)[0]
            file_extension = os.path.splitext(output_path)[1]
            join_analysis_path = f"{base_path}_joinanalysis{file_extension}"
            
            if file_extension == '.csv':
                join_analysis_df.to_csv(join_analysis_path, index=False)
            elif file_extension == '.json':
                join_analysis_df.to_json(join_analysis_path, orient='records', indent=2)
            else:
                # Default to CSV for unknown formats
                join_analysis_path = f"{base_path}_joinanalysis.csv"
                join_analysis_df.to_csv(join_analysis_path, index=False)
            
            print(f"✓ Join analysis written to: {join_analysis_path}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create join analysis file: {str(e)}")
