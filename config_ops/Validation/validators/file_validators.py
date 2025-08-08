"""File system validation (paths, formats, sheets)."""

import os
from typing import Dict, Any
from validation.exceptions import InvalidConfigurationError
from constants import DEFAULT_NA_VALUE, CSV_EXTENSION, EXCEL_EXTENSIONS
from ..validation_base import BaseValidator, FileValidatorMixin, ConfigValidatorMixin
from constants import (
    VALID_FILE_FORMATS, VALID_NUMBER_OF_FILES, ERROR_MESSAGES
)


class FileValidator(BaseValidator, FileValidatorMixin, ConfigValidatorMixin):
    """Validates file system aspects (paths, formats, sheets)."""
    
    def validate(self, config: Dict[str, Any]) -> None:
        self.clear()
        
        if not self.validate_field_value(config, 'file_format', VALID_FILE_FORMATS):
            return
        
        if not self.validate_field_value(config, 'number_of_files', VALID_NUMBER_OF_FILES):
            return
        
        self._validate_file_paths(config)
    
    def _validate_file_paths(self, config: Dict[str, Any]) -> None:
        file_format = config['file_format']
        number_of_files = config['number_of_files']
        
        if not self._validate_file_path(config['file1_path'], 'file1_path', file_format):
            return
        
        if number_of_files == 2:
            if 'file2_path' not in config or config['file2_path'] == DEFAULT_NA_VALUE:
                self.add_error(ERROR_MESSAGES['FILE2_PATH_REQUIRED'])
                return
            
            if not self._validate_file_path(config['file2_path'], 'file2_path', file_format):
                return
        
        if file_format == EXCEL_EXTENSIONS[0]:  # .xlsx
            self._validate_excel_sheets(config, number_of_files)
    
    def _validate_file_path(self, file_path: str, file_label: str, file_format: str) -> bool:
        if file_format != 'mixed':
            if not file_path.endswith(file_format):
                self.add_error(f"{file_label} must end with {file_format}")
                return False
        
        if not self.validate_file_exists(file_path, file_label):
            return False
        
        if not self.validate_file_readable(file_path, file_label):
            return False
        
        return True
    
    def _validate_excel_sheets(self, config: Dict[str, Any], number_of_files: int) -> None:
        if number_of_files == 2:
            if 'file1_sheet1' not in config or config['file1_sheet1'] == DEFAULT_NA_VALUE:
                self.add_error(ERROR_MESSAGES['FILE1_SHEET1_REQUIRED'])
            
            if 'file2_sheet' not in config or config['file2_sheet'] == DEFAULT_NA_VALUE:
                self.add_error(ERROR_MESSAGES['FILE2_SHEET_REQUIRED'])
        else:
            if 'file1_sheet1' not in config or config['file1_sheet1'] == DEFAULT_NA_VALUE:
                self.add_error(ERROR_MESSAGES['FILE1_SHEET1_REQUIRED'])
            
            if 'file1_sheet2' not in config or config['file1_sheet2'] == DEFAULT_NA_VALUE:
                self.add_error(ERROR_MESSAGES['FILE1_SHEET2_REQUIRED']) 