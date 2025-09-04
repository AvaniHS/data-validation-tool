from typing import Dict, Any, Tuple, Optional, List
import pandas as pd
import os
from services.file_handler import read_file, read_two_sheets_from_one_file
from validation.exceptions import DataPreparationError, FileNotFoundError, InvalidConfigurationError
from validation.type_detector import TypeDetector
from validation.contracts import (
    IDataValidator,
    IDataLoader,
    IDataCleaner,
    ITypeDetector,
    IDataPreparer
)
from constants import DEFAULT_FILE1_SHEET1, DEFAULT_FILE1_SHEET2, DEFAULT_FILE2_SHEET, DEFAULT_NA_VALUE


class DataValidator(IDataValidator):
    
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        required_fields = ['file1_path', 'number_of_files']
        
        for field in required_fields:
            if field not in config:
                raise InvalidConfigurationError(f"Missing required field: {field}")
        
        if not os.path.exists(config['file1_path']):
            raise FileNotFoundError(f"File not found: {config['file1_path']}")
        
        if config['number_of_files'] == 2:
            file2_path = config.get('file2_path')
            if not file2_path:
                raise InvalidConfigurationError("file2_path is required when number_of_files is 2")
            if not os.path.exists(file2_path):
                raise FileNotFoundError(f"File not found: {file2_path}")
    
    def validate_dataframe(self, df: pd.DataFrame, name: str) -> None:
        if df is None:
            raise DataPreparationError(f"{name} dataframe is None")
        
        if df.empty:
            print(f"⚠️  Warning: {name} dataframe is empty")
        
        if len(df.columns) == 0:
            raise DataPreparationError(f"{name} dataframe has no columns")


class DataLoader(IDataLoader):
    
    def load_single_file_two_sheets(self, file_path: str, sheet1: str, sheet2: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        try:
            df1, df2 = read_two_sheets_from_one_file(file_path, sheet1, sheet2)
            return df1, df2
        except Exception as e:
            raise DataPreparationError(f"Failed to load sheets from {file_path}: {str(e)}")
    
    def load_two_separate_files(self, file1_path: str, file2_path: str, sheet1: str, sheet2: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        try:
            df1 = read_file(file1_path, sheet1)
            df2 = read_file(file2_path, sheet2)
            return df1, df2
        except Exception as e:
            raise DataPreparationError(f"Failed to load separate files: {str(e)}")


class DataCleaner(IDataCleaner):
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        df = self._remove_unnamed_columns(df)
        
        df = self._clean_currency_values(df)
        
        df = df.reset_index(drop=True)
        
        return df
    
    def _remove_unnamed_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
        if unnamed_cols:
            df = df.drop(columns=unnamed_cols)
            print(f"✓ Removed {len(unnamed_cols)} unnamed columns")
        return df
    
    def _clean_currency_values(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in df.columns:
            if df[col].dtype == 'object':
                # Only clean columns that contain literal dollar signs
                has_dollar = any('$' in str(val) for val in df[col].values if pd.notna(val))
                if has_dollar:
                    df[col] = df[col].astype(str).str.replace('$', '').str.replace(',', '')
                    try:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    except:
                        pass
        return df


class TypeDetectionService(ITypeDetector):
    
    def detect_and_validate_join_key_types(self, config: Dict[str, Any], df1: pd.DataFrame, df2: pd.DataFrame) -> Dict[str, str]:
        join_keys = config.get('join_keys', {})
        detected_types = {}
        
        for key1, key2 in join_keys.items():
            if key1 in df1.columns and key2 in df2.columns:
                df1_type = self._detect_column_type(df1[key1])
                df2_type = self._detect_column_type(df2[key2])
                
                if df1_type == df2_type:
                    detected_types[key1] = df1_type
                else:
                    detected_types[key1] = 'mixed'
            else:
                detected_types[key1] = 'unknown'
        
        self._update_config_with_detected_types(config, detected_types)
        return detected_types
    
    def _detect_column_type(self, column: pd.Series) -> str:
        if pd.api.types.is_numeric_dtype(column):
            return 'numeric'
        else:
            return 'non_numeric'
    
    def _update_config_with_detected_types(self, config: Dict[str, Any], detected_types: Dict[str, str]) -> None:
        if 'join_keys_types' not in config:
            config['join_keys_types'] = {}
        
        for key, detected_type in detected_types.items():
            if key in config['join_keys_types'] and config['join_keys_types'][key] == 'NA':
                config['join_keys_types'][key] = detected_type


class DataPreparer(IDataPreparer):
    
    def __init__(self):
        self._validator = DataValidator()
        self._loader = DataLoader()
        self._cleaner = DataCleaner()
        self._type_detector = TypeDetectionService()
    
    def prepare_data_frames(self, config: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        self._validator.validate_configuration(config)
        
        if config['number_of_files'] == 1:
            df1, df2 = self._loader.load_single_file_two_sheets(
                config['file1_path'],
                config.get('file1_sheet1', DEFAULT_FILE1_SHEET1),
                config.get('file1_sheet2', DEFAULT_FILE1_SHEET2)
            )
        else:
            df1, df2 = self._loader.load_two_separate_files(
                config['file1_path'],
                config['file2_path'],
                config.get('file1_sheet1', DEFAULT_FILE1_SHEET1),
                config.get('file2_sheet', DEFAULT_FILE2_SHEET)
            )
        
        self._validator.validate_dataframe(df1, "First")
        self._validator.validate_dataframe(df2, "Second")
        
        df1 = self._cleaner.clean_dataframe(df1)
        df2 = self._cleaner.clean_dataframe(df2)
        
        self._type_detector.detect_and_validate_join_key_types(config, df1, df2)
        
        return df1, df2 