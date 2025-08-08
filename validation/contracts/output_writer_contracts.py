"""
Output writer contracts.
Separated from implementations to follow proper design principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd


class IOutputConfigValidator(ABC):
    """Contract for output configuration validation"""
    
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validate output configuration"""
        pass


class IOutputConfigExtractor(ABC):
    """Contract for output configuration extraction"""
    
    @abstractmethod
    def extract_output_settings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract output settings from configuration"""
        pass


class IDataFormatter(ABC):
    """Contract for data formatting operations"""
    
    @abstractmethod
    def format_dataframe(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Format dataframe for output"""
        pass


class IFileWriter(ABC):
    """Contract for file writing operations"""
    
    @abstractmethod
    def write_file(self, df: pd.DataFrame, output_path: str, output_sheet: str) -> None:
        """Write dataframe to file"""
        pass


class IOutputResultValidator(ABC):
    """Contract for output result validation"""
    
    @abstractmethod
    def validate_result(self, df: pd.DataFrame, output_path: str) -> None:
        """Validate output result"""
        pass


class IOutputWriter(ABC):
    """Contract for output writing operations"""
    
    @abstractmethod
    def write_output(self, df: pd.DataFrame, config: Dict[str, Any]) -> None:
        """Write dataframe to output file based on configuration"""
        pass