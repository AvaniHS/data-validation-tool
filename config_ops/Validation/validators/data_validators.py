"""Data validation (column existence, mapping validation)."""

from typing import Dict, Any, Optional, List
from validation.exceptions import InvalidConfigurationError
from constants import DEFAULT_NA_VALUE
from ..validation_base import BaseValidator, ConfigValidatorMixin
from ...file_reader import FileReader


class DataValidator(BaseValidator, ConfigValidatorMixin):
    """Validates data-related aspects (column existence, mappings)."""
    
    def __init__(self):
        super().__init__()
        self.file_reader = FileReader()
    
    def validate(self, config: Dict[str, Any]) -> None:
        self.clear()
        
        file1_columns, file2_columns = self.file_reader.get_both_file_columns(config)
        
        if file1_columns is None or file2_columns is None:
            self.add_error("Unable to read file columns for validation")
            return
        
        self._validate_column_mapping(config['column_mapping'], file1_columns, file2_columns)
        self._validate_join_keys(config, file1_columns, file2_columns)
        self._validate_additional_columns(config, file1_columns, file2_columns)
        self._validate_aggregation_columns(config, file1_columns, file2_columns)
    
    def _validate_column_mapping(self, column_mapping: Dict[str, str], file1_columns: set, file2_columns: set) -> None:
        missing_in_file1 = []
        missing_in_file2 = []
        
        for file1_col, file2_col in column_mapping.items():
            if file1_col not in file1_columns:
                missing_in_file1.append(file1_col)
            if file2_col not in file2_columns:
                missing_in_file2.append(file2_col)
        
        if missing_in_file1 or missing_in_file2:
            error_msg = "Column mapping validation failed:\n"
            if missing_in_file1:
                error_msg += f"  Missing in file1: {', '.join(missing_in_file1)}\n"
            if missing_in_file2:
                error_msg += f"  Missing in file2: {', '.join(missing_in_file2)}\n"
            self.add_error(error_msg)
        else:
            self.add_warning(f"Column mapping validation passed: {len(column_mapping)} columns mapped successfully")
    
    def _validate_join_keys(self, config: Dict[str, Any], file1_columns: set, file2_columns: set) -> None:
        if 'join_keys' not in config or config['join_keys'] == DEFAULT_NA_VALUE:
            return
        
        join_keys = config['join_keys']
        missing_in_file1 = []
        missing_in_file2 = []
        
        for file1_key, file2_key in join_keys.items():
            if file1_key not in file1_columns:
                missing_in_file1.append(file1_key)
            if file2_key not in file2_columns:
                missing_in_file2.append(file2_key)
        
        if missing_in_file1 or missing_in_file2:
            error_msg = "Join keys validation failed:\n"
            if missing_in_file1:
                error_msg += f"  Missing in file1: {', '.join(missing_in_file1)}\n"
            if missing_in_file2:
                error_msg += f"  Missing in file2: {', '.join(missing_in_file2)}\n"
            self.add_error(error_msg)
        else:
            self.add_warning(f"Join keys validation passed: {len(join_keys)} join keys validated successfully")
    
    def _validate_additional_columns(self, config: Dict[str, Any], file1_columns: set, file2_columns: set) -> None:
        self._validate_additional_columns_file(config, 'additional_columns_file1', file1_columns)
        self._validate_additional_columns_file(config, 'additional_columns_file2', file2_columns)
    
    def _validate_additional_columns_file(self, config: Dict[str, Any], field_name: str, file_columns: set) -> None:
        if field_name not in config or config[field_name] == DEFAULT_NA_VALUE:
            return
        
        additional_cols = config[field_name]
        
        if isinstance(additional_cols, dict):
            column_names = list(additional_cols.keys())
            missing_columns = [col for col in column_names if col not in file_columns]
            
            if missing_columns:
                self.add_error(f"Missing additional columns in {field_name}: {', '.join(missing_columns)}")
            else:
                self.add_warning(f"Additional columns validation passed: {len(column_names)} from {field_name}")
        elif isinstance(additional_cols, list):
            missing_columns = [col for col in additional_cols if col not in file_columns]
            
            if missing_columns:
                self.add_error(f"Missing additional columns in {field_name}: {', '.join(missing_columns)}")
            else:
                self.add_warning(f"Additional columns validation passed: {len(additional_cols)} from {field_name}")
        else:
            self.add_error(f"{field_name} must be a list or a dictionary (object)")
    
    def _validate_aggregation_columns(self, config: Dict[str, Any], file1_columns: set, file2_columns: set) -> None:
        aggregation = config.get('aggregation', {})
        if not aggregation:
            return
        
        self._validate_file_aggregation_columns(aggregation, 'file1_columns', file1_columns)
        self._validate_file_aggregation_columns(aggregation, 'file2_columns', file2_columns)
        self._validate_groupby_columns_existence(aggregation, file1_columns, file2_columns)
        self._print_aggregation_success(aggregation)
    
    def _validate_file_aggregation_columns(self, aggregation: Dict[str, Any], field_name: str, file_columns: set) -> None:
        if field_name not in aggregation:
            return
        
        agg_dict = aggregation[field_name]
        if not isinstance(agg_dict, dict):
            return
        
        missing_columns = []
        for agg_type, columns in agg_dict.items():
            if columns != DEFAULT_NA_VALUE and isinstance(columns, list):
                for col in columns:
                    if col not in file_columns:
                        missing_columns.append(f"{col} (in {agg_type})")
        
        if missing_columns:
            self.add_error(f"Missing aggregation columns in {field_name}: {', '.join(missing_columns)}")
    
    def _validate_groupby_columns_existence(self, aggregation: Dict[str, Any], file1_columns: set, file2_columns: set) -> None:
        groupby_fields = ['file1_groupby_columns', 'file2_groupby_columns', 'final_groupby_columns', 'groupby_columns']
        
        for field in groupby_fields:
            if field not in aggregation:
                continue
            
            groupby_cols = aggregation[field]
            if groupby_cols == DEFAULT_NA_VALUE or not isinstance(groupby_cols, list):
                continue
            
            missing_columns = []
            for col in groupby_cols:
                if field == 'file1_groupby_columns' and col not in file1_columns:
                    missing_columns.append(f"{col} (in {field})")
                elif field == 'file2_groupby_columns' and col not in file2_columns:
                    missing_columns.append(f"{col} (in {field})")
                elif field in ['final_groupby_columns', 'groupby_columns']:
                    if col not in file1_columns and col not in file2_columns:
                        missing_columns.append(f"{col} (in {field})")
            
            if missing_columns:
                self.add_error(f"Missing groupby columns: {', '.join(missing_columns)}")
    
    def _print_aggregation_success(self, aggregation: Dict[str, Any]) -> None:
        total_agg_cols = 0
        for field in ['file1_columns', 'file2_columns', 'final_aggregated_columns']:
            if field in aggregation and isinstance(aggregation[field], dict):
                for columns in aggregation[field].values():
                    if columns != DEFAULT_NA_VALUE and isinstance(columns, list):
                        total_agg_cols += len(columns)
        
        groupby_counts = {}
        groupby_fields = ['file1_groupby_columns', 'file2_groupby_columns', 'final_groupby_columns', 'groupby_columns']
        for field in groupby_fields:
            if field in aggregation:
                groupby_cols = aggregation[field]
                if groupby_cols != DEFAULT_NA_VALUE and isinstance(groupby_cols, list):
                    groupby_counts[field] = len(groupby_cols)
        
        if total_agg_cols == 0 and not groupby_counts:
            self.add_warning("Aggregation validation passed: No aggregation configured, all columns will be auto-grouped")
        else:
            success_msg = f"Aggregation columns validation passed: {total_agg_cols} aggregation columns"
            if groupby_counts:
                groupby_details = []
                for field, count in groupby_counts.items():
                    groupby_details.append(f"{count} {field}")
                success_msg += f", {', '.join(groupby_details)}"
            self.add_warning(success_msg) 