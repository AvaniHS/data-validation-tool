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
                    left_keys: List[str], right_keys: List[str]) -> pd.DataFrame:
        try:
            left_suffix = '_file1'
            right_suffix = '_file2'
            
            df1_copy = df1.copy()
            df2_copy = df2.copy()
            
            # Rename join keys to force suffixed columns
            for left_key, right_key in zip(left_keys, right_keys):
                df1_copy = df1_copy.rename(columns={left_key: f"{left_key}{left_suffix}"})
                df2_copy = df2_copy.rename(columns={right_key: f"{right_key}{right_suffix}"})
                
                # Convert to string for consistent joining
                df1_copy[f"{left_key}{left_suffix}"] = df1_copy[f"{left_key}{left_suffix}"].astype(str)
                df2_copy[f"{right_key}{right_suffix}"] = df2_copy[f"{right_key}{right_suffix}"].astype(str)
            
            # Create new key lists with suffixed names
            left_keys_suffixed = [f"{key}{left_suffix}" for key in left_keys]
            right_keys_suffixed = [f"{key}{right_suffix}" for key in right_keys]
            
            joined_df = df1_copy.merge(
                df2_copy,
                left_on=left_keys_suffixed,
                right_on=right_keys_suffixed,
                how='outer',
                suffixes=(left_suffix, right_suffix)
            )
            
            joined_df = self._remove_unnamed_columns(joined_df)
            joined_df = self._add_join_keys_status(joined_df, left_keys, right_keys)
            
            return joined_df
            
        except Exception as e:
            raise DataJoiningError(f"Failed to execute join: {str(e)}")
    
    def _remove_unnamed_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
        if unnamed_cols:
            df = df.drop(columns=unnamed_cols)
        return df
    
    def _add_join_keys_status(self, df: pd.DataFrame, left_keys: List[str], right_keys: List[str]) -> pd.DataFrame:
        # Create a combined join status column
        df['Join_status'] = 'matched'
        
        # Check for any suffixed columns to determine status
        file1_cols = [col for col in df.columns if col.endswith('_file1')]
        file2_cols = [col for col in df.columns if col.endswith('_file2')]
        
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
                    left_key_col = f"{left_key}_file1"
                    right_key_col = f"{right_key}_file2"
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
        
        joined_df = self._join_executor.execute_join(df1, df2, left_keys, right_keys)
        
        self._result_validator.validate_join_result(joined_df, df1, df2)
        
        return joined_df
    
    def _ensure_dataframes_valid(self, df1: pd.DataFrame, df2: pd.DataFrame) -> None:
        if df1 is None or df2 is None:
            raise DataJoiningError("One or both input dataframes are None")
        
        if df1.empty or df2.empty:
            print("⚠️  Warning: One or both input dataframes are empty") 