"""
Data joining module for preparing output dataframe by joining two dataframes.
Follows OOP, SOLID principles, and separation of concerns.
"""

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
    """Concrete implementation of join key extraction"""
    
    def extract_join_keys(self, config: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Extract join keys from configuration"""
        join_keys = config.get('join_keys', {})
        column_mapping = config.get('column_mapping', {})
        
        if join_keys and join_keys != DEFAULT_NA_VALUE and isinstance(join_keys, dict):
            # Use explicit join keys
            return self._extract_from_join_keys(join_keys)
        else:
            # Use column mapping as join keys
            return self._extract_from_column_mapping(column_mapping)
    
    def _extract_from_join_keys(self, join_keys: Dict[str, str]) -> Tuple[List[str], List[str]]:
        """Extract left and right join keys from join_keys dictionary"""
        left_keys = list(join_keys.keys())
        right_keys = list(join_keys.values())
        return left_keys, right_keys
    
    def _extract_from_column_mapping(self, column_mapping: Dict[str, str]) -> Tuple[List[str], List[str]]:
        """Extract join keys from column mapping"""
        left_keys = list(column_mapping.keys())
        right_keys = list(column_mapping.values())
        return left_keys, right_keys


class JoinKeyValidator(IJoinKeyValidator):
    """Concrete implementation of join key validation"""
    
    def validate_join_keys(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                          left_keys: List[str], right_keys: List[str]) -> None:
        """Validate that join keys exist in respective dataframes"""
        missing_in_df1 = [key for key in left_keys if key not in df1.columns]
        missing_in_df2 = [key for key in right_keys if key not in df2.columns]
        
        if missing_in_df1 or missing_in_df2:
            error_message = self._build_validation_error_message(
                df1, df2, missing_in_df1, missing_in_df2
            )
            raise DataJoiningError(error_message)
    
    def _build_validation_error_message(self, df1: pd.DataFrame, df2: pd.DataFrame,
                                      missing_in_df1: List[str], missing_in_df2: List[str]) -> str:
        """Build detailed error message for join key validation failures"""
        error_message = "Join keys validation failed:\n"
        
        if missing_in_df1:
            error_message += f"  Missing join keys in df1: {', '.join(missing_in_df1)}\n"
            error_message += f"  Available columns in df1: {', '.join(sorted(df1.columns))}\n"
        
        if missing_in_df2:
            error_message += f"  Missing join keys in df2: {', '.join(missing_in_df2)}\n"
            error_message += f"  Available columns in df2: {', '.join(sorted(df2.columns))}\n"
        
        return error_message


class JoinExecutor(IJoinExecutor):
    """Concrete implementation of join execution"""
    
    def execute_join(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                    left_keys: List[str], right_keys: List[str]) -> pd.DataFrame:
        """Execute full outer join on dataframes"""
        try:
            # Create suffixes for overlapping column names
            left_suffix = '_file1'
            right_suffix = '_file2'
            
            # Convert join keys to compatible data types
            df1_copy = df1.copy()
            df2_copy = df2.copy()
            
            for left_key, right_key in zip(left_keys, right_keys):
                # Convert both columns to string type for consistent joining
                df1_copy[left_key] = df1_copy[left_key].astype(str)
                df2_copy[right_key] = df2_copy[right_key].astype(str)
            
            # Perform full outer join
            joined_df = df1_copy.merge(
                df2_copy,
                left_on=left_keys,
                right_on=right_keys,
                how='outer',
                suffixes=(left_suffix, right_suffix)
            )
            
            # Remove unnamed columns
            joined_df = self._remove_unnamed_columns(joined_df)
            
            # Add JoinKeys column to show match/mismatch status
            joined_df = self._add_join_keys_status(joined_df, left_keys, right_keys)
            
            return joined_df
            
        except Exception as e:
            raise DataJoiningError(f"Failed to execute join operation: {str(e)}")
    
    def _remove_unnamed_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove unnamed columns from joined dataframe"""
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
        if unnamed_cols:
            df = df.drop(columns=unnamed_cols)
            print(f"✓ Removed {len(unnamed_cols)} unnamed columns from joined data")
        return df
    
    def _add_join_keys_status(self, df: pd.DataFrame, left_keys: List[str], right_keys: List[str]) -> pd.DataFrame:
        """Add JoinKeys column showing match/mismatch status"""
        df_copy = df.copy()
        
        # Create JoinKeys status column
        join_status = []
        for idx in range(len(df_copy)):
            # Check if all join keys match for this row
            all_match = True
            for left_key, right_key in zip(left_keys, right_keys):
                left_val = str(df_copy.loc[idx, left_key]) if pd.notna(df_copy.loc[idx, left_key]) else ''
                right_val = str(df_copy.loc[idx, right_key]) if pd.notna(df_copy.loc[idx, right_key]) else ''
                
                if left_val != right_val:
                    all_match = False
                    break
            
            if all_match:
                join_status.append("Match")
            else:
                join_status.append("Mismatch")
        
        # Insert JoinKeys column at the beginning
        df_copy.insert(0, 'JoinKeys', join_status)
        
        return df_copy


class JoinResultValidator(IJoinResultValidator):
    """Concrete implementation of join result validation"""
    
    def validate_join_result(self, joined_df: pd.DataFrame, df1: pd.DataFrame, df2: pd.DataFrame) -> None:
        """Validate the join result"""
        if joined_df is None:
            raise DataJoiningError("Join operation returned None")
        
        if joined_df.empty:
            print("⚠️  Warning: Join operation resulted in empty dataframe")
        
        # Check if join preserved expected data
        expected_min_rows = max(len(df1), len(df2))
        if len(joined_df) < expected_min_rows:
            print(f"⚠️  Warning: Join result has fewer rows ({len(joined_df)}) than expected minimum ({expected_min_rows})")


class DataJoiner(IDataJoiner):
    """Concrete implementation of data joining"""
    
    def __init__(self):
        self._key_extractor = JoinKeyExtractor()
        self._key_validator = JoinKeyValidator()
        self._join_executor = JoinExecutor()
        self._result_validator = JoinResultValidator()
    
    def join_dataframes(self, df1: pd.DataFrame, df2: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Join two dataframes using join keys or column mapping
        
        Args:
            df1: First dataframe
            df2: Second dataframe
            config: Configuration dictionary containing join keys and column mapping
            
        Returns:
            Joined dataframe with full outer join
            
        Raises:
            DataJoiningError: If joining fails
            InvalidConfigurationError: If configuration is invalid
        """
        try:
            self._ensure_dataframes_valid(df1, df2)
            
            # Extract join keys from configuration
            left_keys, right_keys = self._key_extractor.extract_join_keys(config)
            
            # Validate join keys exist in dataframes
            self._key_validator.validate_join_keys(df1, df2, left_keys, right_keys)
            
            # Execute join operation
            joined_df = self._join_executor.execute_join(df1, df2, left_keys, right_keys)
            
            # Validate join result
            self._result_validator.validate_join_result(joined_df, df1, df2)
            
            print(f"✓ Data joining completed successfully")
            print(f"  Original df1: {len(df1)} rows")
            print(f"  Original df2: {len(df2)} rows")
            print(f"  Joined result: {len(joined_df)} rows, {len(joined_df.columns)} columns")
            print(f"  Join keys used: {dict(zip(left_keys, right_keys))}")
            
            return joined_df
            
        except (InvalidConfigurationError, DataJoiningError):
            raise
        except Exception as e:
            raise DataJoiningError(f"Failed to join dataframes: {str(e)}")
    
    def _ensure_dataframes_valid(self, df1: pd.DataFrame, df2: pd.DataFrame) -> None:
        if df1 is None or df2 is None:
            raise DataJoiningError("Input dataframes cannot be None")
        
        if df1.empty and df2.empty:
            raise DataJoiningError("Both input dataframes are empty")
        
        if len(df1.columns) == 0 or len(df2.columns) == 0:
            raise DataJoiningError("Input dataframes must have at least one column") 