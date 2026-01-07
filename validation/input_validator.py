import os
from typing import List, Tuple, Dict, Any
import pandas as pd
import json
from config_ops.Validation.config_validator import ConfigValidator
from config_ops.config_enricher import ConfigEnricher
from constants import SUPPORTED_EXTENSIONS, VALID_AGGREGATION_TYPES


class InputValidator:
    
    @staticmethod
    def is_supported_filetype(path: str) -> bool:
        return any(path.lower().endswith(extension) for extension in SUPPORTED_EXTENSIONS)
    
    @staticmethod
    def validate_file_path(file_path: str, required: bool = True) -> str:
        if not file_path and not required:
            return None
            
        if file_path and os.path.exists(file_path):
            return file_path
        else:
            if required:
                raise ValueError(f"File not found: {file_path}")
            return None
    
    @staticmethod
    def validate_configuration_file(config_file_path: str) -> Dict[str, Any]:
        return ConfigValidator.validate_config_file(config_file_path)
    
    @staticmethod
    def extract_file_paths_from_config(config: Dict[str, Any]) -> Tuple[str, str]:
        return ConfigEnricher.extract_file_paths(config)
    
    @staticmethod
    def validate_json_mapping(mapping_input: str) -> Dict[str, str]:
        try:
            parsed_mapping = json.loads(mapping_input)
            
            if isinstance(parsed_mapping, dict):
                return parsed_mapping
            else:
                raise ValueError("Mapping must be a JSON object (dictionary).")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format. Please enter a valid JSON mapping.")
    
    @staticmethod
    def validate_column_selection(column_numbers: List[int], available_columns: List[str]) -> List[str]:
        if not all(1 <= number <= len(available_columns) for number in column_numbers):
            raise ValueError("Invalid column numbers. Please enter valid numbers.")
        
        return [available_columns[number - 1] for number in column_numbers]
    
    @staticmethod
    def validate_dataframe_compatibility(df1: pd.DataFrame, df2: pd.DataFrame, 
                                       column_mapping: Dict[str, str]) -> bool:
        missing_columns_in_df1 = [column for column in column_mapping.keys() if column not in df1.columns]
        missing_columns_in_df2 = [column for column in column_mapping.values() if column not in df2.columns]
        
        if missing_columns_in_df1 or missing_columns_in_df2:
            return False
        
        return True 