import pandas as pd
import json
import os
import sys
from constants import EXIT_COMMANDS, USER_CHOICE_OVERWRITE, USER_CHOICE_RENAME
from services.logging.logger_service import get_logger


class JSONFileWriter:
    """Writer for JSON files that converts pandas DataFrame to JSON format"""
    
    def __init__(self):
        self.logger = get_logger("json_writer")
    
    def write(self, df: pd.DataFrame, file_path: str, **kwargs):
        """
        Write DataFrame to JSON file
        
        Args:
            df: DataFrame to write
            file_path: Path where to save the JSON file
            **kwargs: Additional options:
                - orient: JSON orientation ('records', 'index', 'values', 'split', 'table')
                - indent: JSON indentation (default: 2)
                - date_format: Date format for datetime columns
        """
        self.logger.log_operation_start("write_json_file", {"file_path": file_path, "dataframe_shape": df.shape})
        
        try:
            self._ensure_file_writable(file_path)
            
            # Handle file overwrite confirmation
            if os.path.exists(file_path):
                self.logger.warning(f"File already exists: {file_path}")
                while True:
                    print(f"Warning: File '{file_path}' already exists.")
                    choice = input("Type 'o' to overwrite, 'r' to enter a new file name, or 'exit' to quit: ").strip().lower()
                    if choice == USER_CHOICE_OVERWRITE:
                        self.logger.info(f"User chose to overwrite file: {file_path}")
                        break
                    elif choice == USER_CHOICE_RENAME:
                        new_file = input("Enter a new file name (including path): ").strip()
                        if new_file and not os.path.exists(new_file):
                            self.logger.info(f"User renamed file from {file_path} to {new_file}")
                            file_path = new_file
                            break
                        elif new_file:
                            print(f"File '{new_file}' already exists. Please choose another name.")
                    elif choice in EXIT_COMMANDS:
                        self.logger.info("User chose to exit during file overwrite prompt")
                        print("Exiting as requested by user.")
                        sys.exit(0)
                    else:
                        print("Invalid choice. Please enter 'o', 'r', or 'exit'.")
            
            # Extract JSON writing options
            orient = kwargs.get('orient', 'records')  # Default to records format
            indent = kwargs.get('indent', 2)  # Pretty formatting by default
            date_format = kwargs.get('date_format', 'iso')
            
            self.logger.debug(f"JSON write options: orient={orient}, indent={indent}, date_format={date_format}")
            
            # Convert DataFrame to JSON
            json_str = df.to_json(
                orient=orient,
                date_format=date_format,
                indent=indent,
                force_ascii=False  # Allow unicode characters
            )
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(json_str)
            
            file_size = os.path.getsize(file_path)
            self.logger.log_file_operation("write", file_path, True, f"Size: {file_size} bytes")
            self.logger.log_operation_success("write_json_file")
                
        except Exception as e:
            error_msg = f"Error writing JSON file '{file_path}': {str(e)}"
            self.logger.error(error_msg, e)
            raise ValueError(error_msg)
    
    def _ensure_file_writable(self, file_path: str) -> None:
        """Validate that the file can be written"""
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
