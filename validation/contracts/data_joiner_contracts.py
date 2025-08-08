"""
Data joining contracts.
Separated from implementations to follow proper design principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
import pandas as pd


class IJoinKeyExtractor(ABC):
    """Contract for join key extraction operations"""
    
    @abstractmethod
    def extract_join_keys(self, config: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Extract join keys from configuration"""
        pass


class IJoinKeyValidator(ABC):
    """Contract for join key validation operations"""
    
    @abstractmethod
    def validate_join_keys(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                          left_keys: List[str], right_keys: List[str]) -> None:
        """Validate that join keys exist in respective dataframes"""
        pass


class IJoinExecutor(ABC):
    """Contract for join execution operations"""
    
    @abstractmethod
    def execute_join(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                    left_keys: List[str], right_keys: List[str]) -> pd.DataFrame:
        """Execute the join operation"""
        pass


class IJoinResultValidator(ABC):
    """Contract for join result validation"""
    
    @abstractmethod
    def validate_join_result(self, joined_df: pd.DataFrame, df1: pd.DataFrame, df2: pd.DataFrame) -> None:
        """Validate the join result"""
        pass


class IDataJoiner(ABC):
    """Contract for data joining operations"""
    
    @abstractmethod
    def join_dataframes(self, df1: pd.DataFrame, df2: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Join two dataframes based on configuration join keys"""
        pass 