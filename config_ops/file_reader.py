"""File reading operations for configuration processing."""

import pandas as pd
import json
import os
from typing import Optional, Dict, Any
from constants import DEFAULT_FILE1_SHEET1, DEFAULT_FILE1_SHEET2, DEFAULT_FILE2_SHEET, DEFAULT_NA_VALUE


class FileReader:
    """Handles file reading operations for configuration processing."""
    
    @staticmethod
    def read_file(file_path: str) -> Dict[str, Any]:
        """Read a JSON configuration file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to read configuration file {file_path}: {str(e)}")
    
    @staticmethod
    def read_dataframe(file_path: str, sheet_name: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Read a dataframe from file."""
        try:
            if file_path.endswith('.csv'):
                return pd.read_csv(file_path)
            else:
                return pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
        except Exception as e:
            return None
    
    @staticmethod
    def get_file_columns(config: Dict[str, Any], file_type: str) -> Optional[set]:
        """Get columns from a file based on config."""
        if file_type == 'file1':
            file_path = config['file1_path']
            sheet_name = config.get('file1_sheet1', DEFAULT_FILE1_SHEET1)
        else:
            if config['number_of_files'] == 2:
                file_path = config.get('file2_path')
                sheet_name = config.get('file2_sheet', DEFAULT_FILE2_SHEET)
            else:
                file_path = config['file1_path']
                sheet_name = config.get('file1_sheet2', DEFAULT_FILE1_SHEET2)
        
        if not file_path or file_path == DEFAULT_NA_VALUE:
            return set()
        
        df = FileReader.read_dataframe(file_path, sheet_name)
        return set(df.columns) if df is not None else None
    
    @staticmethod
    def get_both_file_columns(config: Dict[str, Any]) -> tuple[Optional[set], Optional[set]]:
        """Get columns from both files."""
        file1_columns = FileReader.get_file_columns(config, 'file1')
        file2_columns = FileReader.get_file_columns(config, 'file2')
        return file1_columns, file2_columns 