from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd


class IOutputConfigValidator(ABC):
    
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        pass


class IOutputConfigExtractor(ABC):
    
    @abstractmethod
    def extract_output_settings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        pass


class IDataFormatter(ABC):
    
    @abstractmethod
    def format_dataframe(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        pass


class IFileWriter(ABC):
    
    @abstractmethod
    def write_file(self, df: pd.DataFrame, output_path: str, output_sheet: str) -> None:
        pass


class IOutputResultValidator(ABC):
    
    @abstractmethod
    def validate_result(self, df: pd.DataFrame, output_path: str) -> None:
        pass


class IOutputWriter(ABC):
    
    @abstractmethod
    def write_output(self, df: pd.DataFrame, config: Dict[str, Any]) -> None:
        pass