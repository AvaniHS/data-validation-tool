from typing import Optional, Tuple
import pandas as pd

from ..file_operation_contracts import (
    IFileOperationHandler,
    IErrorHandler,
    IFileValidator,
    IRetryExecutor,
    FileOperationResult
)

from validation.exceptions import (
    FileOperationError,
    FileValidationError
)

from .error_handlers import (
    StandardErrorHandler,
    SilentErrorHandler,
    RetryErrorHandler
)

from validation.file_validators import (
    FileValidator,
    StrictFileValidator,
    PermissiveFileValidator
)

from .retry_handlers import (
    RetryExecutor,
    NoRetryExecutor
)

from .operation_handler import FileOperationHandler
from .file_handler_wrapper import FileHandler

def read_file(file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
    handler = FileOperationHandler()
    result = handler.read_file(file_path, sheet_name)
    if not result.success:
        raise FileOperationError(result.error_message)
    return result.data


def write_file(df: pd.DataFrame, file_path: str, sheet_name: Optional[str] = None, append_sheet: bool = False) -> None:
    handler = FileOperationHandler()
    result = handler.write_file(df, file_path, sheet_name, append_sheet)
    if not result.success:
        raise FileOperationError(result.error_message)
    return result.data


def read_two_sheets_from_one_file(file_path: str, sheet1: str, sheet2: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    handler = FileOperationHandler()
    result = handler.read_two_sheets_from_one_file(file_path, sheet1, sheet2)
    if not result.success:
        raise FileOperationError(result.error_message)
    return result.data

__all__ = [
    'IFileOperationHandler',
    'IErrorHandler', 
    'IFileValidator',
    'IRetryExecutor',
    'FileOperationResult',
    'FileOperationError',
    'FileValidationError',
    'StandardErrorHandler',
    'SilentErrorHandler',
    'RetryErrorHandler',
    'FileValidator',
    'StrictFileValidator',
    'PermissiveFileValidator',
    'RetryExecutor',
    'NoRetryExecutor',
    'FileOperationHandler',
    'FileHandler',
    'read_file',
    'write_file',
    'read_two_sheets_from_one_file'
] 