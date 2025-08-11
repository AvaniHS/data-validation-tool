import os
import json
from typing import Dict, Any, List
from .validation_base import BaseValidator
from .validator_factory import ValidatorFactory
from constants import (
    ERROR_MESSAGES, VALIDATION_MESSAGES, DEFAULT_OUTPUT_PATH, DEFAULT_OUTPUT_SHEET
)


class ConfigValidator(BaseValidator):
    
    def __init__(self):
        super().__init__()
        self.validator_factory = ValidatorFactory()
        self.validators = self.validator_factory.get_all_validators()
    
    @staticmethod
    def validate_config_file(config_file_path: str) -> Dict[str, Any]:
        validator = ConfigValidator()
        return validator._validate_config_file(config_file_path)
    
    def _validate_config_file(self, config_file_path: str) -> Dict[str, Any]:
        try:
            self._validate_file_access(config_file_path)
            with open(config_file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.validate_config(config)
            return config
            
        except json.JSONDecodeError as e:
            raise ValueError(ERROR_MESSAGES['INVALID_JSON_FORMAT'].format(str(e)))
        except Exception as e:
            raise ValueError(ERROR_MESSAGES['CONFIGURATION_VALIDATION_ERROR'].format(str(e)))
    
    def validate_config(self, config: Dict[str, Any]) -> None:
        try:
            self._validate_basic_structure(config)
            self._run_validators(config)
            
            if self.has_errors():
                error_message = "Configuration validation failed:\n" + "\n".join(self.get_errors())
                raise ValueError(error_message)
                
        except Exception as e:
            raise ValueError(ERROR_MESSAGES['CONFIGURATION_VALIDATION_ERROR'].format(str(e)))
    
    def _validate_file_access(self, config_file_path: str) -> None:
        if not os.path.exists(config_file_path):
            raise ValueError(ERROR_MESSAGES['CONFIG_FILE_NOT_FOUND'].format(config_file_path))
        
        if not os.access(config_file_path, os.R_OK):
            raise ValueError(ERROR_MESSAGES['CONFIG_FILE_PERMISSION_DENIED'].format(config_file_path))
    

    
    def _validate_basic_structure(self, config: Dict[str, Any]) -> None:
        required_fields = ['file_format', 'number_of_files', 'file1_path', 'column_mapping']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            self.add_error(ERROR_MESSAGES['MISSING_REQUIRED_FIELDS'].format(missing_fields))
    
    def _run_validators(self, config: Dict[str, Any]) -> None:
        validator_order = ['file', 'schema', 'data', 'output']
        
        for validator_name in validator_order:
            if validator_name in self.validators:
                self._run_validator(validator_name, config)
    
    def _run_validator(self, validator_name: str, config: Dict[str, Any]) -> None:
        validator = self.validators[validator_name]
        validator.validate(config)
        
        for error in validator.get_errors():
            self.add_error(error)
        
        for warning in validator.get_warnings():
            self.add_warning(warning)