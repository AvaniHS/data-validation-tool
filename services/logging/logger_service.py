import logging
import traceback
from typing import Any, Dict, Optional, Union
from datetime import datetime
import pandas as pd

from .logging_config import LoggingConfig, PerformanceLogger, DataLogger


class LoggerService:
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.logger = LoggingConfig.get_logger(component_name)
    
    def debug(self, message: str, extra_data: Dict[str, Any] = None):
        self._log_with_extra(logging.DEBUG, message, extra_data)
    
    def info(self, message: str, extra_data: Dict[str, Any] = None):
        self._log_with_extra(logging.INFO, message, extra_data)
    
    def warning(self, message: str, extra_data: Dict[str, Any] = None):
        self._log_with_extra(logging.WARNING, message, extra_data)
    
    def error(self, message: str, exception: Exception = None, extra_data: Dict[str, Any] = None):
        if exception:
            message += f" | Exception: {str(exception)}"
            if self.logger.level <= logging.DEBUG:
                message += f" | Traceback: {traceback.format_exc()}"
        self._log_with_extra(logging.ERROR, message, extra_data)
    
    def critical(self, message: str, exception: Exception = None, extra_data: Dict[str, Any] = None):
        if exception:
            message += f" | Exception: {str(exception)}"
            message += f" | Traceback: {traceback.format_exc()}"
        self._log_with_extra(logging.CRITICAL, message, extra_data)
    
    def _log_with_extra(self, level: int, message: str, extra_data: Dict[str, Any] = None):
        if extra_data:
            extra_str = " | ".join([f"{k}={v}" for k, v in extra_data.items()])
            message += f" | {extra_str}"
        self.logger.log(level, message)
    
    def log_operation_start(self, operation: str, details: Dict[str, Any] = None):
        message = f"Starting {operation}"
        self.info(message, details)
    
    def log_operation_success(self, operation: str, duration: float = None, details: Dict[str, Any] = None):
        message = f"Completed {operation}"
        if duration:
            message += f" in {duration:.2f}s"
        self.info(message, details)
    
    def log_operation_failure(self, operation: str, error: Exception, details: Dict[str, Any] = None):
        message = f"Failed {operation}"
        self.error(message, error, details)
    
    def log_file_operation(self, operation: str, file_path: str, success: bool = True, details: str = None):
        status = "successfully" if success else "failed"
        message = f"File {operation} {status}: {file_path}"
        if details:
            message += f" - {details}"
        
        if success:
            self.info(message)
        else:
            self.error(message)
    
    def log_dataframe_info(self, operation: str, df: pd.DataFrame, description: str = None):
        if df is not None:
            rows, cols = df.shape
            message = f"{operation} - DataFrame: {rows} rows × {cols} columns"
            if description:
                message += f" ({description})"
            self.info(message)
            
            if self.logger.level <= logging.DEBUG:
                memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024
                self.debug(f"DataFrame memory usage: {memory_usage:.2f} MB")
                self.debug(f"DataFrame columns: {list(df.columns)}")
        else:
            self.warning(f"{operation} - DataFrame is None")
    
    def log_configuration(self, config: Dict[str, Any], operation: str = "Configuration loaded"):
        self.info(f"{operation}")
        if self.logger.level <= logging.DEBUG:
            key_params = {
                'file_format': config.get('file_format'),
                'number_of_files': config.get('number_of_files'),
                'output_path': config.get('output_path'),
                'aggregation': 'enabled' if config.get('aggregation', 'NA') != 'NA' else 'disabled'
            }
            self.debug("Configuration parameters", key_params)
    
    def log_validation_result(self, validation_type: str, passed: bool, details: str = None, data: Dict[str, Any] = None):
        status = "PASSED" if passed else "FAILED"
        message = f"Validation {validation_type}: {status}"
        if details:
            message += f" - {details}"
        
        if passed:
            self.info(message, data)
        else:
            self.error(message, data=data)
    
    def log_performance_metrics(self, operation: str, metrics: Dict[str, Union[float, int]]):
        self.info(f"Performance metrics for {operation}", metrics)
    
    def log_pipeline_stage(self, stage: str, status: str, details: Dict[str, Any] = None):
        message = f"Pipeline stage '{stage}': {status}"
        
        if status.lower() in ['completed', 'success', 'successful']:
            self.info(message, details)
        elif status.lower() in ['failed', 'error']:
            self.error(message, details)
        else:
            self.info(message, details)
    
    def performance_context(self, operation_name: str):
        return PerformanceLogger(f"{self.component_name}.{operation_name}")
    
    @staticmethod
    def setup_application_logging(log_level: str = "INFO", log_dir: str = None, enable_console: bool = True):
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        log_level_int = level_map.get(log_level.upper(), logging.INFO)
        LoggingConfig.setup_logging(
            log_dir=log_dir,
            log_level=log_level_int,
            enable_console=enable_console
        )
    
    @staticmethod
    def log_session_start(config_path: str = None):
        LoggingConfig.log_session_start(config_path)
    
    @staticmethod
    def log_session_end(success: bool, duration: float = None):
        LoggingConfig.log_session_end(success, duration)


def get_logger(component_name: str) -> LoggerService:
    return LoggerService(component_name)
