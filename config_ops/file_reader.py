"""File reading operations for configuration processing."""

import json
import pandas as pd
from typing import Optional, Dict, Any
from constants import DEFAULT_FILE1_SHEET1, DEFAULT_FILE1_SHEET2, DEFAULT_FILE2_SHEET, DEFAULT_NA_VALUE
from services.file_handler.dataframe_reader import dataframe_reader


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
        
        df = dataframe_reader.read_dataframe(file_path, sheet_name)
        return set(df.columns) if df is not None else None
    
    @staticmethod
    def get_both_file_columns(config: Dict[str, Any]) -> tuple[Optional[set], Optional[set]]:
        """Get columns from both files."""
        file1_columns = FileReader.get_file_columns(config, 'file1')
        file2_columns = FileReader.get_file_columns(config, 'file2')
        return file1_columns, file2_columns 