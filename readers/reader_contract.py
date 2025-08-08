from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd

class IDataReader(ABC):
    @abstractmethod
    def read(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        pass 