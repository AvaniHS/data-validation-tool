import pandas as pd
from typing import Dict, Tuple
import sys
import json
from constants import EXIT_COMMANDS

class DataTypeValidator:
    def validate(self, df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[bool, Dict[str, Tuple[str, str]]]:
        incompatible_columns = {}
        for column in df1.columns:
            data_type1 = str(df1[column].dtype)
            data_type2 = str(df2[column].dtype)
            if data_type1 != data_type2:
                if not (('object' in data_type1 and 'object' in data_type2) or ('int' in data_type1 and 'float' in data_type2) or ('float' in data_type1 and 'int' in data_type2)):
                    incompatible_columns[column] = (data_type1, data_type2)
        return (len(incompatible_columns) == 0), incompatible_columns

class ColumnMapper:
    def __init__(self, column_mapping: Dict[str, str]):
        self.column_mapping = column_mapping

    def map(self, df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        while True:
            missing_columns_file1 = [col for col in self.column_mapping.keys() if col not in df1.columns]
            missing_columns_file2 = [col for col in self.column_mapping.values() if col not in df2.columns]
            if not missing_columns_file1 and not missing_columns_file2:
                mapped_dataframe1 = df1[list(self.column_mapping.keys())].copy()
                mapped_dataframe2 = df2[list(self.column_mapping.values())].copy()
                mapped_dataframe2.columns = list(self.column_mapping.keys())
                
                if mapped_dataframe1.empty or mapped_dataframe2.empty:
                    print("\nError: No data to compare after mapping columns. One or both files/sheets are empty after filtering.")
                    print(f"  Rows in file 1 after mapping: {len(mapped_dataframe1)}")
                    print(f"  Rows in file 2 after mapping: {len(mapped_dataframe2)}")
                    print("\nOptions:")
                    print("  1. Type 'restart' to re-enter file names and mapping from the beginning.")
                    print("  2. Type 'exit' to quit.")
                    user_choice = input("Your choice: ").strip().lower()
                    if user_choice in EXIT_COMMANDS:
                        print("Exiting as requested by user.")
                        sys.exit(0)
                    elif user_choice == 'restart':
                        raise RuntimeError('restart')
                    else:
                        print("Invalid choice. Please type 'restart' or 'exit'.")
                        continue
                return mapped_dataframe1, mapped_dataframe2
            print("\nError: Column mapping refers to columns not found in the input files.")
            if missing_columns_file1:
                print(f"  Missing in file 1: {', '.join(missing_columns_file1)}")
                print(f"  Available columns in file 1: {', '.join(df1.columns)}")
            if missing_columns_file2:
                print(f"  Missing in file 2: {', '.join(missing_columns_file2)}")
                print(f"  Available columns in file 2: {', '.join(df2.columns)}")
            new_mapping_input = input("Enter a valid column mapping as JSON (or type 'exit' to quit): ")
            if new_mapping_input.strip().lower() in EXIT_COMMANDS:
                print("Exiting as requested by user.")
                sys.exit(0)
            try:
                self.column_mapping = json.loads(new_mapping_input)
                if not isinstance(self.column_mapping, dict):
                    raise ValueError
            except Exception:
                print("Invalid JSON. Please try again.") 