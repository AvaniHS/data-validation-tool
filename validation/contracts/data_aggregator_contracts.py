"""
Data aggregation contracts.
Separated from implementations to follow proper design principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd


class IAggregationStrategy(ABC):
    """Contract for aggregation strategies"""
    
    @abstractmethod
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        """Apply aggregation to specified columns"""
        pass


class IAggregationConfigValidator(ABC):
    """Contract for aggregation configuration validation"""
    
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validate aggregation configuration"""
        pass


class IAggregationConfigExtractor(ABC):
    """Contract for aggregation configuration extraction"""
    
    @abstractmethod
    def extract_groupby_columns(self, df: pd.DataFrame, config: Dict[str, Any]) -> List[str]:
        """Extract groupby columns from configuration"""
        pass
    
    @abstractmethod
    def extract_aggregation_columns(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract aggregation columns from configuration"""
        pass


class IAggregationExecutor(ABC):
    """Contract for aggregation execution"""
    
    @abstractmethod
    def execute_aggregation(self, df: pd.DataFrame, groupby_columns: List[str], 
                          aggregation_config: Dict[str, List[str]]) -> pd.DataFrame:
        """Execute aggregation on dataframe"""
        pass


class IAggregationResultValidator(ABC):
    """Contract for aggregation result validation"""
    
    @abstractmethod
    def validate_result(self, result_df: pd.DataFrame, original_df: pd.DataFrame) -> None:
        """Validate aggregation result"""
        pass


class IAggregator(ABC):
    """Contract for data aggregation operations"""
    
    @abstractmethod
    def apply_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Apply aggregation logic to dataframe based on configuration"""
        pass 