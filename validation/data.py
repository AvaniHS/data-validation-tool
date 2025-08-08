import pandas as pd
from typing import Dict
import sys
from .schema import ColumnMapper, DataTypeValidator
from constants import EXIT_COMMANDS

class DataComparer:
    def __init__(self, validator=None):
        self.validator = validator or DataTypeValidator()

    def compare(self, df1: pd.DataFrame, df2: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
        mapper = ColumnMapper(column_mapping)
        mapped_df1, mapped_df2 = mapper.map(df1, df2)
        while True:
            valid, incompatible = self.validator.validate(mapped_df1, mapped_df2)
            if valid:
                comparison = mapped_df1.eq(mapped_df2)
                result = mapped_df1.copy()
                for col in comparison.columns:
                    result[col + '_match'] = comparison[col]
                return result
            print("\nError: Incompatible data types detected in the following columns:")
            for col, (dtype1, dtype2) in incompatible.items():
                print(f"  Column '{col}': file1 type = {dtype1}, file2 type = {dtype2}")
            print("\nOptions:")
            print("  1. Edit the files to fix data types, then press Enter to retry with the same files.")
            print("  2. Type 'restart' to re-enter file names and mapping from the beginning.")
            print("  3. Type 'exit' to quit.")
            choice = input("Your choice: ").strip().lower()
            if choice in EXIT_COMMANDS:
                print("Exiting as requested by user.")
                sys.exit(0)
            elif choice == 'restart':
                raise RuntimeError('restart')
            else:
                print("You may now safely edit and save the files. Press Enter when ready to retry.")
                # Re-read the files to pick up changes
                return None  # Signal to main to re-read files and retry 