"""
Data preparation module for loading and preparing data frames from input files.
Follows OOP, SOLID principles, and separation of concerns.
"""

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
    """Concrete implementation of data validation"""
    
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validate configuration parameters"""
        required_fields = ['file1_path', 'number_of_files']
        
        for field in required_fields:
            if field not in config:
                raise InvalidConfigurationError(f"Missing required field: {field}")
        
        # Validate file paths
        if not os.path.exists(config['file1_path']):
            raise FileNotFoundError(f"File not found: {config['file1_path']}")
        
        if config['number_of_files'] == 2:
            file2_path = config.get('file2_path')
            if not file2_path:
                raise InvalidConfigurationError("file2_path is required when number_of_files is 2")
            if not os.path.exists(file2_path):
                raise FileNotFoundError(f"File not found: {file2_path}")
    
    def validate_dataframe(self, df: pd.DataFrame, name: str) -> None:
        """Validate dataframe structure and content"""
        if df is None:
            raise DataPreparationError(f"{name} dataframe is None")
        
        if df.empty:
            print(f"⚠️  Warning: {name} dataframe is empty")
        
        if len(df.columns) == 0:
            raise DataPreparationError(f"{name} dataframe has no columns")


class DataLoader(IDataLoader):
    """Concrete implementation of data loading"""
    
    def load_single_file_two_sheets(self, file_path: str, sheet1: str, sheet2: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load two sheets from a single file"""
        try:
            df1, df2 = read_two_sheets_from_one_file(file_path, sheet1, sheet2)
            return df1, df2
        except Exception as e:
            raise DataPreparationError(f"Failed to load sheets from {file_path}: {str(e)}")
    
    def load_two_separate_files(self, file1_path: str, file2_path: str, sheet1: str, sheet2: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load data from two separate files"""
        try:
            df1 = read_file(file1_path, sheet1)
            df2 = read_file(file2_path, sheet2)
            return df1, df2
        except Exception as e:
            raise DataPreparationError(f"Failed to load separate files: {str(e)}")


class DataCleaner(IDataCleaner):
    """Concrete implementation of data cleaning"""
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare dataframe"""
        df = df.copy()
        
        # Remove unnamed columns
        df = self._remove_unnamed_columns(df)
        
        # Clean currency values
        df = self._clean_currency_values(df)
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def _remove_unnamed_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove unnamed columns from dataframe"""
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
        if unnamed_cols:
            df = df.drop(columns=unnamed_cols)
            print(f"✓ Removed {len(unnamed_cols)} unnamed columns")
        return df
    
    def _clean_currency_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean currency values in dataframe"""
        for col in df.columns:
            if df[col].dtype == 'object':
                # Remove currency symbols and convert to numeric
                df[col] = df[col].astype(str).str.replace(r'[$,€£¥₹]', '', regex=True)
                df[col] = df[col].str.replace(',', '', regex=False)
                
                # Try to convert to numeric
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    # Keep original value if conversion fails
                    pass
        
        return df


class TypeDetectionService(ITypeDetector):
    """Concrete implementation of type detection"""
    
    def detect_and_validate_join_key_types(self, config: Dict[str, Any], df1: pd.DataFrame, df2: pd.DataFrame) -> Dict[str, str]:
        """Detect and validate join key types"""
        try:
            # Detect types using TypeDetector
            detected_types = TypeDetector.detect_join_key_types(config, df1, df2)
            
            # Validate compatibility
            is_compatible, _ = TypeDetector.validate_join_key_compatibility(config, df1, df2)
            
            if not is_compatible:
                print("⚠️  Warning: Some join key compatibility issues detected")
            
            # Update config with detected types
            self._update_config_with_detected_types(config, detected_types)
            
            return detected_types
            
        except Exception as e:
            print(f"⚠️  Warning: Failed to detect join key types: {str(e)}")
            return {}
    
    def _update_config_with_detected_types(self, config: Dict[str, Any], detected_types: Dict[str, str]) -> None:
        """Update configuration with detected types"""
        join_keys_types = config.get('join_keys_types', {})
        
        if join_keys_types == DEFAULT_NA_VALUE or not join_keys_types:
            config['join_keys_types'] = detected_types
            print(f"✓ Auto-detected join key types: {detected_types}")
        else:
            # Fill in any "NA" values with detected types
            updated_types = join_keys_types.copy()
            for key, detected_type in detected_types.items():
                if key in updated_types and updated_types[key] == DEFAULT_NA_VALUE:
                    updated_types[key] = detected_type
                    print(f"✓ Auto-detected type for '{key}': {detected_type}")
            
            config['join_keys_types'] = updated_types


class DataPreparer(IDataPreparer):
    """Concrete implementation of data preparation"""
    
    def __init__(self):
        self._validator = DataValidator()
        self._loader = DataLoader()
        self._cleaner = DataCleaner()
        self._type_detector = TypeDetectionService()
    
    def prepare_data_frames(self, config: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Prepare two data frames from input files based on configuration
        
        Args:
            config: Configuration dictionary containing file paths and settings
            
        Returns:
            Tuple of (dataframe1, dataframe2) loaded from input files
            
        Raises:
            DataPreparationError: If data loading fails
            InvalidConfigurationError: If configuration is invalid
            FileNotFoundError: If input files are not found
        """
        try:
            # Validate configuration
            self._validator.validate_configuration(config)
            
            # Extract configuration parameters
            file1_path = config['file1_path']
            file2_path = config.get('file2_path')
            file1_sheet1 = config.get('file1_sheet1', DEFAULT_FILE1_SHEET1)
            file1_sheet2 = config.get('file1_sheet2', DEFAULT_FILE1_SHEET2)
            file2_sheet = config.get('file2_sheet', DEFAULT_FILE2_SHEET)
            number_of_files = config['number_of_files']
            
            # Load data based on configuration
            if number_of_files == 1:
                df1, df2 = self._loader.load_single_file_two_sheets(file1_path, file1_sheet1, file1_sheet2)
            else:
                df1, df2 = self._loader.load_two_separate_files(file1_path, file2_path, file1_sheet1, file2_sheet)
            
            # Validate loaded dataframes
            self._validator.validate_dataframe(df1, "First")
            self._validator.validate_dataframe(df2, "Second")
            
            # Clean dataframes
            df1 = self._cleaner.clean_dataframe(df1)
            df2 = self._cleaner.clean_dataframe(df2)
            
            # Detect and validate join key types
            self._type_detector.detect_and_validate_join_key_types(config, df1, df2)
            
            print(f"✓ Data preparation completed successfully")
            print(f"  DataFrame 1: {df1.shape[0]} rows, {df1.shape[1]} columns")
            print(f"  DataFrame 2: {df2.shape[0]} rows, {df2.shape[1]} columns")
            
            return df1, df2
                
        except (InvalidConfigurationError, FileNotFoundError):
            raise
        except Exception as e:
            raise DataPreparationError(f"Failed to prepare data frames: {str(e)}") 