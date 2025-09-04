from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np
from validation.exceptions import DataComparisonError, InvalidConfigurationError
from validation.contracts import IDataComparer
from validation.interfaces.comparison_strategies import (
    IComparisonStrategy,
    IComparisonConfigValidator,
    IComparisonConfigExtractor,
    IComparisonStrategySelector,
    IComparisonExecutor,
    IComparisonResultValidator
)
from validation.interfaces.dataframe_validator import IDataFrameValidator
from validation.validators import DataFrameValidator
from constants import DEFAULT_NA_VALUE


class StringComparisonStrategy(IComparisonStrategy):
    def compare(self, value1: Any, value2: Any) -> Tuple[str, Optional[float]]:
        if pd.isna(value1) and pd.isna(value2):
            return "match", 0.0
        if pd.isna(value1) or pd.isna(value2):
            return "no match", 100.0
        
        normalized_value1 = str(value1).strip().lower()
        normalized_value2 = str(value2).strip().lower()
        
        if normalized_value1 == normalized_value2:
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
            numeric_value1 = float(value1)
            numeric_value2 = float(value2)
            
            absolute_difference = numeric_value1 - numeric_value2
            
            if numeric_value1 != 0:
                percentage_difference = (absolute_difference / numeric_value1) * 100
            else:
                percentage_difference = float('inf') if absolute_difference != 0 else 0.0
            
            return str(absolute_difference), percentage_difference
                
        except (ValueError, TypeError):
            return "null", 100.0





class ComparisonConfigValidator(IComparisonConfigValidator):
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        column_mapping = config.get('column_mapping', {})
        
        if not column_mapping or column_mapping == DEFAULT_NA_VALUE:
            raise InvalidConfigurationError("Column mapping is required for comparison")
        
        if not isinstance(column_mapping, dict):
            raise InvalidConfigurationError("Column mapping must be a dictionary")
        
        if len(column_mapping) == 0:
            raise InvalidConfigurationError("Column mapping cannot be empty")





class ComparisonConfigExtractor(IComparisonConfigExtractor):
    def extract_column_mapping(self, config: Dict[str, Any]) -> Dict[str, str]:
        column_mapping = config.get('column_mapping', {})
        
        if not column_mapping or column_mapping == DEFAULT_NA_VALUE:
            return {}
        
        return column_mapping.copy()





class ComparisonStrategySelector(IComparisonStrategySelector):
    def __init__(self):
        self._available_strategies = {
            'string': StringComparisonStrategy(),
            'numeric': NumericComparisonStrategy()
        }
    
    def select_strategy(self, series1: pd.Series, series2: pd.Series, config: Dict[str, Any], file1_col: str) -> IComparisonStrategy:
        comparison_types = config.get('comparison_types', {})
        if comparison_types and file1_col in comparison_types:
            strategy_type = comparison_types[file1_col]
            if strategy_type in self._available_strategies:
                return self._available_strategies[strategy_type]
        
        metrics = config.get('metrics', [])
        if file1_col in metrics and self._is_numeric_series(series1) and self._is_numeric_series(series2):
            return self._available_strategies['numeric']
        else:
            return self._available_strategies['string']
    
    def _is_numeric_series(self, series: pd.Series) -> bool:
        try:
            pd.to_numeric(series, errors='raise')
            return True
        except (ValueError, TypeError):
            return False





class ComparisonExecutor(IComparisonExecutor):
    def execute_comparison(self, df: pd.DataFrame, column_mapping: Dict[str, str], 
                          strategy_selector: IComparisonStrategySelector, config: Dict[str, Any]) -> pd.DataFrame:
        try:
            result_dataframe = df.copy()
            
            for file1_column, file2_column in column_mapping.items():
                file1_suffixed_column = f"{file1_column}_file1"
                file2_suffixed_column = f"{file2_column}_file2"
                
                actual_file1_column = file1_suffixed_column if file1_suffixed_column in df.columns else file1_column
                actual_file2_column = file2_suffixed_column if file2_suffixed_column in df.columns else file2_column
                
                if actual_file1_column not in df.columns or actual_file2_column not in df.columns:
                    print(f"⚠️  Warning: Column mapping {file1_column} -> {file2_column} not found in dataframe")
                    print(f"  Looking for: {actual_file1_column}, {actual_file2_column}")
                    print(f"  Available columns: {list(df.columns)}")
                    continue
                
                selected_strategy = strategy_selector.select_strategy(
                    df[actual_file1_column], df[actual_file2_column], config, file1_column
                )
                
                comparison_results = []
                delta_results = []
                
                for row_index in range(len(df)):
                    value_from_file1 = df.loc[row_index, actual_file1_column]
                    value_from_file2 = df.loc[row_index, actual_file2_column]
                    
                    comparison_result, delta_value = selected_strategy.compare(value_from_file1, value_from_file2)
                    comparison_results.append(comparison_result)
                    delta_results.append(delta_value)
                
                comparison_column_name = f"{file1_column}_vs_{file2_column}_comparison"
                result_dataframe[comparison_column_name] = comparison_results
                
                if isinstance(selected_strategy, NumericComparisonStrategy):
                    delta_column_name = f"{file1_column}_vs_{file2_column}_delta"
                    result_dataframe[delta_column_name] = delta_results
            
            return result_dataframe
            
        except Exception as e:
            raise DataComparisonError(f"Failed to execute comparison: {str(e)}")





class ComparisonResultValidator(IComparisonResultValidator):
    def validate_result(self, result_df: pd.DataFrame, original_df: pd.DataFrame) -> None:
        if result_df is None:
            raise DataComparisonError("Comparison result is None")
        
        if result_df.empty:
            print("⚠️  Warning: Comparison resulted in empty dataframe")
        
        if len(result_df) != len(original_df):
            raise DataComparisonError(f"Comparison result has different number of rows ({len(result_df)}) than original ({len(original_df)})")


class DataComparer(IDataComparer):
    def __init__(self):
        self._dataframe_validator: IDataFrameValidator = DataFrameValidator()
        self._config_validator: IComparisonConfigValidator = ComparisonConfigValidator()
        self._config_extractor: IComparisonConfigExtractor = ComparisonConfigExtractor()
        self._strategy_selector: IComparisonStrategySelector = ComparisonStrategySelector()
        self._executor: IComparisonExecutor = ComparisonExecutor()
        self._result_validator: IComparisonResultValidator = ComparisonResultValidator()
    
    def compare_mapped_columns(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        try:
            self._dataframe_validator.validate_dataframe(df)
            self._config_validator.validate_configuration(config)
            column_mapping = self._config_extractor.extract_column_mapping(config)
            
            if not column_mapping:
                print("✓ No comparison required")
                return df
            
            comparison_result = self._executor.execute_comparison(df, column_mapping, self._strategy_selector, config)
            self._result_validator.validate_result(comparison_result, df)
            
            print(f"✓ Data comparison completed successfully")
            print(f"  Original dataframe: {len(df)} rows, {len(df.columns)} columns")
            print(f"  Comparison result: {len(comparison_result)} rows, {len(comparison_result.columns)} columns")
            print(f"  Column mappings: {len(column_mapping)} pairs compared")
            
            return comparison_result
            
        except (InvalidConfigurationError, DataComparisonError):
            raise
        except Exception as e:
            raise DataComparisonError(f"Failed to compare mapped columns: {str(e)}")
    
 