from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
import pandas as pd


class IJoinKeyExtractor(ABC):
    
    @abstractmethod
    def extract_join_keys(self, config: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        pass


class IJoinKeyValidator(ABC):
    
    @abstractmethod
    def validate_join_keys(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                          left_keys: List[str], right_keys: List[str]) -> None:
        pass


class IJoinExecutor(ABC):
    
    @abstractmethod
    def execute_join(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                    left_keys: List[str], right_keys: List[str]) -> pd.DataFrame:
        pass


class IJoinResultValidator(ABC):
    
    @abstractmethod
    def validate_join_result(self, joined_df: pd.DataFrame, df1: pd.DataFrame, df2: pd.DataFrame) -> None:
        pass


class IDataJoiner(ABC):
    
    @abstractmethod
    def join_dataframes(self, df1: pd.DataFrame, df2: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        pass 