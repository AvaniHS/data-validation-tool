import pandas as pd
import os
import sys
from constants import EXIT_COMMANDS, USER_CHOICE_OVERWRITE, USER_CHOICE_RENAME

class CSVFileWriter:
    def write(self, df: pd.DataFrame, file_path: str, **kwargs):
        self._ensure_file_writable(file_path)
        
        if os.path.exists(file_path):
            while True:
                print(f"Warning: File '{file_path}' already exists.")
                choice = input("Type 'o' to overwrite, 'r' to enter a new file name, or 'exit' to quit: ").strip().lower()
                if choice == USER_CHOICE_OVERWRITE:
                    break
                elif choice == USER_CHOICE_RENAME:
                    new_file = input("Enter a new file name (including path): ").strip()
                    if new_file and not os.path.exists(new_file):
                        file_path = new_file
                        break
                    elif new_file:
                        print(f"File '{new_file}' already exists. Please choose another name.")
                elif choice in EXIT_COMMANDS:
                    print("Exiting as requested by user.")
                    sys.exit(0)
                else:
                    print("Invalid choice. Please enter 'o', 'r', or 'exit'.")
        df.to_csv(file_path, index=False)
    
    def _ensure_file_writable(self, file_path: str) -> None:
        if os.path.exists(file_path):
            if not os.access(file_path, os.W_OK):
                raise PermissionError(f"Permission denied: Cannot write to file {file_path}")
        
        file_dir = os.path.dirname(file_path)
        if file_dir and not os.access(file_dir, os.W_OK):
            raise PermissionError(f"Permission denied: Cannot write to directory {file_dir}")
        
        if file_dir and not os.path.exists(file_dir):
            try:
                os.makedirs(file_dir, exist_ok=True)
            except PermissionError:
                raise PermissionError(f"Permission denied: Cannot create directory {file_dir}")
            except Exception as e:
                raise PermissionError(f"Failed to create directory {file_dir}: {str(e)}") 