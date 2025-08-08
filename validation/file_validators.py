import os
from typing import Optional
from services.file_handler.file_types import FileTypeFactory
from .exceptions import FileValidationError


class FileValidator:
    def validate_file_operation(self, file_path: str, sheet_name: Optional[str] = None) -> None:
        strategy = FileTypeFactory.create_handler(file_path)
        
        if not strategy.supports_sheets() and sheet_name:
            raise FileValidationError("CSV files do not support sheet names")


class StrictFileValidator:
    def validate_file_operation(self, file_path: str, sheet_name: Optional[str] = None) -> None:
        if not os.path.exists(file_path):
            raise FileValidationError(f"File does not exist: {file_path}")
        
        if not os.path.isfile(file_path):
            raise FileValidationError(f"Path is not a file: {file_path}")
        
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise FileValidationError(f"File is empty: {file_path}")
        
        strategy = FileTypeFactory.create_handler(file_path)
        
        if not strategy.supports_sheets() and sheet_name:
            raise FileValidationError("CSV files do not support sheet names")


class PermissiveFileValidator:
    def validate_file_operation(self, file_path: str, sheet_name: Optional[str] = None) -> None:
        try:
            strategy = FileTypeFactory.create_handler(file_path)
            
            if not strategy.supports_sheets() and sheet_name:
                raise FileValidationError("CSV files do not support sheet names")
        except ValueError as e:
            raise FileValidationError(f"Unsupported file type: {e}") 