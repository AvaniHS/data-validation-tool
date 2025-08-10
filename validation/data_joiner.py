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
        
        if join_keys and join_keys != DEFAULT_NA_VALUE and isinstance(join_keys, dict):
            return self._extract_from_join_keys(join_keys)
        else:
            return self._extract_from_column_mapping(column_mapping)
    
    def _extract_from_join_keys(self, join_keys: Dict[str, str]) -> Tuple[List[str], List[str]]:
        left_keys = list(join_keys.keys())
        right_keys = list(join_keys.values())
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
            
            for left_key, right_key in zip(left_keys, right_keys):
                df1_copy[left_key] = df1_copy[left_key].astype(str)
                df2_copy[right_key] = df2_copy[right_key].astype(str)
            
            joined_df = df1_copy.merge(
                df2_copy,
                left_on=left_keys,
                right_on=right_keys,
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
        for left_key, right_key in zip(left_keys, right_keys):
            status_col = f"{left_key}_join_status"
            df[status_col] = 'matched'
            
            left_key_file1 = f"{left_key}_file1"
            right_key_file2 = f"{right_key}_file2"
            
            if left_key_file1 in df.columns and right_key_file2 in df.columns:
                df.loc[df[left_key_file1].isna(), status_col] = 'only_in_file2'
                df.loc[df[right_key_file2].isna(), status_col] = 'only_in_file1'
        
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