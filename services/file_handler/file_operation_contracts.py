from abc import ABC, abstractmethod
from typing import Optional, Protocol
import pandas as pd


# ============================================================================
# LOW-LEVEL FILE OPERATION CONTRACTS
# ============================================================================

class FileReader(Protocol):
    """Contract for low-level file reading operations"""
    def read(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        ...


class FileWriter(Protocol):
    """Contract for low-level file writing operations"""
    def write(self, df: pd.DataFrame, file_path: str, **kwargs) -> None:
        ...


class FileTypeStrategy(ABC):
    """Contract for file type strategy that provides readers and writers"""
    @abstractmethod
    def get_reader(self) -> FileReader:
        pass
    
    @abstractmethod
    def get_writer(self) -> FileWriter:
        pass
    
    @abstractmethod
    def supports_sheets(self) -> bool:
        pass


# ============================================================================
# HIGH-LEVEL FILE OPERATION CONTRACTS
# ============================================================================

class FileOperationResult:
    """Result wrapper for file operations"""
    def __init__(self, success: bool, data=None, error_message: str = None):
        self.success = success
        self.data = data
        self.error_message = error_message


class IFileOperationHandler(ABC):
    """Contract for high-level file operation orchestration"""
    @abstractmethod
    def read_file(self, file_path: str, sheet_name: Optional[str] = None) -> FileOperationResult:
        pass
    
    @abstractmethod
    def write_file(self, df: pd.DataFrame, file_path: str, 
                   sheet_name: Optional[str] = None, append_sheet: bool = False) -> FileOperationResult:
        pass
    
    @abstractmethod
    def read_two_sheets_from_one_file(self, file_path: str, sheet1: str, sheet2: str) -> FileOperationResult:
        pass


class IErrorHandler(Protocol):
    """Contract for error handling during file operations"""
    def handle_error(self, error: Exception, file_path: str, operation: str) -> str:
        ...


class IFileValidator(Protocol):
    """Contract for file validation during operations"""
    def validate_file_operation(self, file_path: str, sheet_name: Optional[str] = None) -> None:
        ...


class IRetryExecutor(Protocol):
    """Contract for retry execution during file operations"""
    def execute_with_retry(self, operation_func, file_path: str, operation_name: str) -> FileOperationResult:
        ... 