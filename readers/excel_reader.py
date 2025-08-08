import pandas as pd
import os
from typing import Optional
import sys
from .reader_contract import IDataReader
from constants import DEFAULT_FILE1_SHEET1, EXIT_COMMANDS

class ExcelReader(IDataReader):
    def read(self, file_path: str, sheet_name: str = None) -> pd.DataFrame:
        self._ensure_file_readable(file_path)
        
        if sheet_name is None:
            sheet_name = DEFAULT_FILE1_SHEET1
        
        try:
            return pd.read_excel(file_path, sheet_name=sheet_name)
        except ValueError as e:
            if "Worksheet named" in str(e) and "not found" in str(e):
                print(f"Available sheets in '{file_path}':")
                try:
                    xls = pd.ExcelFile(file_path)
                    for i, sheet in enumerate(xls.sheet_names, 1):
                        print(f"  {i}. {sheet}")
                    
                    while True:
                        new_sheet = input("Enter a valid sheet name from the above list (or type 'exit' to quit): ")
                        if new_sheet.strip().lower() in EXIT_COMMANDS:
                            print("Exiting as requested by user.")
                            exit(0)
                        
                        if new_sheet in xls.sheet_names:
                            return pd.read_excel(file_path, sheet_name=new_sheet)
                        else:
                            print(f"Sheet '{new_sheet}' not found. Please choose from the list above.")
                except Exception as e2:
                    raise ValueError(f"Error reading Excel file '{file_path}': {str(e2)}")
            else:
                raise ValueError(f"Error reading Excel file '{file_path}': {str(e)}")
        except Exception as e:
            raise ValueError(f"Error reading Excel file '{file_path}': {str(e)}")
    
    def _ensure_file_readable(self, file_path: str) -> None:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"Permission denied: Cannot read file {file_path}")
        
        file_dir = os.path.dirname(file_path)
        if file_dir and not os.access(file_dir, os.R_OK):
            raise PermissionError(f"Permission denied: Cannot access directory {file_dir}") 