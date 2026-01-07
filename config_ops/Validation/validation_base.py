import os
from typing import Dict, Any, List, Optional
import pandas as pd
from .config_validation_contracts import IValidator, IFileValidator, IConfigValidator
from validation.exceptions import InvalidConfigurationError


class BaseValidator(IValidator):
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self, config: Dict[str, Any]) -> None:
        pass
    
    def add_error(self, message: str) -> None:
        self.errors.append(message)
    
    def add_warning(self, message: str) -> None:
        self.warnings.append(message)
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    def get_errors(self) -> List[str]:
        return self.errors.copy()
    
    def get_warnings(self) -> List[str]:
        return self.warnings.copy()
    
    def clear(self) -> None:
        self.errors.clear()
        self.warnings.clear()


class FileValidatorMixin(IFileValidator):
    
    def validate_file_exists(self, file_path: str, file_label: str) -> bool:
        if not os.path.exists(file_path):
            self.add_error(f"File not found: {file_path} ({file_label})")
            return False
        return True
    
    def validate_file_readable(self, file_path: str, file_label: str) -> bool:
        if not os.access(file_path, os.R_OK):
            self.add_error(f"Permission denied: Cannot read file {file_path} ({file_label})")
            return False
        return True
    
    def validate_directory_accessible(self, file_path: str, file_label: str) -> bool:
        file_dir = os.path.dirname(file_path)
        if file_dir and not os.access(file_dir, os.R_OK):
            self.add_error(f"Permission denied: Cannot access directory {file_dir} ({file_label})")
            return False
        return True


class ConfigValidatorMixin(IConfigValidator):
    
    def validate_required_fields(self, config: Dict[str, Any], required_fields: List[str]) -> bool:
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            self.add_error(f"Missing required fields: {', '.join(missing_fields)}")
            return False
        return True
    
    def validate_field_type(self, config: Dict[str, Any], field: str, expected_type: type) -> bool:
        if field in config and not isinstance(config[field], expected_type):
            self.add_error(f"Field '{field}' must be of type {expected_type.__name__}")
            return False
        return True
    
    def validate_field_value(self, config: Dict[str, Any], field: str, valid_values: List[Any]) -> bool:
        if field in config and config[field] not in valid_values:
            self.add_error(f"Invalid value for '{field}': {config[field]}. Must be one of: {', '.join(map(str, valid_values))}")
            return False
        return True 