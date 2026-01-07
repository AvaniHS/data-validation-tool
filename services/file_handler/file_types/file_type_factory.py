import os
from typing import Dict, Type
from .csv_handler import CSVHandler
from .excel_handler import ExcelHandler
from .json_handler import JSONHandler
from constants import CSV_EXTENSION, JSON_EXTENSION, EXCEL_EXTENSIONS


class FileTypeFactory:
    
    _handlers: Dict[str, Type] = {
        CSV_EXTENSION: CSVHandler,
        JSON_EXTENSION: JSONHandler,
        EXCEL_EXTENSIONS[0]: ExcelHandler,
        EXCEL_EXTENSIONS[1]: ExcelHandler
    }
    
    @classmethod
    def create_handler(cls, file_path: str):
        _, ext = os.path.splitext(file_path)
        
        if ext not in cls._handlers:
            raise ValueError(f"Unsupported file extension: {ext}")
        
        return cls._handlers[ext]() 