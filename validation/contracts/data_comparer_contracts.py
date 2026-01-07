from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd


class IDataComparer(ABC):
    
    @abstractmethod
    def compare_mapped_columns(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        pass 