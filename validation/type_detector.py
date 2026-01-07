import pandas as pd
from typing import Dict, Any, List, Tuple
from validation.exceptions import InvalidConfigurationError
from constants import DEFAULT_NA_VALUE


class TypeDetector:
    
    @staticmethod
    def detect_join_key_types(config: Dict[str, Any], df1: pd.DataFrame, df2: pd.DataFrame) -> Dict[str, str]:
        join_keys = config.get('join_keys', {})
        join_keys_types = config.get('join_keys_types', {})
        
        if not join_keys or join_keys == DEFAULT_NA_VALUE:
            return {}
        
        detected_types = {}
        
        for file1_key, file2_key in join_keys.items():
            if join_keys_types and file1_key in join_keys_types:
                if join_keys_types[file1_key] != DEFAULT_NA_VALUE:
                    detected_types[file1_key] = join_keys_types[file1_key]
                    continue
            
            detected_type1 = TypeDetector._detect_column_type(df1, file1_key)
            detected_type2 = TypeDetector._detect_column_type(df2, file2_key)
            
            if detected_type1 == 'non_numeric' or detected_type2 == 'non_numeric':
                detected_types[file1_key] = 'non_numeric'
            else:
                detected_types[file1_key] = 'numeric'
        
        return detected_types
    
    @staticmethod
    def _detect_column_type(df: pd.DataFrame, column: str) -> str:
        if column not in df.columns:
            return 'non_numeric'
        
        column_data = df[column]
        
        if pd.api.types.is_numeric_dtype(column_data):
            return 'numeric'
        
        try:
            cleaned_column_data = column_data.astype(str).str.replace('$', '', regex=False)
            cleaned_column_data = cleaned_column_data.str.replace(',', '', regex=False)
            cleaned_column_data = cleaned_column_data.str.strip()
            
            numeric_column_data = pd.to_numeric(cleaned_column_data, errors='coerce')
            
            if numeric_column_data.notna().sum() / len(numeric_column_data) > 0.8:
                return 'numeric'
            else:
                return 'non_numeric'
        except:
            return 'non_numeric'
    
    @staticmethod
    def validate_join_key_compatibility(config: Dict[str, Any], df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[bool, Dict[str, str]]:
        join_keys = config.get('join_keys', {})
        if not join_keys or join_keys == DEFAULT_NA_VALUE:
            return True, {}
        
        detected_types = TypeDetector.detect_join_key_types(config, df1, df2)
        
        compatibility_warnings = []
        for file1_key, file2_key in join_keys.items():
            if file1_key not in df1.columns:
                compatibility_warnings.append(f"Join key '{file1_key}' not found in file1")
            if file2_key not in df2.columns:
                compatibility_warnings.append(f"Join key '{file2_key}' not found in file2")
            
            if file1_key in detected_types and file2_key in detected_types:
                detected_type1 = TypeDetector._detect_column_type(df1, file1_key)
                detected_type2 = TypeDetector._detect_column_type(df2, file2_key)
                
                if detected_type1 != detected_type2:
                    compatibility_warnings.append(f"Type mismatch for join key '{file1_key}': {detected_type1} vs {detected_type2}")
        
        if compatibility_warnings:
            print("⚠️  Join key compatibility warnings:")
            for warning in compatibility_warnings:
                print(f"   {warning}")
        
        return len(compatibility_warnings) == 0, detected_types 