"""
Logging configuration for the data validation tool.
Provides structured logging with file rotation, different log levels, and formatters.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class LoggingConfig:
    """Centralized logging configuration"""
    
    # Default configuration
    DEFAULT_LOG_DIR = "logs"
    DEFAULT_LOG_LEVEL = logging.INFO
    DEFAULT_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
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
        """
        Setup logging configuration for the application
        
        Args:
            log_dir: Directory for log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_file_size: Maximum size of each log file in bytes
            backup_count: Number of backup files to keep
            log_format: Custom log format string
            date_format: Custom date format string
            enable_console: Whether to also log to console
        """
        # Use defaults if not provided
        log_dir = log_dir or cls.DEFAULT_LOG_DIR
        log_level = log_level or cls.DEFAULT_LOG_LEVEL
        max_file_size = max_file_size or cls.DEFAULT_MAX_FILE_SIZE
        backup_count = backup_count or cls.DEFAULT_BACKUP_COUNT
        log_format = log_format or cls.DEFAULT_LOG_FORMAT
        date_format = date_format or cls.DEFAULT_DATE_FORMAT
        
        # Create log directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Create formatter
        formatter = logging.Formatter(log_format, date_format)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Setup file handlers
        cls._setup_file_handlers(root_logger, log_path, formatter, max_file_size, backup_count)
        
        # Setup console handler if enabled
        if enable_console:
            cls._setup_console_handler(root_logger, formatter)
    
    @classmethod
    def _setup_file_handlers(cls, logger: logging.Logger, log_path: Path, 
                           formatter: logging.Formatter, max_file_size: int, backup_count: int) -> None:
        """Setup rotating file handlers for different log levels"""
        
        # Main application log (INFO and above)
        main_log_file = log_path / "data_validation.log"
        main_handler = logging.handlers.RotatingFileHandler(
            main_log_file, maxBytes=max_file_size, backupCount=backup_count
        )
        main_handler.setLevel(logging.INFO)
        main_handler.setFormatter(formatter)
        logger.addHandler(main_handler)
        
        # Error log (ERROR and above)
        error_log_file = log_path / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file, maxBytes=max_file_size, backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
        
        # Debug log (DEBUG and above) - only if debug level is set
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
        """Setup console handler for immediate feedback"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
        
        # Simplified format for console
        console_format = "%(levelname)-8s | %(name)-15s | %(message)s"
        console_formatter = logging.Formatter(console_format)
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(console_handler)
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a logger instance for a specific module"""
        return logging.getLogger(name)
    
    @classmethod
    def log_session_start(cls, config_path: str = None) -> None:
        """Log the start of a new validation session"""
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
        """Log the end of a validation session"""
        logger = cls.get_logger("session")
        
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"VALIDATION SESSION COMPLETED - STATUS: {status}")
        if duration:
            logger.info(f"Total duration: {duration:.2f} seconds")
        logger.info(f"Session end time: {datetime.now().isoformat()}")
        logger.info("=" * 80)


class PerformanceLogger:
    """Logger for performance metrics and timing"""
    
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
    """Logger for data-related operations and statistics"""
    
    @staticmethod
    def log_data_stats(operation: str, dataframe_shape: tuple, file_path: str = None):
        """Log DataFrame statistics"""
        logger = LoggingConfig.get_logger("data")
        rows, cols = dataframe_shape
        message = f"{operation} - DataFrame: {rows} rows × {cols} columns"
        if file_path:
            message += f" from {file_path}"
        logger.info(message)
    
    @staticmethod
    def log_data_validation(validation_type: str, passed: bool, details: str = None):
        """Log data validation results"""
        logger = LoggingConfig.get_logger("validation")
        status = "PASSED" if passed else "FAILED"
        message = f"Data validation {validation_type}: {status}"
        if details:
            message += f" - {details}"
        
        if passed:
            logger.info(message)
        else:
            logger.error(message)
