import os
from typing import Optional, Tuple, TYPE_CHECKING
import pandas as pd

from ..file_types import FileTypeFactory
from validation.input_validator import InputValidator
from services.user_interaction.console import ConsoleUserInputProvider
from ..file_operation_contracts import IFileOperationHandler, FileOperationResult, IErrorHandler, IFileValidator, IRetryExecutor
from .error_handlers import StandardErrorHandler
from validation.file_validators import FileValidator
from .retry_handlers import RetryExecutor
from constants import EXCEL_EXTENSIONS

if TYPE_CHECKING:
    from services.user_interaction.interaction import UserInteraction
else:
    # Import for runtime use
    from services.user_interaction.interaction import UserInteraction


class FileOperationHandler(IFileOperationHandler):
    def __init__(self, 
                 user_interaction: Optional['UserInteraction'] = None,
                 input_validator: InputValidator = None,
                 error_handler: IErrorHandler = None,
                 file_validator: IFileValidator = None,
                 retry_executor: IRetryExecutor = None):
        self.user_interaction = user_interaction or UserInteraction(ConsoleUserInputProvider())
        self.input_validator = input_validator or InputValidator()
        self.error_handler = error_handler or StandardErrorHandler(self.user_interaction)
        self.file_validator = file_validator or FileValidator()
        self.retry_executor = retry_executor or RetryExecutor(self.error_handler, self.file_validator)
    
    def read_file(self, file_path: str, sheet_name: Optional[str] = None) -> FileOperationResult:
        return self.retry_executor.execute_with_retry(
            lambda: self._perform_read(file_path, sheet_name),
            file_path,
            "read"
        )
    
    def write_file(self, df: pd.DataFrame, file_path: str, 
                   sheet_name: Optional[str] = None, append_sheet: bool = False) -> FileOperationResult:
        return self.retry_executor.execute_with_retry(
            lambda: self._perform_write(df, file_path, sheet_name, append_sheet),
            file_path,
            "write to"
        )
    
    def read_two_sheets_from_one_file(self, file_path: str, sheet1: str, sheet2: str) -> FileOperationResult:
        return self.retry_executor.execute_with_retry(
            lambda: self._perform_read_two_sheets(file_path, sheet1, sheet2),
            file_path,
            "read two sheets from"
        )
    
    def _perform_read(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        strategy = FileTypeFactory.create_handler(file_path)
        reader = strategy.get_reader()
        return reader.read(file_path, sheet_name)
    
    def _perform_write(self, df: pd.DataFrame, file_path: str, 
                      sheet_name: Optional[str] = None, append_sheet: bool = False) -> None:
        strategy = FileTypeFactory.create_handler(file_path)
        writer = strategy.get_writer()
        write_params = self._build_write_parameters(file_path, sheet_name, append_sheet)
        writer.write(df, file_path, **write_params)
    
    def _perform_read_two_sheets(self, file_path: str, sheet1: str, sheet2: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        strategy = FileTypeFactory.create_handler(file_path)
        reader = strategy.get_reader()
        df1 = reader.read(file_path, sheet1)
        df2 = reader.read(file_path, sheet2)
        return df1, df2
    
    def _build_write_parameters(self, file_path: str, sheet_name: Optional[str], append_sheet: bool) -> dict:
        params = {}
        
        # Only add sheet_name for Excel files
        if sheet_name and file_path.lower().endswith(tuple(EXCEL_EXTENSIONS)):
            params['sheet_name'] = sheet_name
        
        # Use append mode to preserve other sheets when overwriting a specific sheet
        if os.path.exists(file_path) and file_path.lower().endswith(tuple(EXCEL_EXTENSIONS)):
            params['mode'] = 'a'  # Always use append mode to preserve other sheets
        
        return params 