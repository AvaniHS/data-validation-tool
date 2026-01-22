from typing import Dict, Any, List
import pandas as pd
from validation.aggregation_step_mapper import AggregationStepMapper
from constants import (
    AGGREGATION_STEP_FILE1, AGGREGATION_STEP_FILE2, AGGREGATION_STEP_FINAL
)


class GroupByColumnResolver:
    """
    Resolves groupby columns for aggregation steps.
    Implements auto-grouping logic: if groupby columns are not specified,
    automatically uses all non-aggregated, non-join-key columns.
    """
    
    def __init__(self, config_extractor):
        """
        Initialize the resolver with a config extractor.
        
        Args:
            config_extractor: An instance of AggregationConfigExtractor
        """
        self._config_extractor = config_extractor
    
    def resolve_groupby_columns(
        self, 
        df: pd.DataFrame, 
        config: Dict[str, Any], 
        step: str
    ) -> List[str]:
        """
        Resolve groupby columns for a given aggregation step.
        First tries to extract from configuration, then falls back to auto-determination.
        
        Args:
            df: The dataframe to validate columns against
            config: The configuration dictionary
            step: The aggregation step ('file1', 'file2', or 'final')
        
        Returns:
            List of column names to use for grouping
        """
        groupby_columns = self._config_extractor.extract_groupby_columns(df, config, step)
        
        if not groupby_columns:
            groupby_columns = self._auto_determine_groupby_columns(df, config, step)
        
        return groupby_columns
    
    def _auto_determine_groupby_columns(
        self, 
        df: pd.DataFrame, 
        config: Dict[str, Any], 
        step: str
    ) -> List[str]:
        """
        Automatically determine groupby columns by excluding aggregated columns and join keys.
        
        Args:
            df: The dataframe
            config: The configuration dictionary
            step: The aggregation step
        
        Returns:
            List of column names that should be used for grouping
        """
        all_columns = list(df.columns)
        aggregated_columns = self._config_extractor._get_all_aggregated_columns(
            config.get('aggregation', {}), 
            step
        )
        join_keys = self._get_join_keys_for_step(config, step)
        
        groupby_columns = [
            col for col in all_columns 
            if col not in aggregated_columns and col not in join_keys
        ]
        
        return groupby_columns
    
    def _get_join_keys_for_step(self, config: Dict[str, Any], step: str) -> List[str]:
        """
        Get join keys relevant to a specific aggregation step.
        
        Args:
            config: The configuration dictionary
            step: The aggregation step
        
        Returns:
            List of join key column names
        """
        join_keys_dict = config.get('join_keys', {})
        
        if step == AGGREGATION_STEP_FILE1:
            return list(join_keys_dict.keys())
        elif step == AGGREGATION_STEP_FILE2:
            return list(join_keys_dict.values())
        elif step == AGGREGATION_STEP_FINAL:
            left_keys = list(join_keys_dict.keys())
            right_keys = list(join_keys_dict.values())
            column_mapping = config.get('column_mapping', {})
            mapped_right_keys = [
                column_mapping.get(left_key, right_key) 
                for left_key, right_key in join_keys_dict.items()
            ]
            return left_keys + right_keys + mapped_right_keys
        
        return []
