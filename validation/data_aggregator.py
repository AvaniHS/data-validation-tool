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
from validation.aggregation_step_mapper import AggregationStepMapper
from validation.groupby_column_resolver import GroupByColumnResolver
from services.logging import get_logger
from constants import (
    VALID_AGGREGATION_TYPES, AGGREGATION_SUM, AGGREGATION_AVG, AGGREGATION_COUNT,
    AGGREGATION_MIN, AGGREGATION_MAX, DEFAULT_NA_VALUE,
    AGGREGATION_STEP_FILE1, AGGREGATION_STEP_FILE2, AGGREGATION_STEP_FINAL,
    AGGREGATION_CONFIG_FILE1_COLUMNS, AGGREGATION_CONFIG_FILE2_COLUMNS,
    AGGREGATION_CONFIG_FINAL_COLUMNS, AGGREGATION_CONFIG_FILE1_GROUPBY,
    AGGREGATION_CONFIG_FILE2_GROUPBY, AGGREGATION_CONFIG_FINAL_GROUPBY,
    AGGREGATION_CONFIG_GROUPBY
)


class SumAggregationStrategy(IAggregationStrategy):
    """
    Strategy for summing columns in a grouped dataframe.
    """
    
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        """
        Sum the specified columns in the grouped dataframe.
        
        Args:
            df: A grouped dataframe (result of groupby operation)
            columns: List of column names to sum
        
        Returns:
            Series with sum values for each group
        """
        if not columns:
            return pd.Series()
        return df[columns].sum()


class AvgAggregationStrategy(IAggregationStrategy):
    """
    Strategy for calculating average of columns in a grouped dataframe.
    """
    
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        """
        Calculate the average of specified columns in the grouped dataframe.
        
        Args:
            df: A grouped dataframe (result of groupby operation)
            columns: List of column names to average
        
        Returns:
            Series with average values for each group
        """
        if not columns:
            return pd.Series()
        return df[columns].mean()


class CountAggregationStrategy(IAggregationStrategy):
    """
    Strategy for counting non-null values in columns of a grouped dataframe.
    """
    
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        """
        Count non-null values in specified columns of the grouped dataframe.
        
        Args:
            df: A grouped dataframe (result of groupby operation)
            columns: List of column names to count
        
        Returns:
            Series with count values for each group
        """
        if not columns:
            return pd.Series()
        return df[columns].count()


class MinAggregationStrategy(IAggregationStrategy):
    """
    Strategy for finding minimum values in columns of a grouped dataframe.
    """
    
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        """
        Find minimum values in specified columns of the grouped dataframe.
        
        Args:
            df: A grouped dataframe (result of groupby operation)
            columns: List of column names to find minimum
        
        Returns:
            Series with minimum values for each group
        """
        if not columns:
            return pd.Series()
        return df[columns].min()


class MaxAggregationStrategy(IAggregationStrategy):
    """
    Strategy for finding maximum values in columns of a grouped dataframe.
    """
    
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        """
        Find maximum values in specified columns of the grouped dataframe.
        
        Args:
            df: A grouped dataframe (result of groupby operation)
            columns: List of column names to find maximum
        
        Returns:
            Series with maximum values for each group
        """
        if not columns:
            return pd.Series()
        return df[columns].max()


class AggregationConfigValidator(IAggregationConfigValidator):
    """
    Validates aggregation configuration structure and values.
    """
    
    def __init__(self):
        self._logger = get_logger(self.__class__.__name__)
    
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """
        Validate the aggregation configuration structure.
        
        Args:
            config: The configuration dictionary containing aggregation settings
        
        Raises:
            InvalidConfigurationError: If the configuration is invalid
        """
        aggregation_config = config.get('aggregation', {})
        
        if not aggregation_config or aggregation_config == DEFAULT_NA_VALUE:
            return
        
        if not isinstance(aggregation_config, dict):
            raise InvalidConfigurationError("Aggregation configuration must be a dictionary")
        
        for key, value in aggregation_config.items():
            if key in [AGGREGATION_CONFIG_FILE1_COLUMNS, AGGREGATION_CONFIG_FILE2_COLUMNS, AGGREGATION_CONFIG_FINAL_COLUMNS]:
                if not isinstance(value, dict):
                    raise InvalidConfigurationError(f"Aggregation configuration '{key}' must be a dictionary")
                for agg_type, columns in value.items():
                    if agg_type not in VALID_AGGREGATION_TYPES:
                        raise InvalidConfigurationError(f"Invalid aggregation type: {agg_type}. Valid types: {VALID_AGGREGATION_TYPES}")
                    if not isinstance(columns, list):
                        raise InvalidConfigurationError(f"Aggregation columns for '{agg_type}' in '{key}' must be a list")
            elif key in [AGGREGATION_CONFIG_FILE1_GROUPBY, AGGREGATION_CONFIG_FILE2_GROUPBY, AGGREGATION_CONFIG_FINAL_GROUPBY, AGGREGATION_CONFIG_GROUPBY]:
                if value != DEFAULT_NA_VALUE and not isinstance(value, list):
                    raise InvalidConfigurationError(f"Groupby columns '{key}' must be a list or 'NA'")
            elif key in VALID_AGGREGATION_TYPES:
                if not isinstance(value, list):
                    raise InvalidConfigurationError(f"Aggregation columns for '{key}' must be a list")


class AggregationConfigExtractor(IAggregationConfigExtractor):
    """
    Extracts aggregation configuration from the main configuration dictionary.
    Handles extraction of groupby columns and aggregation columns for different steps.
    """
    
    def __init__(self):
        self._step_mapper = AggregationStepMapper()
        self._logger = get_logger(self.__class__.__name__)
    
    def extract_groupby_columns(self, df: pd.DataFrame, config: Dict[str, Any], step: str = AGGREGATION_STEP_FINAL) -> List[str]:
        """
        Extract groupby columns from configuration for a specific aggregation step.
        
        Args:
            df: The dataframe to validate columns against
            config: The configuration dictionary
            step: The aggregation step ('file1', 'file2', or 'final')
        
        Returns:
            List of column names to use for grouping, or empty list if not specified
        """
        aggregation_config = config.get('aggregation', {})
        
        if not aggregation_config or aggregation_config == DEFAULT_NA_VALUE:
            return []
        
        if not isinstance(aggregation_config, dict):
            return []
        
        groupby_key = self._step_mapper.get_groupby_key(step)
        
        if groupby_key and groupby_key in aggregation_config:
            groupby_cols = aggregation_config[groupby_key]
            if groupby_cols != DEFAULT_NA_VALUE and isinstance(groupby_cols, list):
                valid_cols = [col for col in groupby_cols if col in df.columns]
                if len(valid_cols) < len(groupby_cols):
                    missing = set(groupby_cols) - set(valid_cols)
                    self._logger.warning(f"Some groupby columns not found in dataframe for step '{step}': {missing}")
                return valid_cols
        
        if AGGREGATION_CONFIG_GROUPBY in aggregation_config and step == AGGREGATION_STEP_FINAL:
            groupby_cols = aggregation_config[AGGREGATION_CONFIG_GROUPBY]
            if groupby_cols != DEFAULT_NA_VALUE and isinstance(groupby_cols, list):
                valid_cols = [col for col in groupby_cols if col in df.columns]
                if len(valid_cols) < len(groupby_cols):
                    missing = set(groupby_cols) - set(valid_cols)
                    self._logger.warning(f"Some groupby columns not found in dataframe: {missing}")
                return valid_cols
        
        return []
    
    def extract_aggregation_columns(self, config: Dict[str, Any], step: str = AGGREGATION_STEP_FINAL) -> Dict[str, List[str]]:
        """
        Extract aggregation columns configuration for a specific step.
        
        Args:
            config: The configuration dictionary
            step: The aggregation step ('file1', 'file2', or 'final')
        
        Returns:
            Dictionary mapping aggregation types to lists of column names
        """
        aggregation_config = config.get('aggregation', {})
        
        if not aggregation_config or aggregation_config == DEFAULT_NA_VALUE:
            return {}
        
        if not isinstance(aggregation_config, dict):
            return {}
        
        columns_key = self._step_mapper.get_columns_key(step)
        
        if columns_key and columns_key in aggregation_config:
            agg_dict = aggregation_config[columns_key]
            if isinstance(agg_dict, dict):
                result = {
                    agg_type: columns for agg_type, columns in agg_dict.items() 
                    if agg_type in VALID_AGGREGATION_TYPES and isinstance(columns, list) and columns
                }
                if result:
                    self._logger.debug(f"Extracted {len(result)} aggregation types for step '{step}'")
                return result
        
        if step == AGGREGATION_STEP_FINAL and any(key in VALID_AGGREGATION_TYPES for key in aggregation_config.keys()):
            result = {
                agg_type: columns for agg_type, columns in aggregation_config.items() 
                if agg_type in VALID_AGGREGATION_TYPES and isinstance(columns, list) and columns
            }
            if result:
                self._logger.debug(f"Extracted {len(result)} aggregation types from legacy format")
            return result
        
        return {}
    
    def _get_all_aggregated_columns(self, aggregation_config: Dict[str, Any], step: str = AGGREGATION_STEP_FINAL) -> List[str]:
        """
        Get all column names that are specified for aggregation in a given step.
        
        Args:
            aggregation_config: The aggregation configuration dictionary
            step: The aggregation step
        
        Returns:
            List of all column names used in aggregation
        """
        all_columns = []
        agg_columns = self.extract_aggregation_columns({'aggregation': aggregation_config}, step)
        for columns in agg_columns.values():
            if isinstance(columns, list):
                all_columns.extend(columns)
        return list(set(all_columns))


class AggregationExecutor(IAggregationExecutor):
    """
    Executes aggregation operations on dataframes using strategy pattern.
    """
    
    def __init__(self):
        self._strategies = {
            AGGREGATION_SUM: SumAggregationStrategy(),
            AGGREGATION_AVG: AvgAggregationStrategy(),
            AGGREGATION_COUNT: CountAggregationStrategy(),
            AGGREGATION_MIN: MinAggregationStrategy(),
            AGGREGATION_MAX: MaxAggregationStrategy()
        }
        self._logger = get_logger(self.__class__.__name__)
    
    def execute_aggregation(self, df: pd.DataFrame, groupby_columns: List[str], 
                          aggregation_config: Dict[str, List[str]]) -> pd.DataFrame:
        """
        Execute aggregation operations on a dataframe.
        
        Args:
            df: The dataframe to aggregate
            groupby_columns: Columns to group by
            aggregation_config: Dictionary mapping aggregation types to column lists
        
        Returns:
            Aggregated dataframe
        
        Raises:
            DataAggregationError: If aggregation fails
        """
        if not groupby_columns or not aggregation_config:
            return df
        
        try:
            self._logger.debug(f"Executing aggregation with {len(groupby_columns)} groupby columns and {len(aggregation_config)} aggregation types")
            grouped_df = df.groupby(groupby_columns)
            aggregated_results = {}
            
            for agg_type, columns in aggregation_config.items():
                if agg_type in self._strategies and columns:
                    strategy = self._strategies[agg_type]
                    aggregated_results[agg_type] = strategy.aggregate(grouped_df, columns)
                    self._logger.debug(f"Applied {agg_type} aggregation to {len(columns)} columns")
            
            if aggregated_results:
                result_df = pd.concat(aggregated_results, axis=1)
                result_df = result_df.reset_index()
                self._logger.info(f"Aggregation completed: {result_df.shape[0]} rows × {result_df.shape[1]} columns")
                return result_df
            else:
                self._logger.warning("No aggregation results produced, returning original dataframe")
                return df
                
        except (ValueError, KeyError, TypeError) as e:
            self._logger.error(f"Aggregation failed due to data error: {str(e)}", exception=e)
            raise DataAggregationError(f"Failed to execute aggregation: {str(e)}") from e
        except Exception as e:
            self._logger.error(f"Unexpected error during aggregation: {str(e)}", exception=e)
            raise DataAggregationError(f"Unexpected error during aggregation: {str(e)}") from e


class AggregationResultValidator(IAggregationResultValidator):
    """
    Validates aggregation results to ensure data integrity.
    """
    
    def __init__(self):
        self._logger = get_logger(self.__class__.__name__)
    
    def validate_result(self, result_df: pd.DataFrame, original_df: pd.DataFrame) -> None:
        """
        Validate that the aggregation result is valid.
        
        Args:
            result_df: The aggregated dataframe
            original_df: The original dataframe before aggregation
        
        Raises:
            DataAggregationError: If the result is invalid
        """
        if result_df is None:
            self._logger.error("Aggregation result is None")
            raise DataAggregationError("Aggregation result is None")
        
        if result_df.empty:
            self._logger.warning("Aggregation result is empty")
        
        if len(result_df.columns) == 0:
            self._logger.error("Aggregation result has no columns")
            raise DataAggregationError("Aggregation result has no columns")
        
        self._logger.info(f"Aggregation validation completed. Result: {result_df.shape[0]} rows × {result_df.shape[1]} columns")


class DataAggregator(IAggregator):
    """
    Main aggregator class that orchestrates aggregation operations.
    Supports separate aggregation steps for file1, file2, and final aggregation.
    """
    
    def __init__(self):
        self._config_validator = AggregationConfigValidator()
        self._config_extractor = AggregationConfigExtractor()
        self._groupby_resolver = GroupByColumnResolver(self._config_extractor)
        self._executor = AggregationExecutor()
        self._result_validator = AggregationResultValidator()
        self._logger = get_logger(self.__class__.__name__)
    
    def apply_aggregation(self, df: pd.DataFrame, config: Dict[str, Any], step: str = AGGREGATION_STEP_FINAL) -> pd.DataFrame:
        """
        Apply aggregation to a dataframe for a specific step.
        
        Args:
            df: The dataframe to aggregate
            config: The configuration dictionary
            step: The aggregation step ('file1', 'file2', or 'final')
        
        Returns:
            Aggregated dataframe, or original dataframe if no aggregation configured
        
        Raises:
            DataAggregationError: If aggregation fails
            InvalidConfigurationError: If configuration is invalid
        """
        self._ensure_dataframe_valid(df)
        
        aggregation_config = config.get('aggregation', {})
        if not aggregation_config or aggregation_config == DEFAULT_NA_VALUE:
            self._logger.debug(f"No aggregation configuration for step '{step}', returning original dataframe")
            return df
        
        self._config_validator.validate_configuration(config)
        
        aggregation_columns = self._config_extractor.extract_aggregation_columns(config, step)
        
        if not aggregation_columns:
            self._logger.debug(f"No aggregation columns configured for step '{step}', returning original dataframe")
            return df
        
        groupby_columns = self._groupby_resolver.resolve_groupby_columns(df, config, step)
        
        if not groupby_columns:
            self._logger.warning(f"No groupby columns found for {step} aggregation, returning original dataframe")
            return df
        
        self._logger.info(f"Applying {step} aggregation with {len(groupby_columns)} groupby columns")
        result_df = self._executor.execute_aggregation(df, groupby_columns, aggregation_columns)
        
        self._result_validator.validate_result(result_df, df)
        
        return result_df
    
    def apply_file1_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply aggregation to file1 dataframe.
        
        Args:
            df: The file1 dataframe
            config: The configuration dictionary
        
        Returns:
            Aggregated dataframe
        """
        return self.apply_aggregation(df, config, step=AGGREGATION_STEP_FILE1)
    
    def apply_file2_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply aggregation to file2 dataframe.
        
        Args:
            df: The file2 dataframe
            config: The configuration dictionary
        
        Returns:
            Aggregated dataframe
        """
        return self.apply_aggregation(df, config, step=AGGREGATION_STEP_FILE2)
    
    def apply_final_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply final aggregation after joining dataframes.
        
        Args:
            df: The joined dataframe
            config: The configuration dictionary
        
        Returns:
            Aggregated dataframe
        """
        return self.apply_aggregation(df, config, step=AGGREGATION_STEP_FINAL)
    
    def _ensure_dataframe_valid(self, df: pd.DataFrame) -> None:
        """
        Validate that the input dataframe is valid for aggregation.
        
        Args:
            df: The dataframe to validate
        
        Raises:
            DataAggregationError: If the dataframe is invalid
        """
        if df is None:
            self._logger.error("Input dataframe is None")
            raise DataAggregationError("Input dataframe is None")
        
        if df.empty:
            self._logger.warning("Input dataframe is empty")
        
        if len(df.columns) == 0:
            self._logger.error("Input dataframe has no columns")
            raise DataAggregationError("Input dataframe has no columns") 