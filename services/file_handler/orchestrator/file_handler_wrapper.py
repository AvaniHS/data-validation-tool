from typing import Optional, Tuple
import pandas as pd

from ..file_operation_contracts import IFileOperationHandler, FileOperationResult
from .operation_handler import FileOperationHandler
from validation.exceptions import FileOperationError


class FileHandler:
    def __init__(self, handler: IFileOperationHandler = None):
        self._handler = handler or FileOperationHandler()
    
    def read_file(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        result = self._handler.read_file(file_path, sheet_name)
        if not result.success:
            raise FileOperationError(result.error_message)
        return result.data
    
    def write_file(self, df: pd.DataFrame, file_path: str, sheet_name: Optional[str] = None, append_sheet: bool = False) -> None:
        result = self._handler.write_file(df, file_path, sheet_name, append_sheet)
        if not result.success:
            raise FileOperationError(result.error_message)
        return result.data
    
    def read_two_sheets_from_one_file(self, file_path: str, sheet1: str, sheet2: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        result = self._handler.read_two_sheets_from_one_file(file_path, sheet1, sheet2)
        if not result.success:
            raise FileOperationError(result.error_message)
        return result.data 