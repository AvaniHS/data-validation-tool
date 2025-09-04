from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd


class IComparisonStrategy(ABC):
    @abstractmethod
    def compare(self, value1: Any, value2: Any) -> Tuple[str, Optional[float]]:
        pass


class IComparisonConfigValidator(ABC):
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        pass


class IComparisonConfigExtractor(ABC):
    @abstractmethod
    def extract_column_mapping(self, config: Dict[str, Any]) -> Dict[str, str]:
        pass


class IComparisonStrategySelector(ABC):
    @abstractmethod
    def select_strategy(self, series1: pd.Series, series2: pd.Series, config: Dict[str, Any], file1_col: str) -> IComparisonStrategy:
        pass


class IComparisonExecutor(ABC):
    @abstractmethod
    def execute_comparison(self, df: pd.DataFrame, column_mapping: Dict[str, str], 
                          strategy_selector: IComparisonStrategySelector, config: Dict[str, Any]) -> pd.DataFrame:
        pass


class IComparisonResultValidator(ABC):
    @abstractmethod
    def validate_result(self, result_df: pd.DataFrame, original_df: pd.DataFrame) -> None:
        pass
