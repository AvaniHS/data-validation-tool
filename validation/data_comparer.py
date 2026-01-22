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
from services.logging import get_logger


class StringComparisonStrategy(IComparisonStrategy):
    def compare(self, value1: Any, value2: Any) -> Tuple[str, Optional[float], Optional[float]]:
        is_blank1 = self._is_blank(value1)
        is_blank2 = self._is_blank(value2)
        
        if is_blank1 and is_blank2:
            return "no match", 100.0, 100.0
        
        if is_blank1 or is_blank2:
            return "no match", 100.0, 100.0
        
        if pd.isna(value1) and pd.isna(value2):
            return "no match", 100.0, 100.0
        
        if pd.isna(value1) or pd.isna(value2):
            return "no match", 100.0, 100.0
        
        normalized_value1 = self._normalize_string(value1)
        normalized_value2 = self._normalize_string(value2)
        
        if normalized_value1 == normalized_value2:
            return "match", 0.0, 0.0
        else:
            return "no match", 100.0, 100.0
    
    def _is_blank(self, value: Any) -> bool:
        if pd.isna(value):
            return True
        if value is None:
            return True
        value_str = str(value).strip()
        if len(value_str) == 0:
            return True
        import re
        value_str = value_str.replace('_x000D_', '')
        value_str = re.sub(r'[\r\n\t\s]+', '', value_str)
        return len(value_str) == 0
    
    def _normalize_string(self, value: Any) -> str:
        import re
        import unicodedata
        
        if pd.isna(value) or value is None:
            return ""
        
        value_str = str(value)
        
        value_str = value_str.replace('_x000D_', '')
        value_str = value_str.replace('\x00', '')
        value_str = unicodedata.normalize('NFKC', value_str)
        
        value_str = re.sub(r'[\r\n\t]+', ' ', value_str)
        value_str = re.sub(r'[\u00A0\u2000-\u200B\u202F\u205F\u3000]+', ' ', value_str)
        value_str = re.sub(r'\s+', ' ', value_str)
        value_str = value_str.strip().lower()
        
        return value_str


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
    """
    Executes comparison operations on dataframes using strategy pattern.
    """
    
    def __init__(self):
        self._logger = get_logger(self.__class__.__name__)
    
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
                    comparison_column_name = f"{file1_column}{left_suffix}_vs_{file2_column}{right_suffix}_comparison"
                    self._logger.warning(f"Column mapping {file1_column} -> {file2_column} not found in dataframe")
                    self._logger.debug(f"Expected file1 column: {actual_file1_column} (tried: {file1_suffixed_column} or {file1_column})")
                    self._logger.debug(f"Expected file2 column: {actual_file2_column} (tried: {file2_suffixed_column} or {file2_column})")
                    matching_file1 = [col for col in df.columns if file1_column.lower() in col.lower()]
                    matching_file2 = [col for col in df.columns if file2_column.lower() in col.lower()]
                    self._logger.debug(f"Available columns matching '{file1_column}': {matching_file1}")
                    self._logger.debug(f"Available columns matching '{file2_column}': {matching_file2}")
                    all_cols = list(df.columns)[:20] if len(df.columns) > 20 else list(df.columns)
                    self._logger.debug(f"All available columns: {all_cols}")
                    self._logger.warning(f"Comparison column '{comparison_column_name}' will not be created")
                    continue
                
                selected_strategy = strategy_selector.select_strategy(
                    df[actual_file1_column], df[actual_file2_column], config, file1_column, file2_column
                )
                
                comparison_results = []
                delta_results = []
                percentage_delta_results = []
                
                detailed_delta_analysis = config.get('detailed_metric_delta_analysis', '').lower() == 'yes'
                is_metric = strategy_selector.is_column_metric(config, file1_column, file2_column)
                
                for row_index in range(len(df)):
                    value_from_file1 = df.loc[row_index, actual_file1_column]
                    value_from_file2 = df.loc[row_index, actual_file2_column]
                    
                    comparison_result, delta_value, percentage_delta_value = selected_strategy.compare(value_from_file1, value_from_file2)
                    delta_results.append(delta_value)
                    percentage_delta_results.append(percentage_delta_value)
                    
                    if is_metric and not detailed_delta_analysis:
                        comparison_results.append(delta_value)
                    else:
                        comparison_results.append(comparison_result)
                
                # Include suffixes in comparison column names to show source file/sheet
                comparison_column_name = f"{file1_column}{left_suffix}_vs_{file2_column}{right_suffix}_comparison"
                result_dataframe[comparison_column_name] = comparison_results
                
                # Only create delta columns if detailed_metric_delta_analysis is set to "yes" and column is a metric
                if detailed_delta_analysis and is_metric:
                    delta_column_name = f"{file1_column}{left_suffix}_vs_{file2_column}{right_suffix}_delta"
                    percentage_delta_column_name = f"{file1_column}{left_suffix}_vs_{file2_column}{right_suffix}_delta%"
                    result_dataframe[delta_column_name] = delta_results
                    result_dataframe[percentage_delta_column_name] = percentage_delta_results
            
            return result_dataframe
            
        except (ValueError, KeyError, TypeError) as e:
            self._logger.error(f"Comparison failed due to data error: {str(e)}", exception=e)
            raise DataComparisonError(f"Failed to execute comparison: {str(e)}") from e
        except Exception as e:
            self._logger.error(f"Unexpected error during comparison: {str(e)}", exception=e)
            raise DataComparisonError(f"Unexpected error during comparison: {str(e)}") from e





class ComparisonResultValidator(IComparisonResultValidator):
    """
    Validates comparison results to ensure data integrity.
    """
    
    def __init__(self):
        self._logger = get_logger(self.__class__.__name__)
    
    def validate_result(self, result_df: pd.DataFrame, original_df: pd.DataFrame) -> None:
        """
        Validate that the comparison result is valid.
        
        Args:
            result_df: The comparison result dataframe
            original_df: The original dataframe before comparison
        
        Raises:
            DataComparisonError: If the result is invalid
        """
        if result_df is None:
            self._logger.error("Comparison result is None")
            raise DataComparisonError("Comparison result is None")
        
        if result_df.empty:
            self._logger.warning("Comparison resulted in empty dataframe")
        
        if len(result_df) != len(original_df):
            error_msg = f"Comparison result has different number of rows ({len(result_df)}) than original ({len(original_df)})"
            self._logger.error(error_msg)
            raise DataComparisonError(error_msg)


class DataComparer(IDataComparer):
    """
    Main comparer class that orchestrates comparison operations.
    """
    
    def __init__(self):
        self._dataframe_validator: IDataFrameValidator = DataFrameValidator()
        self._config_validator: IComparisonConfigValidator = ComparisonConfigValidator()
        self._config_extractor: IComparisonConfigExtractor = ComparisonConfigExtractor()
        self._strategy_selector: IComparisonStrategySelector = ComparisonStrategySelector()
        self._executor: IComparisonExecutor = ComparisonExecutor()
        self._result_validator: IComparisonResultValidator = ComparisonResultValidator()
        self._logger = get_logger(self.__class__.__name__)
    
    def compare_mapped_columns(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Compare mapped columns between two dataframes.
        
        Args:
            df: The dataframe containing both file1 and file2 columns
            config: The configuration dictionary
        
        Returns:
            Dataframe with comparison results
        
        Raises:
            DataComparisonError: If comparison fails
            InvalidConfigurationError: If configuration is invalid
        """
        try:
            self._dataframe_validator.validate_dataframe(df)
            self._config_validator.validate_configuration(config)
            column_mapping = self._config_extractor.extract_column_mapping(config)
            
            if not column_mapping:
                self._logger.info("No comparison required")
                return df
            
            self._logger.info(f"Starting comparison for {len(column_mapping)} column pairs")
            comparison_result = self._executor.execute_comparison(df, column_mapping, self._strategy_selector, config)
            self._result_validator.validate_result(comparison_result, df)
            
            self._logger.info(f"Data comparison completed successfully")
            self._logger.info(f"Original dataframe: {len(df)} rows, {len(df.columns)} columns")
            self._logger.info(f"Comparison result: {len(comparison_result)} rows, {len(comparison_result.columns)} columns")
            self._logger.info(f"Column mappings: {len(column_mapping)} pairs compared")
            
            return comparison_result
            
        except (InvalidConfigurationError, DataComparisonError):
            raise
        except Exception as e:
            self._logger.error(f"Failed to compare mapped columns: {str(e)}", exception=e)
            raise DataComparisonError(f"Failed to compare mapped columns: {str(e)}") from e
    
 