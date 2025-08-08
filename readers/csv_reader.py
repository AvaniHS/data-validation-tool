import pandas as pd
import os
from typing import Optional
from .reader_contract import IDataReader

class CSVReader(IDataReader):
    def read(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        self._ensure_file_readable(file_path)
        return pd.read_csv(file_path)
    
    def _ensure_file_readable(self, file_path: str) -> None:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"Permission denied: Cannot read file {file_path}")
        
        file_dir = os.path.dirname(file_path)
        if file_dir and not os.access(file_dir, os.R_OK):
            raise PermissionError(f"Permission denied: Cannot access directory {file_dir}") 