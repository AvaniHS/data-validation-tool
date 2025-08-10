import logging
import logging.handlers
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class LoggingConfig:
    
    DEFAULT_LOG_DIR = "logs"
    DEFAULT_LOG_LEVEL = logging.INFO
    DEFAULT_MAX_FILE_SIZE = 10 * 1024 * 1024
    DEFAULT_BACKUP_COUNT = 5
    DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s"
    DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    @classmethod
    def setup_logging(cls, 
                     log_dir: str = None,
                     log_level: int = None,
                     max_file_size: int = None,
                     backup_count: int = None,
                     log_format: str = None,
                     date_format: str = None,
                     enable_console: bool = True) -> None:
        
        log_dir = log_dir or cls.DEFAULT_LOG_DIR
        log_level = log_level or cls.DEFAULT_LOG_LEVEL
        max_file_size = max_file_size or cls.DEFAULT_MAX_FILE_SIZE
        backup_count = backup_count or cls.DEFAULT_BACKUP_COUNT
        log_format = log_format or cls.DEFAULT_LOG_FORMAT
        date_format = date_format or cls.DEFAULT_DATE_FORMAT
        
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        formatter = logging.Formatter(log_format, date_format)
        
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        root_logger.handlers.clear()
        
        cls._setup_file_handlers(root_logger, log_path, formatter, max_file_size, backup_count)
        
        if enable_console:
            cls._setup_console_handler(root_logger, formatter)
    
    @classmethod
    def _setup_file_handlers(cls, logger: logging.Logger, log_path: Path, 
                           formatter: logging.Formatter, max_file_size: int, backup_count: int) -> None:
        
        main_log_file = log_path / "data_validation.log"
        main_handler = logging.handlers.RotatingFileHandler(
            main_log_file, maxBytes=max_file_size, backupCount=backup_count
        )
        main_handler.setLevel(logging.INFO)
        main_handler.setFormatter(formatter)
        logger.addHandler(main_handler)
        
        error_log_file = log_path / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file, maxBytes=max_file_size, backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
        
        if logger.level <= logging.DEBUG:
            debug_log_file = log_path / "debug.log"
            debug_handler = logging.handlers.RotatingFileHandler(
                debug_log_file, maxBytes=max_file_size, backupCount=backup_count
            )
            debug_handler.setLevel(logging.DEBUG)
            debug_handler.setFormatter(formatter)
            logger.addHandler(debug_handler)
    
    @classmethod
    def _setup_console_handler(cls, logger: logging.Logger, formatter: logging.Formatter) -> None:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        console_format = "%(levelname)-8s | %(name)-15s | %(message)s"
        console_formatter = logging.Formatter(console_format)
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(console_handler)
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        return logging.getLogger(name)
    
    @classmethod
    def log_session_start(cls, config_path: str = None) -> None:
        logger = cls.get_logger("session")
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info("=" * 80)
        logger.info(f"NEW VALIDATION SESSION STARTED - ID: {session_id}")
        logger.info("=" * 80)
        if config_path:
            logger.info(f"Configuration file: {config_path}")
        logger.info(f"Session start time: {datetime.now().isoformat()}")
    
    @classmethod
    def log_session_end(cls, success: bool, duration: float = None) -> None:
        logger = cls.get_logger("session")
        
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"VALIDATION SESSION COMPLETED - STATUS: {status}")
        if duration:
            logger.info(f"Total duration: {duration:.2f} seconds")
        logger.info(f"Session end time: {datetime.now().isoformat()}")
        logger.info("=" * 80)


class PerformanceLogger:
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.logger = LoggingConfig.get_logger("performance")
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            if exc_type:
                self.logger.warning(f"Operation '{self.operation_name}' failed after {duration:.2f}s: {exc_val}")
            else:
                self.logger.info(f"Operation '{self.operation_name}' completed in {duration:.2f}s")


class DataLogger:
    
    @staticmethod
    def log_data_stats(operation: str, dataframe_shape: tuple, file_path: str = None):
        logger = LoggingConfig.get_logger("data")
        rows, cols = dataframe_shape
        message = f"{operation} - DataFrame: {rows} rows × {cols} columns"
        if file_path:
            message += f" from {file_path}"
        logger.info(message)
    
    @staticmethod
    def log_data_validation(validation_type: str, passed: bool, details: str = None):
        logger = LoggingConfig.get_logger("validation")
        status = "PASSED" if passed else "FAILED"
        message = f"Data validation {validation_type}: {status}"
        if details:
            message += f" - {details}"
        
        if passed:
            logger.info(message)
        else:
            logger.error(message)
