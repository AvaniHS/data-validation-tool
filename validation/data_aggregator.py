"""
Data aggregation module for applying aggregation logic on output dataframe.
Follows OOP, SOLID principles, and separation of concerns.
"""

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
    """Sum aggregation strategy"""
    
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        """Apply sum aggregation to specified columns"""
        if not columns:
            return pd.Series()
        return df[columns].sum()


class AvgAggregationStrategy(IAggregationStrategy):
    """Average aggregation strategy"""
    
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        """Apply average aggregation to specified columns"""
        if not columns:
            return pd.Series()
        return df[columns].mean()


class CountAggregationStrategy(IAggregationStrategy):
    """Count aggregation strategy"""
    
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        """Apply count aggregation to specified columns"""
        if not columns:
            return pd.Series()
        return df[columns].count()


class MinAggregationStrategy(IAggregationStrategy):
    """Minimum aggregation strategy"""
    
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        """Apply minimum aggregation to specified columns"""
        if not columns:
            return pd.Series()
        return df[columns].min()


class MaxAggregationStrategy(IAggregationStrategy):
    """Maximum aggregation strategy"""
    
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        """Apply maximum aggregation to specified columns"""
        if not columns:
            return pd.Series()
        return df[columns].max()


class AggregationConfigValidator(IAggregationConfigValidator):
    """Concrete implementation of aggregation configuration validation"""
    
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validate aggregation configuration"""
        aggregation_config = config.get('aggregation', {})
        
        if not aggregation_config or aggregation_config == DEFAULT_NA_VALUE:
            return  # No aggregation needed
        
        if not isinstance(aggregation_config, dict):
            raise InvalidConfigurationError("Aggregation configuration must be a dictionary")
        
        # Validate aggregation types
        for agg_type, columns in aggregation_config.items():
            if agg_type not in VALID_AGGREGATION_TYPES:
                raise InvalidConfigurationError(f"Invalid aggregation type: {agg_type}. Valid types: {VALID_AGGREGATION_TYPES}")
            
            if not isinstance(columns, list):
                raise InvalidConfigurationError(f"Aggregation columns for '{agg_type}' must be a list")


class AggregationConfigExtractor(IAggregationConfigExtractor):
    """Concrete implementation of aggregation configuration extraction"""
    
    def extract_groupby_columns(self, df: pd.DataFrame, config: Dict[str, Any]) -> List[str]:
        """Extract groupby columns from configuration"""
        aggregation_config = config.get('aggregation', {})
        
        if not aggregation_config or aggregation_config == DEFAULT_NA_VALUE:
            return []
        
        # Get all columns that are not being aggregated
        all_aggregated_columns = self._get_all_aggregated_columns(aggregation_config)
        groupby_columns = [col for col in df.columns if col not in all_aggregated_columns]
        
        return groupby_columns
    
    def extract_aggregation_columns(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract aggregation columns from configuration"""
        aggregation_config = config.get('aggregation', {})
        
        if not aggregation_config or aggregation_config == DEFAULT_NA_VALUE:
            return {}
        
        return aggregation_config.copy()
    
    def _get_all_aggregated_columns(self, aggregation_config: Dict[str, Any]) -> List[str]:
        """Get all columns that are being aggregated"""
        all_columns = []
        for columns in aggregation_config.values():
            if isinstance(columns, list):
                all_columns.extend(columns)
        return list(set(all_columns))  # Remove duplicates


class AggregationExecutor(IAggregationExecutor):
    """Concrete implementation of aggregation execution"""
    
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
        """Execute aggregation on dataframe"""
        try:
            if not aggregation_config:
                return df
            
            # Prepare aggregation dictionary for pandas groupby
            agg_dict = {}
            for agg_type, columns in aggregation_config.items():
                if agg_type in self._strategies and columns:
                    for col in columns:
                        if col in df.columns:
                            agg_dict[col] = agg_type
            
            if not agg_dict:
                return df
            
            # Perform groupby aggregation
            if groupby_columns:
                # Group by specified columns
                grouped = df.groupby(groupby_columns, as_index=False)
                result = grouped.agg(agg_dict)
            else:
                # No grouping, aggregate entire dataframe
                result = df.agg(agg_dict).to_frame().T
            
            return result
            
        except Exception as e:
            raise DataAggregationError(f"Failed to execute aggregation: {str(e)}")


class AggregationResultValidator(IAggregationResultValidator):
    """Concrete implementation of aggregation result validation"""
    
    def validate_result(self, result_df: pd.DataFrame, original_df: pd.DataFrame) -> None:
        """Validate aggregation result"""
        if result_df is None:
            raise DataAggregationError("Aggregation result is None")
        
        if result_df.empty:
            print("⚠️  Warning: Aggregation resulted in empty dataframe")
        
        # Check if result has reasonable number of rows
        if len(result_df) > len(original_df):
            print(f"⚠️  Warning: Aggregation result has more rows ({len(result_df)}) than original ({len(original_df)})")


class DataAggregator(IAggregator):
    """Concrete implementation of data aggregation"""
    
    def __init__(self):
        self._config_validator = AggregationConfigValidator()
        self._config_extractor = AggregationConfigExtractor()
        self._executor = AggregationExecutor()
        self._result_validator = AggregationResultValidator()
    
    def apply_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply aggregation logic to dataframe based on configuration
        
        Args:
            df: Input dataframe to aggregate
            config: Configuration dictionary containing aggregation settings
            
        Returns:
            Aggregated dataframe
            
        Raises:
            DataAggregationError: If aggregation fails
            InvalidConfigurationError: If configuration is invalid
        """
        try:
            self._ensure_dataframe_valid(df)
            
            # Validate configuration
            self._config_validator.validate_configuration(config)
            
            # Extract configuration parameters
            groupby_columns = self._config_extractor.extract_groupby_columns(df, config)
            aggregation_config = self._config_extractor.extract_aggregation_columns(config)
            
            # Check if aggregation is needed
            if not aggregation_config:
                print("✓ No aggregation required")
                return df
            
            # Execute aggregation
            result_df = self._executor.execute_aggregation(df, groupby_columns, aggregation_config)
            
            # Validate result
            self._result_validator.validate_result(result_df, df)
            
            print(f"✓ Data aggregation completed successfully")
            print(f"  Original dataframe: {len(df)} rows, {len(df.columns)} columns")
            print(f"  Aggregated result: {len(result_df)} rows, {len(result_df.columns)} columns")
            if groupby_columns:
                print(f"  Grouped by: {groupby_columns}")
            print(f"  Aggregation types: {list(aggregation_config.keys())}")
            
            return result_df
            
        except (InvalidConfigurationError, DataAggregationError):
            raise
        except Exception as e:
            raise DataAggregationError(f"Failed to apply aggregation: {str(e)}")
    
    def _ensure_dataframe_valid(self, df: pd.DataFrame) -> None:
        if df is None:
            raise DataAggregationError("Input dataframe cannot be None")
        
        if df.empty:
            raise DataAggregationError("Input dataframe is empty")
        
        if len(df.columns) == 0:
            raise DataAggregationError("Input dataframe has no columns") 