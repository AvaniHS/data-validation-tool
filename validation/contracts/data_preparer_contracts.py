"""
Data preparation contracts.
Separated from implementations to follow proper design principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import pandas as pd


class IDataValidator(ABC):
    """Contract for data validation operations"""
    
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validate configuration parameters"""
        pass
    
    @abstractmethod
    def validate_dataframe(self, df: pd.DataFrame, name: str) -> None:
        """Validate dataframe structure and content"""
        pass


class IDataLoader(ABC):
    """Contract for data loading operations"""
    
    @abstractmethod
    def load_single_file_two_sheets(self, file_path: str, sheet1: str, sheet2: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load two sheets from a single file"""
        pass
    
    @abstractmethod
    def load_two_separate_files(self, file1_path: str, file2_path: str, sheet1: str, sheet2: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load data from two separate files"""
        pass


class IDataCleaner(ABC):
    """Contract for data cleaning operations"""
    
    @abstractmethod
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare dataframe"""
        pass


class ITypeDetector(ABC):
    """Contract for type detection operations"""
    
    @abstractmethod
    def detect_and_validate_join_key_types(self, config: Dict[str, Any], df1: pd.DataFrame, df2: pd.DataFrame) -> Dict[str, str]:
        """Detect and validate join key types"""
        pass


class IDataPreparer(ABC):
    """Contract for data preparation operations"""
    
    @abstractmethod
    def prepare_data_frames(self, config: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Prepare two data frames from input files based on configuration"""
        pass 