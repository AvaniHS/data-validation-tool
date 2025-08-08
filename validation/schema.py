import pandas as pd
from typing import Dict, Tuple
import sys
import json
from constants import EXIT_COMMANDS

class DataTypeValidator:
    def validate(self, df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[bool, Dict[str, Tuple[str, str]]]:
        incompatible = {}
        for col in df1.columns:
            dtype1 = str(df1[col].dtype)
            dtype2 = str(df2[col].dtype)
            # Consider 'object' as string, but flag if one is numeric and the other is not
            if dtype1 != dtype2:
                if not (('object' in dtype1 and 'object' in dtype2) or ('int' in dtype1 and 'float' in dtype2) or ('float' in dtype1 and 'int' in dtype2)):
                    incompatible[col] = (dtype1, dtype2)
        return (len(incompatible) == 0), incompatible

class ColumnMapper:
    def __init__(self, column_mapping: Dict[str, str]):
        self.column_mapping = column_mapping

    def map(self, df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        while True:
            missing1 = [col for col in self.column_mapping.keys() if col not in df1.columns]
            missing2 = [col for col in self.column_mapping.values() if col not in df2.columns]
            if not missing1 and not missing2:
                mapped_df1 = df1[list(self.column_mapping.keys())].copy()
                mapped_df2 = df2[list(self.column_mapping.values())].copy()
                mapped_df2.columns = list(self.column_mapping.keys())
                # Check for empty dataframes
                if mapped_df1.empty or mapped_df2.empty:
                    print("\nError: No data to compare after mapping columns. One or both files/sheets are empty after filtering.")
                    print(f"  Rows in file 1 after mapping: {len(mapped_df1)}")
                    print(f"  Rows in file 2 after mapping: {len(mapped_df2)}")
                    print("\nOptions:")
                    print("  1. Type 'restart' to re-enter file names and mapping from the beginning.")
                    print("  2. Type 'exit' to quit.")
                    choice = input("Your choice: ").strip().lower()
                    if choice in EXIT_COMMANDS:
                        print("Exiting as requested by user.")
                        sys.exit(0)
                    elif choice == 'restart':
                        raise RuntimeError('restart')
                    else:
                        print("Invalid choice. Please type 'restart' or 'exit'.")
                        continue
                return mapped_df1, mapped_df2
            print("\nError: Column mapping refers to columns not found in the input files.")
            if missing1:
                print(f"  Missing in file 1: {', '.join(missing1)}")
                print(f"  Available columns in file 1: {', '.join(df1.columns)}")
            if missing2:
                print(f"  Missing in file 2: {', '.join(missing2)}")
                print(f"  Available columns in file 2: {', '.join(df2.columns)}")
            new_mapping = input("Enter a valid column mapping as JSON (or type 'exit' to quit): ")
            if new_mapping.strip().lower() in EXIT_COMMANDS:
                print("Exiting as requested by user.")
                sys.exit(0)
            try:
                self.column_mapping = json.loads(new_mapping)
                if not isinstance(self.column_mapping, dict):
                    raise ValueError
            except Exception:
                print("Invalid JSON. Please try again.") 