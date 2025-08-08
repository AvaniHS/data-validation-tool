"""
Type detection utility for join keys.
Provides functionality to automatically detect data types when join_keys_types is set to "NA".
"""

import pandas as pd
from typing import Dict, Any, List, Tuple
from validation.exceptions import InvalidConfigurationError
from constants import DEFAULT_NA_VALUE


class TypeDetector:
    """Utility class for detecting data types in pandas DataFrames"""
    
    @staticmethod
    def detect_join_key_types(config: Dict[str, Any], df1: pd.DataFrame, df2: pd.DataFrame) -> Dict[str, str]:
        """
        Detect data types for join keys when join_keys_types is "NA"
        
        Args:
            config: Configuration dictionary
            df1: First dataframe
            df2: Second dataframe
            
        Returns:
            Dictionary mapping join keys to their detected types ("numeric" or "non_numeric")
        """
        join_keys = config.get('join_keys', {})
        join_keys_types = config.get('join_keys_types', {})
        
        if not join_keys or join_keys == DEFAULT_NA_VALUE:
            return {}
        
        detected_types = {}
        
        for file1_key, file2_key in join_keys.items():
            # Check if type is already specified
            if join_keys_types and file1_key in join_keys_types:
                if join_keys_types[file1_key] != DEFAULT_NA_VALUE:
                    detected_types[file1_key] = join_keys_types[file1_key]
                    continue
            
            # Detect type from data
            type1 = TypeDetector._detect_column_type(df1, file1_key)
            type2 = TypeDetector._detect_column_type(df2, file2_key)
            
            # Use the more restrictive type (if one is numeric and one is non_numeric, use non_numeric)
            if type1 == 'non_numeric' or type2 == 'non_numeric':
                detected_types[file1_key] = 'non_numeric'
            else:
                detected_types[file1_key] = 'numeric'
        
        return detected_types
    
    @staticmethod
    def _detect_column_type(df: pd.DataFrame, column: str) -> str:
        """
        Detect the type of a specific column in a dataframe
        
        Args:
            df: Dataframe to analyze
            column: Column name to check
            
        Returns:
            "numeric" or "non_numeric"
        """
        if column not in df.columns:
            return 'non_numeric'  # Default to non_numeric if column doesn't exist
        
        # Get the column data
        col_data = df[column]
        
        # Check if it's already numeric
        if pd.api.types.is_numeric_dtype(col_data):
            return 'numeric'
        
        # Try to convert to numeric
        try:
            # Remove common non-numeric characters
            cleaned_data = col_data.astype(str).str.replace('$', '', regex=False)
            cleaned_data = cleaned_data.str.replace(',', '', regex=False)
            cleaned_data = cleaned_data.str.strip()
            
            # Try to convert to numeric
            numeric_data = pd.to_numeric(cleaned_data, errors='coerce')
            
            # Check if most values are numeric (more than 80% are not NaN)
            if numeric_data.notna().sum() / len(numeric_data) > 0.8:
                return 'numeric'
            else:
                return 'non_numeric'
        except:
            return 'non_numeric'
    
    @staticmethod
    def validate_join_key_compatibility(config: Dict[str, Any], df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[bool, Dict[str, str]]:
        """
        Validate that join keys are compatible between dataframes
        
        Args:
            config: Configuration dictionary
            df1: First dataframe
            df2: Second dataframe
            
        Returns:
            Tuple of (is_compatible, detected_types)
        """
        join_keys = config.get('join_keys', {})
        if not join_keys or join_keys == DEFAULT_NA_VALUE:
            return True, {}
        
        detected_types = TypeDetector.detect_join_key_types(config, df1, df2)
        
        # Check for potential issues
        warnings = []
        for file1_key, file2_key in join_keys.items():
            if file1_key not in df1.columns:
                warnings.append(f"Join key '{file1_key}' not found in file1")
            if file2_key not in df2.columns:
                warnings.append(f"Join key '{file2_key}' not found in file2")
            
            # Check for type mismatches
            if file1_key in detected_types and file2_key in detected_types:
                type1 = TypeDetector._detect_column_type(df1, file1_key)
                type2 = TypeDetector._detect_column_type(df2, file2_key)
                
                if type1 != type2:
                    warnings.append(f"Type mismatch for join key '{file1_key}': {type1} vs {type2}")
        
        if warnings:
            print("⚠️  Join key compatibility warnings:")
            for warning in warnings:
                print(f"   {warning}")
        
        return len(warnings) == 0, detected_types 