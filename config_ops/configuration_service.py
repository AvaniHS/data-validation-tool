from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json
import os

from config_ops import ConfigValidator, ConfigEnricher, ConfigProcessor
from config_ops.file_reader import FileReader
from validation.exceptions import ConfigValidationError
from constants import DEFAULT_NA_VALUE


class IConfigurationService(ABC):
    
    @abstractmethod
    def load_configuration(self, config_path: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def enrich_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def process_configuration(self, config_path: str) -> Dict[str, Any]:
        pass


class ConfigurationService(IConfigurationService):
    
    def __init__(self):
        self._validator = ConfigValidator()
        self._enricher = ConfigEnricher()
        self._processor = ConfigProcessor()
        self._file_reader = FileReader()
    
    def load_configuration(self, config_path: str) -> Dict[str, Any]:
        try:
            if not os.path.exists(config_path):
                raise ConfigValidationError(f"Configuration file not found: {config_path}")
            
            config_data = self._file_reader.read_file(config_path)
            
            if not isinstance(config_data, dict):
                raise ConfigValidationError("Configuration must be a JSON object")
            
            return config_data
            
        except json.JSONDecodeError as e:
            raise ConfigValidationError(f"Invalid JSON format in configuration file: {str(e)}")
        except Exception as e:
            raise ConfigValidationError(f"Failed to load configuration: {str(e)}")
    
    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        try:
            self._validator.validate_config(config)
            return True
            
        except Exception as e:
            if isinstance(e, ConfigValidationError):
                raise
            raise ConfigValidationError(f"Configuration validation failed: {str(e)}")
    
    def enrich_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self._enricher.enrich_config(config)
        except Exception as e:
            raise ConfigValidationError(f"Failed to enrich configuration: {str(e)}")
    
    def process_configuration(self, config_path: str) -> Dict[str, Any]:
        try:
            config = self.load_configuration(config_path)
            
            self.validate_configuration(config)
            
            enriched_config = self.enrich_configuration(config)
            
            return enriched_config
            
        except Exception as e:
            if isinstance(e, ConfigValidationError):
                raise
            raise ConfigValidationError(f"Configuration processing failed: {str(e)}")
    
    def get_configuration_summary(self, config: Dict[str, Any]) -> Dict[str, Any]:
        try:
            summary = {
                'file_format': config.get('file_format'),
                'number_of_files': config.get('number_of_files'),
                'file1_path': config.get('file1_path'),
                'file2_path': config.get('file2_path'),
                'output_path': config.get('output_path'),
                'column_mapping_count': len(config.get('column_mapping', {})),
                'join_keys_count': len(config.get('join_keys', {})),
                'has_aggregation': config.get('aggregation') != DEFAULT_NA_VALUE,
                'file1_metrics_count': len(config.get('file1_metric_list', [])),
                'file2_metrics_count': len(config.get('file2_metric_list', []))
            }
            
            return summary
            
        except Exception as e:
            return {'error': f"Failed to generate summary: {str(e)}"}
    
    def validate_file_paths(self, config: Dict[str, Any]) -> List[str]:
        errors = []
        
        file1_path = config.get('file1_path')
        if file1_path and not os.path.exists(file1_path):
            errors.append(f"File1 not found: {file1_path}")
        
        file2_path = config.get('file2_path')
        if file2_path and not os.path.exists(file2_path):
            errors.append(f"File2 not found: {file2_path}")
        
        output_directory = os.path.dirname(config.get('output_path', ''))
        output_path = config.get('output_path')
        if output_path:
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                except Exception as e:
                    errors.append(f"Cannot create output directory {output_dir}: {str(e)}")
        
        return errors 