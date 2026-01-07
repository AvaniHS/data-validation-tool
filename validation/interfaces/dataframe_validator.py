from abc import ABC, abstractmethod
import pandas as pd


class IDataFrameValidator(ABC):
    @abstractmethod
    def validate_dataframe(self, df: pd.DataFrame) -> None:
        pass
