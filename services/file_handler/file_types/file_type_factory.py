import os
from typing import Dict, Type
from .csv_handler import CSVHandler
from .excel_handler import ExcelHandler
from constants import CSV_EXTENSION, EXCEL_EXTENSIONS


class FileTypeFactory:
    """Factory for creating file handlers based on file extension"""
    
    _handlers: Dict[str, Type] = {
        CSV_EXTENSION: CSVHandler,
        EXCEL_EXTENSIONS[0]: ExcelHandler,  # .xlsx
        EXCEL_EXTENSIONS[1]: ExcelHandler   # .xls
    }
    
    @classmethod
    def create_handler(cls, file_path: str):
        """Create appropriate handler based on file extension"""
        _, ext = os.path.splitext(file_path)
        
        if ext not in cls._handlers:
            raise ValueError(f"Unsupported file extension: {ext}")
        
        return cls._handlers[ext]() 