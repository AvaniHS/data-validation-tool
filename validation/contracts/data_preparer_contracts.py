from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import pandas as pd


class IDataValidator(ABC):
    
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def validate_dataframe(self, df: pd.DataFrame, name: str) -> None:
        pass


class IDataLoader(ABC):
    
    @abstractmethod
    def load_single_file_two_sheets(self, file_path: str, sheet1: str, sheet2: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        pass
    
    @abstractmethod
    def load_two_separate_files(self, file1_path: str, file2_path: str, sheet1: str, sheet2: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        pass


class IDataCleaner(ABC):
    
    @abstractmethod
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        pass


class ITypeDetector(ABC):
    
    @abstractmethod
    def detect_and_validate_join_key_types(self, config: Dict[str, Any], df1: pd.DataFrame, df2: pd.DataFrame) -> Dict[str, str]:
        pass


class IDataPreparer(ABC):
    
    @abstractmethod
    def prepare_data_frames(self, config: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        pass 