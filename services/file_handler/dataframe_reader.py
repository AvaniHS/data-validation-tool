import pandas as pd
import json
import os
from typing import Optional
from constants import CSV_EXTENSION, JSON_EXTENSION, EXCEL_EXTENSIONS
from services.logging.logger_service import get_logger


class DataFrameReader:
    
    def __init__(self):
        self.logger = get_logger("dataframe_reader")
    
    def read_dataframe(self, file_path: str, sheet_name: Optional[str] = None) -> Optional[pd.DataFrame]:
        self.logger.debug(f"Reading DataFrame from: {file_path}")
        
        try:
            if file_path.endswith(CSV_EXTENSION):
                return self._read_csv(file_path)
            elif file_path.endswith(JSON_EXTENSION):
                return self._read_json(file_path)
            elif any(file_path.endswith(ext) for ext in EXCEL_EXTENSIONS):
                return self._read_excel(file_path, sheet_name)
            else:
                error_msg = f"Unsupported file format: {file_path}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
                
        except Exception as e:
            self.logger.error(f"Error reading file '{file_path}': {str(e)}", e)
            raise
    
    def _read_csv(self, file_path: str) -> pd.DataFrame:
        self.logger.debug(f"Reading CSV file: {file_path}")
        df = pd.read_csv(file_path)
        self.logger.info(f"Successfully read CSV: {df.shape[0]} rows × {df.shape[1]} columns")
        return df
    
    def _read_json(self, file_path: str) -> pd.DataFrame:
        self.logger.debug(f"Reading JSON file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        
        if isinstance(json_data, list):
            df = pd.DataFrame(json_data)
            self.logger.debug("Processed JSON as list of objects")
        elif isinstance(json_data, dict):
            if 'data' in json_data and isinstance(json_data['data'], list):
                if 'columns' in json_data:
                    df = pd.DataFrame(json_data['data'], columns=json_data['columns'])
                    self.logger.debug("Processed structured JSON with data and columns")
                else:
                    df = pd.DataFrame(json_data['data'])
                    self.logger.debug("Processed structured JSON with data only")
            else:
                df = pd.DataFrame([json_data])
                self.logger.debug("Processed JSON as single object")
        else:
            error_msg = f"Unsupported JSON structure in {file_path}. Expected list or dict."
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.info(f"Successfully read JSON: {df.shape[0]} rows × {df.shape[1]} columns")
        return df
    
    def _read_excel(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        self.logger.debug(f"Reading Excel file: {file_path}, sheet: {sheet_name or 'default'}")
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
        self.logger.info(f"Successfully read Excel: {df.shape[0]} rows × {df.shape[1]} columns")
        return df
    
    def get_file_columns(self, file_path: str, sheet_name: Optional[str] = None) -> Optional[set]:
        try:
            df = self.read_dataframe(file_path, sheet_name)
            if df is not None:
                columns = set(df.columns)
                self.logger.debug(f"Retrieved {len(columns)} columns from {file_path}")
                return columns
            return None
        except Exception as e:
            self.logger.error(f"Failed to get columns from {file_path}: {str(e)}", e)
            return None
    
    def validate_file_readable(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return False
        
        if not os.access(file_path, os.R_OK):
            self.logger.error(f"File not readable: {file_path}")
            return False
        
        return True


dataframe_reader = DataFrameReader()
