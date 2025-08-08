"""
Data comparison contracts.
Separated from implementations to follow proper design principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd


class IComparisonStrategy(ABC):
    """Contract for comparison strategies"""
    
    @abstractmethod
    def compare(self, value1: Any, value2: Any) -> Tuple[str, Optional[float]]:
        """Compare two values and return actual difference and delta percentage"""
        pass


class IComparisonConfigValidator(ABC):
    """Contract for comparison configuration validation"""
    
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validate comparison configuration"""
        pass


class IComparisonConfigExtractor(ABC):
    """Contract for comparison configuration extraction"""
    
    @abstractmethod
    def extract_column_mapping(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Extract column mapping from configuration"""
        pass


class IComparisonStrategySelector(ABC):
    """Contract for comparison strategy selection"""
    
    @abstractmethod
    def select_strategy(self, series1: pd.Series, series2: pd.Series, config: Dict[str, Any], file1_col: str) -> IComparisonStrategy:
        """Select appropriate comparison strategy"""
        pass


class IComparisonExecutor(ABC):
    """Contract for comparison execution"""
    
    @abstractmethod
    def execute_comparison(self, df: pd.DataFrame, column_mapping: Dict[str, str], 
                          strategy_selector: IComparisonStrategySelector, config: Dict[str, Any]) -> pd.DataFrame:
        """Execute comparison on dataframe"""
        pass


class IComparisonResultValidator(ABC):
    """Contract for comparison result validation"""
    
    @abstractmethod
    def validate_result(self, result_df: pd.DataFrame, original_df: pd.DataFrame) -> None:
        """Validate comparison result"""
        pass


class IDataComparer(ABC):
    """Contract for data comparison operations"""
    
    @abstractmethod
    def compare_mapped_columns(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Compare mapped columns in dataframe based on configuration"""
        pass 