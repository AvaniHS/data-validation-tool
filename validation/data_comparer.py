from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np
from validation.exceptions import DataComparisonError, InvalidConfigurationError
from validation.contracts import IDataComparer
from validation.interfaces.comparison_strategies import (
    IComparisonStrategy,
    INumericComparisonStrategy,
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
    def compare(self, value1: Any, value2: Any) -> Tuple[str, Optional[float], Optional[float]]:
        if pd.isna(value1) and pd.isna(value2):
            return "match", 0.0, 0.0
        if pd.isna(value1) or pd.isna(value2):
            return "no match", 100.0, 100.0
        
        normalized_value1 = str(value1).strip().lower()
        normalized_value2 = str(value2).strip().lower()
        
        if normalized_value1 == normalized_value2:
            return "match", 0.0, 0.0
        else:
            return "no match", 100.0, 100.0


class NumericComparisonStrategy(INumericComparisonStrategy):
    def compare(self, value1: Any, value2: Any) -> Tuple[str, Optional[float], Optional[float]]:
        if pd.isna(value1) and pd.isna(value2):
            return "0.0", 0.0, 0.0
        if pd.isna(value1):
            try:
                numeric_value2 = float(value2)
                return "null", numeric_value2, 100.0
            except (ValueError, TypeError):
                return "null", 0.0, 100.0
        if pd.isna(value2):
            try:
                numeric_value1 = float(value1)
                return "null", numeric_value1, 100.0
            except (ValueError, TypeError):
                return "null", 0.0, 100.0
        
        try:
            numeric_value1 = float(value1)
            numeric_value2 = float(value2)
            
            absolute_difference = numeric_value1 - numeric_value2
            
            if numeric_value1 != 0:
                percentage_difference = (absolute_difference / numeric_value1) * 100
            else:
                percentage_difference = float('inf') if absolute_difference != 0 else 0.0
            
            return str(absolute_difference), absolute_difference, percentage_difference
                
        except (ValueError, TypeError):
            return "null", 100.0, 100.0





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
    
    def select_strategy(self, series1: pd.Series, series2: pd.Series, config: Dict[str, Any], file1_col: str, file2_col: str = None) -> IComparisonStrategy:
        comparison_types = config.get('comparison_types', {})
        if comparison_types and file1_col in comparison_types:
            strategy_type = comparison_types[file1_col]
            if strategy_type in self._available_strategies:
                return self._available_strategies[strategy_type]
        
        if self._is_join_key(config, file1_col, file2_col):
            return self._available_strategies['string']
        
        is_metric = self.is_column_metric(config, file1_col, file2_col)
        if is_metric:
            return self._available_strategies['numeric']
        
        if self._is_numeric_series(series1) and self._is_numeric_series(series2):
            return self._available_strategies['numeric']
        else:
            return self._available_strategies['string']
    
    def _is_join_key(self, config: Dict[str, Any], file1_col: str, file2_col: str = None) -> bool:
        from constants import DEFAULT_NA_VALUE
        join_keys = config.get('join_keys', {})
        
        if not join_keys or join_keys == DEFAULT_NA_VALUE:
            return False
        
        if not isinstance(join_keys, dict):
            return False
        
        if file1_col in join_keys:
            return True
        
        if file2_col and file2_col in join_keys.values():
            return True
        
        return False
    
    def is_column_metric(self, config: Dict[str, Any], file1_col: str, file2_col: str = None) -> bool:
        if self._is_join_key(config, file1_col, file2_col):
            return False
        
        file1_metrics = config.get('file1_metric_list', [])
        file2_metrics = config.get('file2_metric_list', [])
        
        if not isinstance(file1_metrics, list):
            file1_metrics = []
        if not isinstance(file2_metrics, list):
            file2_metrics = []
        
        if file1_col in file1_metrics:
            return True
        
        if file2_col and file2_col in file2_metrics:
            return True
        
        return False
    
    def _extract_metrics_from_config(self, config: Dict[str, Any]) -> List[str]:
        file1_metrics = config.get('file1_metric_list', [])
        file2_metrics = config.get('file2_metric_list', [])
        
        if not isinstance(file1_metrics, list):
            file1_metrics = []
        if not isinstance(file2_metrics, list):
            file2_metrics = []
        
        return file1_metrics + file2_metrics
    
    def _is_numeric_series(self, series: pd.Series) -> bool:
        try:
            pd.to_numeric(series, errors='raise')
            return True
        except (ValueError, TypeError):
            return False





class ComparisonExecutor(IComparisonExecutor):
    def _get_column_suffixes(self, df: pd.DataFrame, config: Dict[str, Any]) -> Tuple[str, str]:
        """Get column suffixes from dataframe attrs or generate from config."""
        # Try to get from dataframe attributes first
        if hasattr(df, 'attrs') and 'left_suffix' in df.attrs and 'right_suffix' in df.attrs:
            return df.attrs['left_suffix'], df.attrs['right_suffix']
        
        # Fall back to generating from config
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
        
        # Default fallback
        return '_file1', '_file2'
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize file/sheet name for use as column suffix."""
        if not name:
            return 'file'
        sanitized = name.replace(' ', '_').replace('-', '_').replace('.', '_')
        sanitized = ''.join(c if c.isalnum() or c == '_' else '_' for c in sanitized)
        sanitized = sanitized.strip('_')[:50]
        return sanitized if sanitized else 'file'
    
    def execute_comparison(self, df: pd.DataFrame, column_mapping: Dict[str, str], 
                          strategy_selector: IComparisonStrategySelector, config: Dict[str, Any]) -> pd.DataFrame:
        try:
            result_dataframe = df.copy()
            
            # Get suffixes from dataframe attrs or generate from config
            left_suffix, right_suffix = self._get_column_suffixes(df, config)
            
            for file1_column, file2_column in column_mapping.items():
                file1_suffixed_column = f"{file1_column}{left_suffix}"
                file2_suffixed_column = f"{file2_column}{right_suffix}"
                
                actual_file1_column = file1_suffixed_column if file1_suffixed_column in df.columns else file1_column
                actual_file2_column = file2_suffixed_column if file2_suffixed_column in df.columns else file2_column
                
                if actual_file1_column not in df.columns or actual_file2_column not in df.columns:
                    print(f"⚠️  Warning: Column mapping {file1_column} -> {file2_column} not found in dataframe")
                    print(f"  Looking for: {actual_file1_column}, {actual_file2_column}")
                    print(f"  Available columns: {list(df.columns)}")
                    continue
                
                selected_strategy = strategy_selector.select_strategy(
                    df[actual_file1_column], df[actual_file2_column], config, file1_column, file2_column
                )
                
                comparison_results = []
                delta_results = []
                percentage_delta_results = []
                
                for row_index in range(len(df)):
                    value_from_file1 = df.loc[row_index, actual_file1_column]
                    value_from_file2 = df.loc[row_index, actual_file2_column]
                    
                    comparison_result, delta_value, percentage_delta_value = selected_strategy.compare(value_from_file1, value_from_file2)
                    delta_results.append(delta_value)
                    percentage_delta_results.append(percentage_delta_value)
                    
                    comparison_results.append(comparison_result)
                
                # Include suffixes in comparison column names to show source file/sheet
                comparison_column_name = f"{file1_column}{left_suffix}_vs_{file2_column}{right_suffix}_comparison"
                result_dataframe[comparison_column_name] = comparison_results
                
                # Only create delta columns if detailed_metric_delta_analysis is set to "yes" and column is a metric
                detailed_delta_analysis = config.get('detailed_metric_delta_analysis', '').lower() == 'yes'
                is_metric = strategy_selector.is_column_metric(config, file1_column, file2_column)
                
                if detailed_delta_analysis and is_metric:
                    delta_column_name = f"{file1_column}{left_suffix}_vs_{file2_column}{right_suffix}_delta"
                    percentage_delta_column_name = f"{file1_column}{left_suffix}_vs_{file2_column}{right_suffix}_delta%"
                    result_dataframe[delta_column_name] = delta_results
                    result_dataframe[percentage_delta_column_name] = percentage_delta_results
            
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
    
 