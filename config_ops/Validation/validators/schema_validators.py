"""Configuration schema validation."""

from typing import Dict, Any, List
from validation.exceptions import InvalidConfigurationError
from constants import VALID_AGGREGATION_TYPES, ERROR_MESSAGES, DEFAULT_NA_VALUE
from ..validation_base import BaseValidator, ConfigValidatorMixin


class SchemaValidator(BaseValidator, ConfigValidatorMixin):
    """Validates configuration structure and schema."""
    
    def validate(self, config: Dict[str, Any]) -> None:
        self.clear()
        
        self._validate_basic_structure(config)
        self._validate_aggregation_schema(config)
        self._validate_column_mapping_schema(config)
        self._validate_join_keys_schema(config)
        self._validate_additional_columns_schema(config)
    
    def _validate_basic_structure(self, config: Dict[str, Any]) -> None:
        required_fields = ['file_format', 'number_of_files', 'file1_path', 'column_mapping']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            self.add_error(ERROR_MESSAGES['MISSING_REQUIRED_FIELDS'].format(missing_fields))
    
    def _validate_aggregation_schema(self, config: Dict[str, Any]) -> None:
        aggregation = config.get('aggregation', {})
        
        if not aggregation:
            self.add_warning("No aggregation configuration found. All non-join columns will be auto-grouped by default.")
            return
        
        self._validate_aggregation_structure(aggregation)
    
    def _validate_aggregation_structure(self, aggregation: Dict[str, Any]) -> None:
        valid_agg_types = VALID_AGGREGATION_TYPES
        optional_keys = ['file1_columns', 'file2_columns', 'final_aggregated_columns']
        
        has_aggregation = any(key in aggregation for key in optional_keys)
        
        if not has_aggregation:
            self.add_warning("No aggregation configuration found. All non-join columns will be auto-grouped by default.")
            return
        
        for file_key in ['file1_columns', 'file2_columns']:
            if file_key in aggregation:
                self._validate_aggregation_columns_dict(aggregation[file_key], file_key, valid_agg_types)
        
        groupby_fields = ['file1_groupby_columns', 'file2_groupby_columns', 'final_groupby_columns']
        for groupby_field in groupby_fields:
            if groupby_field in aggregation:
                self._validate_groupby_columns(aggregation[groupby_field], groupby_field)
        
        if 'final_aggregated_columns' in aggregation:
            self._validate_aggregation_columns_dict(aggregation['final_aggregated_columns'], 'final_aggregated_columns', valid_agg_types)
        
        if 'groupby_columns' in aggregation:
            self._validate_groupby_columns(aggregation['groupby_columns'], 'groupby_columns')
    
    def _validate_aggregation_columns_dict(self, agg_dict: Dict[str, Any], field_name: str, valid_types: List[str]) -> None:
        if not isinstance(agg_dict, dict):
            self.add_error(ERROR_MESSAGES['AGGREGATION_COLUMN_DICT'].format(field_name))
            return
        
        for agg_type, columns in agg_dict.items():
            if agg_type not in valid_types:
                self.add_error(ERROR_MESSAGES['INVALID_AGGREGATION_TYPE'].format(agg_type, field_name, ', '.join(valid_types)))
                continue
            
            if columns == DEFAULT_NA_VALUE:
                agg_dict[agg_type] = []
            elif isinstance(columns, list):
                if not all(isinstance(col, str) for col in columns):
                    self.add_error(ERROR_MESSAGES['AGGREGATION_COLUMN_LIST'].format(field_name, agg_type))
            else:
                self.add_error(ERROR_MESSAGES['INVALID_AGGREGATION_VALUE'].format(field_name, agg_type))
    
    def _validate_groupby_columns(self, groupby_cols: Any, field_name: str) -> None:
        if groupby_cols == DEFAULT_NA_VALUE:
            return
        elif isinstance(groupby_cols, list):
            if not all(isinstance(col, str) for col in groupby_cols):
                self.add_error(ERROR_MESSAGES['GROUPBY_COLUMN_LIST'])
        else:
            self.add_error(ERROR_MESSAGES['GROUPBY_COLUMN_VALUE'])
    
    def _validate_column_mapping_schema(self, config: Dict[str, Any]) -> None:
        if not self.validate_field_type(config, 'column_mapping', dict):
            return
    
    def _validate_join_keys_schema(self, config: Dict[str, Any]) -> None:
        if 'join_keys' not in config or config['join_keys'] == DEFAULT_NA_VALUE:
            return
        
        if not self.validate_field_type(config, 'join_keys', dict):
            return
    
    def _validate_additional_columns_schema(self, config: Dict[str, Any]) -> None:
        for field in ['additional_columns_file1', 'additional_columns_file2']:
            if field in config and config[field] != DEFAULT_NA_VALUE:
                if not isinstance(config[field], (list, dict)):
                    self.add_error(f"{field} must be a list or a dictionary (object)") 