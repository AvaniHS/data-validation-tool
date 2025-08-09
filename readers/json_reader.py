import pandas as pd
import json
import os
from typing import Optional
from .reader_contract import IDataReader
from services.logging.logger_service import get_logger


class JSONReader(IDataReader):
    """Reader for JSON files that converts JSON data to pandas DataFrame"""
    
    def __init__(self):
        self.logger = get_logger("json_reader")
    
    def read(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Read JSON file and convert to DataFrame
        
        Args:
            file_path: Path to the JSON file
            sheet_name: Not applicable for JSON files, included for interface consistency
            
        Returns:
            pd.DataFrame: DataFrame containing the JSON data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file is not readable
            ValueError: If JSON is malformed or cannot be converted to DataFrame
        """
        self.logger.log_operation_start("read_json_file", {"file_path": file_path})
        
        try:
            self._ensure_file_readable(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
            
            self.logger.debug(f"JSON data type: {type(json_data)}")
            
            # Convert JSON to DataFrame
            if isinstance(json_data, list):
                # If it's a list of objects, each object becomes a row
                df = pd.DataFrame(json_data)
                self.logger.debug("Processed JSON as list of objects")
            elif isinstance(json_data, dict):
                # If it's a single object, treat it as one row
                # Or if it has a structure like {"data": [...], "columns": [...]}
                if 'data' in json_data and isinstance(json_data['data'], list):
                    # Handle structured JSON with data and possibly columns
                    if 'columns' in json_data:
                        df = pd.DataFrame(json_data['data'], columns=json_data['columns'])
                        self.logger.debug("Processed structured JSON with data and columns")
                    else:
                        df = pd.DataFrame(json_data['data'])
                        self.logger.debug("Processed structured JSON with data only")
                else:
                    # Single object - convert to single row DataFrame
                    df = pd.DataFrame([json_data])
                    self.logger.debug("Processed JSON as single object")
            else:
                error_msg = f"Unsupported JSON structure in {file_path}. Expected list or dict."
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            
            self.logger.log_dataframe_info("JSON file read", df, file_path)
            self.logger.log_operation_success("read_json_file")
            return df
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format in {file_path}: {str(e)}"
            self.logger.error(error_msg, e)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error reading JSON file {file_path}: {str(e)}"
            self.logger.error(error_msg, e)
            raise ValueError(error_msg)
    
    def _ensure_file_readable(self, file_path: str) -> None:
        """Validate that the file exists and is readable"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"Permission denied: Cannot read file {file_path}")
        
        file_dir = os.path.dirname(file_path)
        if file_dir and not os.access(file_dir, os.R_OK):
            raise PermissionError(f"Permission denied: Cannot access directory {file_dir}")
