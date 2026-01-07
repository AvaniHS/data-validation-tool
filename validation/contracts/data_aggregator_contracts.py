from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd


class IAggregationStrategy(ABC):
    
    @abstractmethod
    def aggregate(self, df: pd.DataFrame, columns: List[str]) -> pd.Series:
        pass


class IAggregationConfigValidator(ABC):
    
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        pass


class IAggregationConfigExtractor(ABC):
    
    @abstractmethod
    def extract_groupby_columns(self, df: pd.DataFrame, config: Dict[str, Any]) -> List[str]:
        pass
    
    @abstractmethod
    def extract_aggregation_columns(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        pass


class IAggregationExecutor(ABC):
    
    @abstractmethod
    def execute_aggregation(self, df: pd.DataFrame, groupby_columns: List[str], 
                          aggregation_config: Dict[str, List[str]]) -> pd.DataFrame:
        pass


class IAggregationResultValidator(ABC):
    
    @abstractmethod
    def validate_result(self, result_df: pd.DataFrame, original_df: pd.DataFrame) -> None:
        pass


class IAggregator(ABC):
    
    @abstractmethod
    def apply_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        pass 