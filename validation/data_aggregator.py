from typing import Dict, Any, List, Optional, Union
import pandas as pd
from validation.exceptions import DataAggregationError, InvalidConfigurationError
from validation.contracts import (
    IAggregationStrategy,
    IAggregationConfigValidator,
    IAggregationConfigExtractor,
    IAggregationExecutor,
    IAggregationResultValidator,
    IAggregator
)
from constants import (
    VALID_AGGREGATION_TYPES, AGGREGATION_SUM, AGGREGATION_AVG, AGGREGATION_COUNT,
    AGGREGATION_MIN, AGGREGATION_MAX, DEFAULT_NA_VALUE
)


class SumAggregationStrategy(IAggregationStrategy):
    
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        if not columns:
            return pd.Series()
        return df[columns].sum()


class AvgAggregationStrategy(IAggregationStrategy):
    
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        if not columns:
            return pd.Series()
        return df[columns].mean()


class CountAggregationStrategy(IAggregationStrategy):
    
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        if not columns:
            return pd.Series()
        return df[columns].count()


class MinAggregationStrategy(IAggregationStrategy):
    
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        if not columns:
            return pd.Series()
        return df[columns].min()


class MaxAggregationStrategy(IAggregationStrategy):
    
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        if not columns:
            return pd.Series()
        return df[columns].max()


class AggregationConfigValidator(IAggregationConfigValidator):
    
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        aggregation_config = config.get('aggregation', {})
        
        if not aggregation_config or aggregation_config == DEFAULT_NA_VALUE:
            return
        
        if not isinstance(aggregation_config, dict):
            raise InvalidConfigurationError("Aggregation configuration must be a dictionary")
        
        for agg_type, columns in aggregation_config.items():
            if agg_type not in VALID_AGGREGATION_TYPES:
                raise InvalidConfigurationError(f"Invalid aggregation type: {agg_type}. Valid types: {VALID_AGGREGATION_TYPES}")
            
            if not isinstance(columns, list):
                raise InvalidConfigurationError(f"Aggregation columns for '{agg_type}' must be a list")


class AggregationConfigExtractor(IAggregationConfigExtractor):
    
    def extract_groupby_columns(self, df: pd.DataFrame, config: Dict[str, Any]) -> List[str]:
        aggregation_config = config.get('aggregation', {})
        
        if not aggregation_config or aggregation_config == DEFAULT_NA_VALUE:
            return []
        
        if isinstance(aggregation_config, dict) and 'groupby_columns' in aggregation_config:
            groupby_cols = aggregation_config['groupby_columns']
            if groupby_cols != DEFAULT_NA_VALUE and isinstance(groupby_cols, list):
                return [col for col in groupby_cols if col in df.columns]
        
        return []
    
    def extract_aggregation_columns(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        aggregation_config = config.get('aggregation', {})
        
        if not aggregation_config or aggregation_config == DEFAULT_NA_VALUE:
            return {}
        
        if isinstance(aggregation_config, dict):
            return {agg_type: columns for agg_type, columns in aggregation_config.items() 
                   if agg_type in VALID_AGGREGATION_TYPES and isinstance(columns, list)}
        
        return {}
    
    def _get_all_aggregated_columns(self, aggregation_config: Dict[str, Any]) -> List[str]:
        all_columns = []
        for columns in aggregation_config.values():
            if isinstance(columns, list):
                all_columns.extend(columns)
        return list(set(all_columns))


class AggregationExecutor(IAggregationExecutor):
    
    def __init__(self):
        self._strategies = {
            AGGREGATION_SUM: SumAggregationStrategy(),
            AGGREGATION_AVG: AvgAggregationStrategy(),
            AGGREGATION_COUNT: CountAggregationStrategy(),
            AGGREGATION_MIN: MinAggregationStrategy(),
            AGGREGATION_MAX: MaxAggregationStrategy()
        }
    
    def execute_aggregation(self, df: pd.DataFrame, groupby_columns: List[str], 
                          aggregation_config: Dict[str, List[str]]) -> pd.DataFrame:
        if not groupby_columns or not aggregation_config:
            return df
        
        try:
            grouped_df = df.groupby(groupby_columns)
            aggregated_results = {}
            
            for agg_type, columns in aggregation_config.items():
                if agg_type in self._strategies and columns:
                    strategy = self._strategies[agg_type]
                    aggregated_results[agg_type] = strategy.aggregate(grouped_df, columns)
            
            if aggregated_results:
                result_df = pd.concat(aggregated_results, axis=1)
                result_df = result_df.reset_index()
                return result_df
            else:
                return df
                
        except Exception as e:
            raise DataAggregationError(f"Failed to execute aggregation: {str(e)}")


class AggregationResultValidator(IAggregationResultValidator):
    
    def validate_result(self, result_df: pd.DataFrame, original_df: pd.DataFrame) -> None:
        if result_df is None:
            raise DataAggregationError("Aggregation result is None")
        
        if result_df.empty:
            print("⚠️  Warning: Aggregation result is empty")
        
        if len(result_df.columns) == 0:
            raise DataAggregationError("Aggregation result has no columns")
        
        print(f"✓ Aggregation validation completed. Result: {result_df.shape[0]} rows × {result_df.shape[1]} columns")


class DataAggregator(IAggregator):
    
    def __init__(self):
        self._config_validator = AggregationConfigValidator()
        self._config_extractor = AggregationConfigExtractor()
        self._executor = AggregationExecutor()
        self._result_validator = AggregationResultValidator()
    
    def apply_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        self._ensure_dataframe_valid(df)
        
        self._config_validator.validate_configuration(config)
        
        groupby_columns = self._config_extractor.extract_groupby_columns(df, config)
        aggregation_config = self._config_extractor.extract_aggregation_columns(config)
        
        if not groupby_columns or not aggregation_config:
            print("ℹ️  No aggregation configuration found, returning original dataframe")
            return df
        
        result_df = self._executor.execute_aggregation(df, groupby_columns, aggregation_config)
        
        self._result_validator.validate_result(result_df, df)
        
        return result_df
    
    def _ensure_dataframe_valid(self, df: pd.DataFrame) -> None:
        if df is None:
            raise DataAggregationError("Input dataframe is None")
        
        if df.empty:
            print("⚠️  Warning: Input dataframe is empty")
        
        if len(df.columns) == 0:
            raise DataAggregationError("Input dataframe has no columns") 