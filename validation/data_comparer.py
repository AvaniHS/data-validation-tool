from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np
from validation.exceptions import DataComparisonError, InvalidConfigurationError
from validation.contracts import (
    IComparisonStrategy,
    IDataComparer
)
from constants import DEFAULT_NA_VALUE


class StringComparisonStrategy(IComparisonStrategy):
    def compare(self, value1: Any, value2: Any) -> Tuple[str, Optional[float]]:
        if pd.isna(value1) and pd.isna(value2):
            return "match", 0.0
        if pd.isna(value1) or pd.isna(value2):
            return "no match", 100.0
        
        str1 = str(value1).strip().lower()
        str2 = str(value2).strip().lower()
        
        if str1 == str2:
            return "match", 0.0
        else:
            return "no match", 100.0


class NumericComparisonStrategy(IComparisonStrategy):
    def compare(self, value1: Any, value2: Any) -> Tuple[str, Optional[float]]:
        if pd.isna(value1) and pd.isna(value2):
            return "0.0", 0.0
        if pd.isna(value1):
            return "null", 100.0
        if pd.isna(value2):
            return "null", 100.0
        
        try:
            num1 = float(value1)
            num2 = float(value2)
            
            difference = num1 - num2
            
            if num1 != 0:
                delta_percentage = (difference / num1) * 100
            else:
                delta_percentage = float('inf') if difference != 0 else 0.0
            
            return str(difference), delta_percentage
                
        except (ValueError, TypeError):
            return "null", 100.0


class IComparisonConfigValidator(ABC):
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        pass


class ComparisonConfigValidator(IComparisonConfigValidator):
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        column_mapping = config.get('column_mapping', {})
        
        if not column_mapping or column_mapping == DEFAULT_NA_VALUE:
            raise InvalidConfigurationError("Column mapping is required for comparison")
        
        if not isinstance(column_mapping, dict):
            raise InvalidConfigurationError("Column mapping must be a dictionary")
        
        if len(column_mapping) == 0:
            raise InvalidConfigurationError("Column mapping cannot be empty")


class IComparisonConfigExtractor(ABC):
    @abstractmethod
    def extract_column_mapping(self, config: Dict[str, Any]) -> Dict[str, str]:
        pass


class ComparisonConfigExtractor(IComparisonConfigExtractor):
    def extract_column_mapping(self, config: Dict[str, Any]) -> Dict[str, str]:
        column_mapping = config.get('column_mapping', {})
        
        if not column_mapping or column_mapping == DEFAULT_NA_VALUE:
            return {}
        
        return column_mapping.copy()


class IComparisonStrategySelector(ABC):
    @abstractmethod
    def select_strategy(self, series1: pd.Series, series2: pd.Series, config: Dict[str, Any], file1_col: str) -> IComparisonStrategy:
        pass


class ComparisonStrategySelector(IComparisonStrategySelector):
    def __init__(self):
        self._strategies = {
            'string': StringComparisonStrategy(),
            'numeric': NumericComparisonStrategy()
        }
    
    def select_strategy(self, series1: pd.Series, series2: pd.Series, config: Dict[str, Any], file1_col: str) -> IComparisonStrategy:
        comparison_types = config.get('comparison_types', {})
        if comparison_types and file1_col in comparison_types:
            strategy_type = comparison_types[file1_col]
            if strategy_type in self._strategies:
                return self._strategies[strategy_type]
        
        if self._is_numeric_series(series1) and self._is_numeric_series(series2):
            return self._strategies['numeric']
        else:
            return self._strategies['string']
    
    def _is_numeric_series(self, series: pd.Series) -> bool:
        try:
            pd.to_numeric(series, errors='raise')
            return True
        except (ValueError, TypeError):
            return False


class IComparisonExecutor(ABC):
    @abstractmethod
    def execute_comparison(self, df: pd.DataFrame, column_mapping: Dict[str, str], 
                          strategy_selector: IComparisonStrategySelector, config: Dict[str, Any]) -> pd.DataFrame:
        pass


class ComparisonExecutor(IComparisonExecutor):
    def execute_comparison(self, df: pd.DataFrame, column_mapping: Dict[str, str], 
                          strategy_selector: IComparisonStrategySelector, config: Dict[str, Any]) -> pd.DataFrame:
        try:
            result_df = df.copy()
            
            for file1_col, file2_col in column_mapping.items():
                file1_col_suffixed = f"{file1_col}_file1"
                file2_col_suffixed = f"{file2_col}_file2"
                
                actual_file1_col = file1_col_suffixed if file1_col_suffixed in df.columns else file1_col
                actual_file2_col = file2_col_suffixed if file2_col_suffixed in df.columns else file2_col
                
                if actual_file1_col not in df.columns or actual_file2_col not in df.columns:
                    print(f"⚠️  Warning: Column mapping {file1_col} -> {file2_col} not found in dataframe")
                    print(f"  Looking for: {actual_file1_col}, {actual_file2_col}")
                    print(f"  Available columns: {list(df.columns)}")
                    continue
                
                strategy = strategy_selector.select_strategy(
                    df[actual_file1_col], df[actual_file2_col], config, file1_col
                )
                
                comparison_results = []
                delta_results = []
                
                for idx in range(len(df)):
                    value1 = df.loc[idx, actual_file1_col]
                    value2 = df.loc[idx, actual_file2_col]
                    
                    comparison_result, delta = strategy.compare(value1, value2)
                    comparison_results.append(comparison_result)
                    delta_results.append(delta)
                
                comparison_col = f"{file1_col}_vs_{file2_col}_comparison"
                delta_col = f"{file1_col}_vs_{file2_col}_delta"
                
                result_df[comparison_col] = comparison_results
                result_df[delta_col] = delta_results
            
            return result_df
            
        except Exception as e:
            raise DataComparisonError(f"Failed to execute comparison: {str(e)}")


class IComparisonResultValidator(ABC):
    @abstractmethod
    def validate_result(self, result_df: pd.DataFrame, original_df: pd.DataFrame) -> None:
        pass


class ComparisonResultValidator(IComparisonResultValidator):
    def validate_result(self, result_df: pd.DataFrame, original_df: pd.DataFrame) -> None:
        if result_df is None:
            raise DataComparisonError("Comparison result is None")
        
        if result_df.empty:
            print("⚠️  Warning: Comparison resulted in empty dataframe")
        
        # Check if comparison preserved original data
        if len(result_df) != len(original_df):
            raise DataComparisonError(f"Comparison result has different number of rows ({len(result_df)}) than original ({len(original_df)})")


class DataComparer(IDataComparer):
    def __init__(self):
        self._config_validator = ComparisonConfigValidator()
        self._config_extractor = ComparisonConfigExtractor()
        self._strategy_selector = ComparisonStrategySelector()
        self._executor = ComparisonExecutor()
        self._result_validator = ComparisonResultValidator()
    
    def compare_mapped_columns(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        try:
            self._ensure_dataframe_valid(df)
            self._config_validator.validate_configuration(config)
            column_mapping = self._config_extractor.extract_column_mapping(config)
            
            if not column_mapping:
                print("✓ No comparison required")
                return df
            
            result_df = self._executor.execute_comparison(df, column_mapping, self._strategy_selector, config)
            self._result_validator.validate_result(result_df, df)
            
            print(f"✓ Data comparison completed successfully")
            print(f"  Original dataframe: {len(df)} rows, {len(df.columns)} columns")
            print(f"  Comparison result: {len(result_df)} rows, {len(result_df.columns)} columns")
            print(f"  Column mappings: {len(column_mapping)} pairs compared")
            
            return result_df
            
        except (InvalidConfigurationError, DataComparisonError):
            raise
        except Exception as e:
            raise DataComparisonError(f"Failed to compare mapped columns: {str(e)}")
    
    def _ensure_dataframe_valid(self, df: pd.DataFrame) -> None:
        if df is None:
            raise DataComparisonError("Input dataframe cannot be None")
        
        if df.empty:
            raise DataComparisonError("Input dataframe is empty")
        
        if len(df.columns) == 0:
            raise DataComparisonError("Input dataframe has no columns") 