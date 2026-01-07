from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
from validation.exceptions import DataJoiningError, InvalidConfigurationError
from validation.contracts import (
    IJoinKeyExtractor,
    IJoinKeyValidator,
    IJoinExecutor,
    IJoinResultValidator,
    IDataJoiner
)
from constants import DEFAULT_NA_VALUE


class JoinKeyExtractor(IJoinKeyExtractor):
    
    def extract_join_keys(self, config: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        join_keys = config.get('join_keys', {})
        column_mapping = config.get('column_mapping', {})
        file1_metric_list = config.get('file1_metric_list', [])
        file2_metric_list = config.get('file2_metric_list', [])
        
        # Priority 1: If join_keys are specified, use them
        if join_keys and join_keys != DEFAULT_NA_VALUE and isinstance(join_keys, dict):
            return self._extract_from_join_keys(join_keys)
        
        # Priority 2: If metrics are specified, ignore them and use other mapped columns
        elif file1_metric_list or file2_metric_list:
            return self._extract_from_column_mapping_excluding_metrics(column_mapping, file1_metric_list, file2_metric_list)
        
        # Priority 3: Use all mapped columns to join
        else:
            return self._extract_from_column_mapping(column_mapping)
    
    def _extract_from_join_keys(self, join_keys: Dict[str, str]) -> Tuple[List[str], List[str]]:
        left_keys = list(join_keys.keys())
        right_keys = list(join_keys.values())
        return left_keys, right_keys
    
    def _extract_from_column_mapping_excluding_metrics(self, column_mapping: Dict[str, str], 
                                                      file1_metrics: List[str], file2_metrics: List[str]) -> Tuple[List[str], List[str]]:
        # Get all metrics (from both file1 and file2 metric lists)
        all_metrics = set(file1_metrics + file2_metrics)
        
        # Filter out metric columns from column mapping
        filtered_mapping = {k: v for k, v in column_mapping.items() if k not in all_metrics and v not in all_metrics}
        
        if not filtered_mapping:
            # If no non-metric columns, fall back to all columns
            return self._extract_from_column_mapping(column_mapping)
        
        left_keys = list(filtered_mapping.keys())
        right_keys = list(filtered_mapping.values())
        return left_keys, right_keys
    
    def _extract_from_column_mapping(self, column_mapping: Dict[str, str]) -> Tuple[List[str], List[str]]:
        left_keys = list(column_mapping.keys())
        right_keys = list(column_mapping.values())
        return left_keys, right_keys


class JoinKeyValidator(IJoinKeyValidator):
    
    def validate_join_keys(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                          left_keys: List[str], right_keys: List[str]) -> None:
        missing_in_df1 = [key for key in left_keys if key not in df1.columns]
        missing_in_df2 = [key for key in right_keys if key not in df2.columns]
        
        if missing_in_df1 or missing_in_df2:
            error_message = self._build_validation_error_message(
                df1, df2, missing_in_df1, missing_in_df2
            )
            raise DataJoiningError(error_message)
    
    def _build_validation_error_message(self, df1: pd.DataFrame, df2: pd.DataFrame,
                                      missing_in_df1: List[str], missing_in_df2: List[str]) -> str:
        error_message = "Join keys validation failed:\n"
        
        if missing_in_df1:
            error_message += f"  Missing join keys in df1: {', '.join(missing_in_df1)}\n"
            error_message += f"  Available columns in df1: {', '.join(sorted(df1.columns))}\n"
        
        if missing_in_df2:
            error_message += f"  Missing join keys in df2: {', '.join(missing_in_df2)}\n"
            error_message += f"  Available columns in df2: {', '.join(sorted(df2.columns))}\n"
        
        return error_message


class JoinExecutor(IJoinExecutor):
    
    def execute_join(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                    left_keys: List[str], right_keys: List[str], 
                    config: Dict[str, Any] = None) -> pd.DataFrame:
        try:
            left_suffix, right_suffix = self._generate_column_suffixes(config)
            
            df1_copy = df1.copy()
            df2_copy = df2.copy()
            
            # Rename ALL columns in both dataframes to add suffixes
            df1_copy.columns = [f"{col}{left_suffix}" for col in df1_copy.columns]
            df2_copy.columns = [f"{col}{right_suffix}" for col in df2_copy.columns]
            
            # Create new key lists with suffixed names
            left_keys_suffixed = [f"{key}{left_suffix}" for key in left_keys]
            right_keys_suffixed = [f"{key}{right_suffix}" for key in right_keys]
            
            # Normalize join key values before merging
            for left_key_suffixed, right_key_suffixed in zip(left_keys_suffixed, right_keys_suffixed):
                df1_copy[left_key_suffixed] = self._normalize_join_key_for_string_comparison(
                    df1_copy[left_key_suffixed]
                )
                df2_copy[right_key_suffixed] = self._normalize_join_key_for_string_comparison(
                    df2_copy[right_key_suffixed]
                )
            
            # Perform merge - no need for suffixes parameter since all columns already have suffixes
            joined_df = df1_copy.merge(
                df2_copy,
                left_on=left_keys_suffixed,
                right_on=right_keys_suffixed,
                how='outer'
            )
            
            joined_df = self._remove_unnamed_columns(joined_df)
            joined_df = self._add_join_keys_status(joined_df, left_keys, right_keys, left_suffix, right_suffix)
            
            # Store suffixes in joined_df attributes for use by other components
            joined_df.attrs['left_suffix'] = left_suffix
            joined_df.attrs['right_suffix'] = right_suffix
            
            return joined_df
            
        except Exception as e:
            raise DataJoiningError(f"Failed to execute join: {str(e)}")
    
    def _generate_column_suffixes(self, config: Dict[str, Any] = None) -> Tuple[str, str]:
        """Generate column suffixes from file or sheet names."""
        if config is None:
            return '_file1', '_file2'
        
        import os
        
        number_of_files = config.get('number_of_files', 2)
        
        if number_of_files == 1:
            # Single file with two sheets - use sheet names
            sheet1 = config.get('file1_sheet1', 'Sheet1')
            sheet2 = config.get('file1_sheet2', 'Sheet2')
            left_suffix = f"_{self._sanitize_name(sheet1)}"
            right_suffix = f"_{self._sanitize_name(sheet2)}"
        else:
            # Two separate files - use file names or sheet names
            file1_path = config.get('file1_path', '')
            file2_path = config.get('file2_path', '')
            
            # Try to use sheet names first, fall back to file names
            sheet1 = config.get('file1_sheet1', '')
            sheet2 = config.get('file2_sheet', '')
            
            if sheet1 and sheet2:
                left_suffix = f"_{self._sanitize_name(sheet1)}"
                right_suffix = f"_{self._sanitize_name(sheet2)}"
            else:
                # Use file names
                file1_name = os.path.splitext(os.path.basename(file1_path))[0] if file1_path else 'file1'
                file2_name = os.path.splitext(os.path.basename(file2_path))[0] if file2_path else 'file2'
                left_suffix = f"_{self._sanitize_name(file1_name)}"
                right_suffix = f"_{self._sanitize_name(file2_name)}"
        
        return left_suffix, right_suffix
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize file/sheet name for use as column suffix."""
        if not name:
            return 'file'
        # Replace invalid characters for column names
        sanitized = name.replace(' ', '_').replace('-', '_').replace('.', '_')
        sanitized = ''.join(c if c.isalnum() or c == '_' else '_' for c in sanitized)
        # Remove leading/trailing underscores and limit length
        sanitized = sanitized.strip('_')[:50]
        return sanitized if sanitized else 'file'
    
    def _normalize_join_key_for_string_comparison(self, series: pd.Series) -> pd.Series:
        """Normalize join key values to ensure consistent string comparison.
        
        Handles cases where int64 and float64 values need to match:
        - Converts numeric values to int (if possible) to remove .0 suffix
        - Then converts to string and strips whitespace
        - Handles NaN values appropriately
        """
        try:
            # Try to convert to numeric first
            numeric_series = pd.to_numeric(series, errors='coerce')
            
            # Convert to string, then remove trailing .0 for whole numbers
            # This handles both int64 and float64 cases
            result = numeric_series.astype(str)
            # Remove .0 suffix for whole numbers (e.g., "1062617.0" -> "1062617")
            result = result.str.replace(r'\.0$', '', regex=True)
            # Handle NaN values (they become "nan" string)
            result = result.replace('nan', None)
            # Strip whitespace
            result = result.str.strip() if hasattr(result, 'str') else result
            
            return result
        except (ValueError, TypeError):
            # If conversion fails, just convert to string and strip
            return series.astype(str).str.strip()
    
    def _remove_unnamed_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
        if unnamed_cols:
            df = df.drop(columns=unnamed_cols)
        return df
    
    def _add_join_keys_status(self, df: pd.DataFrame, left_keys: List[str], right_keys: List[str], 
                              left_suffix: str, right_suffix: str) -> pd.DataFrame:
        # Create a combined join status column
        df['Join_status'] = 'matched'
        
        # Check for any suffixed columns to determine status
        file1_cols = [col for col in df.columns if col.endswith(left_suffix)]
        file2_cols = [col for col in df.columns if col.endswith(right_suffix)]
        
        if file1_cols and file2_cols:
            # Use the first available suffixed column to determine status
            file1_col = file1_cols[0]
            file2_col = file2_cols[0]
            
            # Set status based on which file has data
            df.loc[df[file1_col].isna(), 'Join_status'] = 'only_in_file2'
            df.loc[df[file2_col].isna(), 'Join_status'] = 'only_in_file1'
            
            # For rows where both files have data, check if values match
            both_present = df[file1_col].notna() & df[file2_col].notna()
            if both_present.any():
                # Check if all join key values match
                all_match = True
                for left_key, right_key in zip(left_keys, right_keys):
                    left_key_col = f"{left_key}{left_suffix}"
                    right_key_col = f"{right_key}{right_suffix}"
                    if left_key_col in df.columns and right_key_col in df.columns:
                        if not (df.loc[both_present, left_key_col] == df.loc[both_present, right_key_col]).all():
                            all_match = False
                            break
                
                if not all_match:
                    df.loc[both_present, 'Join_status'] = 'key_mismatch'
        
        return df


class JoinResultValidator(IJoinResultValidator):
    
    def validate_join_result(self, joined_df: pd.DataFrame, df1: pd.DataFrame, df2: pd.DataFrame) -> None:
        if joined_df is None:
            raise DataJoiningError("Join result is None")
        
        if joined_df.empty:
            print("⚠️  Warning: Join result is empty")
        
        original_rows = len(df1) + len(df2)
        joined_rows = len(joined_df)
        
        if joined_rows > original_rows:
            print(f"⚠️  Warning: Join result has more rows ({joined_rows}) than input dataframes combined ({original_rows})")
        
        print(f"✓ Join validation completed. Result: {joined_df.shape[0]} rows × {joined_df.shape[1]} columns")


class DataJoiner(IDataJoiner):
    
    def __init__(self):
        self._key_extractor = JoinKeyExtractor()
        self._key_validator = JoinKeyValidator()
        self._join_executor = JoinExecutor()
        self._result_validator = JoinResultValidator()
    
    def join_dataframes(self, df1: pd.DataFrame, df2: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        self._ensure_dataframes_valid(df1, df2)
        
        left_keys, right_keys = self._key_extractor.extract_join_keys(config)
        
        if not left_keys or not right_keys:
            raise InvalidConfigurationError("No valid join keys found in configuration")
        
        self._key_validator.validate_join_keys(df1, df2, left_keys, right_keys)
        
        joined_df = self._join_executor.execute_join(df1, df2, left_keys, right_keys, config)
        
        self._result_validator.validate_join_result(joined_df, df1, df2)
        
        return joined_df
    
    def _ensure_dataframes_valid(self, df1: pd.DataFrame, df2: pd.DataFrame) -> None:
        if df1 is None or df2 is None:
            raise DataJoiningError("One or both input dataframes are None")
        
        if df1.empty or df2.empty:
            print("⚠️  Warning: One or both input dataframes are empty") 