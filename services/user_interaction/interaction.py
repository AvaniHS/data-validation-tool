import os
import sys
import json
import shutil
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from config_ops.config_processor import ConfigValidator
from constants import (
    EXIT_COMMANDS, VALIDATION_MESSAGES, CONSOLE_MESSAGES, 
    ERROR_MESSAGES, EXAMPLE_MESSAGES, DEFAULT_FILE1_SHEET1, DEFAULT_FILE2_SHEET, DEFAULT_OUTPUT_SHEET,
    DEFAULT_OUTPUT_PATH, YES_CHOICES, NO_CHOICES, ENTER_CHOICES, PATHS, EXIT_MESSAGE
)


class UserInteraction:
    def __init__(self, input_provider):
        self.input_provider = input_provider

    def _handle_exit_command(self, user_input):
        if user_input.strip().lower() in EXIT_COMMANDS:
            print("Exiting as requested by user.")
            exit(0)
        return user_input

    def _get_input_with_exit_handling(self, prompt, required=True, default=None):
        while True:
            user_input = self.input_provider.get_input(prompt)
            self._handle_exit_command(user_input)
            
            if not user_input.strip():
                if default is not None:
                    return default
                elif not required:
                    return ""
                else:
                    print(VALIDATION_MESSAGES['REQUIRED_FIELD'])
                    continue
            else:
                return user_input.strip()

    def get_valid_file_path(self, prompt, required=True):
        while True:
            file_path = self._get_input_with_exit_handling(prompt, required)
            
            if not file_path and not required:
                return None
            
            file_path = file_path.strip().strip('"').strip("'")
            
            try:
                if file_path and os.path.exists(file_path):
                    if "configuration" in prompt.lower() and "json" in prompt.lower():
                        if not file_path.lower().endswith('.json'):
                            print(f"Error: Configuration file must be a JSON file (.json extension). You entered: {file_path}")
                            print("Please enter the path to a JSON configuration file, not an Excel or CSV file.")
                            continue
                    
                    return file_path
                else:
                    if required:
                        raise ValueError(f"File not found: {file_path}")
                    return None
            except ValueError as e:
                print(f"Error: {str(e)}")
                if not required:
                    return None

    def display_input_requirements(self):
        print("Configuration file required")

    def get_input_files(self) -> Tuple[str, str, str]:
        print(CONSOLE_MESSAGES['FILE_INPUT_SECTION'])
        print(EXIT_MESSAGE)
        
        self._offer_sample_download()
        
        print(CONSOLE_MESSAGES['CONFIG_FILE_PROMPT'])
        
        while True:
            try:
                config_file = self.get_valid_file_path(
                    "Enter path to your configuration JSON file", required=True
                )
                
                if not config_file:
                    return None, None, None
                
                config = ConfigValidator.validate_config_file(config_file)
                file1 = config.get('file1_path')
                file2 = config.get('file2_path')
                
                return config_file, file1, file2
                
            except ValueError as e:
                print(f"Configuration error: {str(e)}")
                print("What would you like to do?")
                print("R - Retry with different file")
                print("D - Download sample template")
                print("E - Exit")
                
                choice = self._get_input_with_exit_handling("Choice (R/D/E)", required=False, default="R")
                
                if choice.lower() in ['r', 'retry']:
                    continue
                elif choice.lower() in ['d', 'download']:
                    self._download_sample_configs()
                    continue
                elif choice.lower() in ['e', 'exit']:
                    return None, None, None
                else:
                    print("Invalid choice. Please enter R, D, or E.")

    def _offer_sample_download(self):
        while True:
            print("Download sample files? (Y/E/Enter)")
            print("Y - Download template, E - Enter path, Enter - Continue")
            
            choice = self._get_input_with_exit_handling("Choice", required=False, default="")
            
            if choice.lower() in YES_CHOICES:
                self._download_sample_configs()
                break
            elif choice.lower() in ENTER_CHOICES:
                break
            elif choice.lower() in NO_CHOICES:
                break
            else:
                print("Invalid choice. Enter Y, E, or press Enter.")

    def _download_sample_configs(self):
        print("Downloading sample files...")
        
        downloads_dir = PATHS['DOWNLOADS_DIR']
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
            print(f"Created directory: {downloads_dir}")
        
        try:
            from config_ops.templates import get_configuration_template, get_configuration_guidelines
            
            config_template = get_configuration_template()
            template_path = os.path.join(downloads_dir, PATHS['CONFIG_TEMPLATE_JSON'])
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(config_template, f, indent=4)
            print(f"Downloaded: {template_path}")
            
            guidelines_content = get_configuration_guidelines()
            guidelines_path = os.path.join(downloads_dir, PATHS['CONFIG_GUIDELINES_JSONC'])
            with open(guidelines_path, 'w', encoding='utf-8') as f:
                f.write(guidelines_content)
            print(f"Downloaded: {guidelines_path}")
            
        except ImportError as e:
            print(f"Error: Template system unavailable - {e}")
            print("What would you like to do?")
            print("R - Retry download")
            print("C - Continue without sample files")
            print("E - Exit")
            
            choice = self._get_input_with_exit_handling("Choice (R/C/E)", required=False, default="C")
            
            if choice.lower() in ['r', 'retry']:
                self._download_sample_configs()
            elif choice.lower() in ['e', 'exit']:
                return
        
        print(f"Sample files downloaded to '{downloads_dir}/' directory")

    def get_user_inputs(self, args):
        print(CONSOLE_MESSAGES['WELCOME'])
        print(EXIT_MESSAGE)
        
        self._offer_sample_download()
        
        config_file = args.file1 or self.get_valid_file_path("Enter path to your configuration JSON file", required=True)
        
        if not config_file:
            return None, None, None, None, None, None, None
        
        while True:
            try:
                config = ConfigValidator.validate_config_file(config_file)
                file1 = config.get('file1_path')
                file2 = config.get('file2_path')
                
                column_mapping = config.get('column_mapping', {})
                output = args.output or config.get('output_path', DEFAULT_OUTPUT_PATH)
                file1sheet = args.file1sheet or config.get('file1_sheet1', DEFAULT_FILE1_SHEET1)
                file2sheet = args.file2sheet or config.get('file2_sheet', DEFAULT_FILE2_SHEET)
                outputsheet = args.outputsheet or config.get('output_sheet', DEFAULT_OUTPUT_SHEET)
                
                return file1, file2, column_mapping, output, file1sheet, file2sheet, outputsheet
                
            except ValueError as e:
                print(f"Configuration error: {str(e)}")
                print("What would you like to do?")
                print("R - Retry with different file")
                print("D - Download sample template")
                print("E - Exit")
                
                choice = self._get_input_with_exit_handling("Choice (R/D/E)", required=False, default="R")
                
                if choice.lower() in ['r', 'retry']:
                    config_file = self.get_valid_file_path("Enter path to your configuration JSON file", required=True)
                    if not config_file:
                        return None, None, None, None, None, None, None
                    continue
                elif choice.lower() in ['d', 'download']:
                    self._download_sample_configs()
                    config_file = self.get_valid_file_path("Enter path to your configuration JSON file", required=True)
                    if not config_file:
                        return None, None, None, None, None, None, None
                    continue
                elif choice.lower() in ['e', 'exit']:
                    return None, None, None, None, None, None, None
                else:
                    print("Invalid choice. Please enter R, D, or E.")

    def _get_valid_json_mapping(self, prompt):
        while True:
            mapping_input = self._get_input_with_exit_handling(prompt)
            
            try:
                import json
                mapping = json.loads(mapping_input)
                
                if isinstance(mapping, dict):
                    return mapping
                else:
                    raise ValueError("Mapping must be a JSON object (dictionary).")
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format. Please enter a valid JSON mapping.")
            except ValueError as e:
                print(f"Error: {str(e)}")
                print(EXAMPLE_MESSAGES['JSON_MAPPING_EXAMPLE'])

    def get_additional_columns(self, df1: pd.DataFrame, df2: pd.DataFrame) -> Tuple[List[str], List[str]]:
        print(CONSOLE_MESSAGES['ADDITIONAL_COLUMNS_SECTION'])
        
        additional_cols_df1 = self._get_additional_columns_for_dataset(df1, "first dataset")
        additional_cols_df2 = self._get_additional_columns_for_dataset(df2, "second dataset")
        
        return additional_cols_df1, additional_cols_df2

    def _get_additional_columns_for_dataset(self, df: pd.DataFrame, dataset_name: str) -> List[str]:
        print(f"Available columns in {dataset_name}:")
        for i, col in enumerate(df.columns, 1):
            print(f"{i}. {col}")
        
        print(f"Enter column numbers for {dataset_name} (comma-separated, or press Enter to skip):")
        print(EXAMPLE_MESSAGES['COLUMN_NUMBERS_EXAMPLE'])
        print(EXAMPLE_MESSAGES['EXIT_COMMAND'])
        
        while True:
            user_input = self._get_input_with_exit_handling("Column numbers: ", required=False)
            
            if not user_input:
                return []
            
            try:
                column_numbers = [int(x.strip()) for x in user_input.split(',')]
                
                if not all(1 <= num <= len(df.columns) for num in column_numbers):
                    raise ValueError("Invalid column numbers. Please enter valid numbers.")
                
                selected_columns = [df.columns[num - 1] for num in column_numbers]
                print(f"Selected columns for {dataset_name}: {selected_columns}")
                return selected_columns
            except ValueError as e:
                print(f"Error: {str(e)}")
            except Exception:
                print(VALIDATION_MESSAGES['INVALID_FORMAT'])

    def display_dataset_summary(self, df1: pd.DataFrame, df2: pd.DataFrame, 
                              additional_cols_df1: List[str], additional_cols_df2: List[str]):
        print(CONSOLE_MESSAGES['DATASET_SUMMARY_HEADER'])
        
        print(f"First Dataset: {len(df1)} rows, {len(df1.columns)} columns")
        print(f"Second Dataset: {len(df2)} rows, {len(df2.columns)} columns")
        
        if additional_cols_df1:
            print(f"Additional columns from first dataset: {additional_cols_df1}")
        if additional_cols_df2:
            print(f"Additional columns from second dataset: {additional_cols_df2}")
        
        print(CONSOLE_MESSAGES['DATASET_SUMMARY_FOOTER']) 