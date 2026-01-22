from typing import Optional, Dict
from constants import (
    AGGREGATION_STEP_FILE1, AGGREGATION_STEP_FILE2, AGGREGATION_STEP_FINAL,
    AGGREGATION_CONFIG_FILE1_COLUMNS, AGGREGATION_CONFIG_FILE2_COLUMNS,
    AGGREGATION_CONFIG_FINAL_COLUMNS, AGGREGATION_CONFIG_FILE1_GROUPBY,
    AGGREGATION_CONFIG_FILE2_GROUPBY, AGGREGATION_CONFIG_FINAL_GROUPBY
)


class AggregationStepMapper:
    """
    Maps aggregation steps to their corresponding configuration keys.
    Eliminates code duplication by centralizing step-to-key mapping logic.
    """
    
    STEP_TO_GROUPBY_KEY: Dict[str, str] = {
        AGGREGATION_STEP_FILE1: AGGREGATION_CONFIG_FILE1_GROUPBY,
        AGGREGATION_STEP_FILE2: AGGREGATION_CONFIG_FILE2_GROUPBY,
        AGGREGATION_STEP_FINAL: AGGREGATION_CONFIG_FINAL_GROUPBY
    }
    
    STEP_TO_COLUMNS_KEY: Dict[str, str] = {
        AGGREGATION_STEP_FILE1: AGGREGATION_CONFIG_FILE1_COLUMNS,
        AGGREGATION_STEP_FILE2: AGGREGATION_CONFIG_FILE2_COLUMNS,
        AGGREGATION_STEP_FINAL: AGGREGATION_CONFIG_FINAL_COLUMNS
    }
    
    @classmethod
    def get_groupby_key(cls, step: str) -> Optional[str]:
        """
        Get the groupby columns configuration key for a given aggregation step.
        
        Args:
            step: The aggregation step ('file1', 'file2', or 'final')
        
        Returns:
            The configuration key for groupby columns, or None if step is invalid
        """
        return cls.STEP_TO_GROUPBY_KEY.get(step)
    
    @classmethod
    def get_columns_key(cls, step: str) -> Optional[str]:
        """
        Get the aggregation columns configuration key for a given aggregation step.
        
        Args:
            step: The aggregation step ('file1', 'file2', or 'final')
        
        Returns:
            The configuration key for aggregation columns, or None if step is invalid
        """
        return cls.STEP_TO_COLUMNS_KEY.get(step)
    
    @classmethod
    def is_valid_step(cls, step: str) -> bool:
        """
        Check if a given step is a valid aggregation step.
        
        Args:
            step: The step to validate
        
        Returns:
            True if step is valid, False otherwise
        """
        return step in cls.STEP_TO_GROUPBY_KEY
