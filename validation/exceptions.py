class FileOperationError(Exception):
    pass


class FileValidationError(Exception):
    pass


class ConfigValidationError(Exception):
    pass


class DataValidationError(Exception):
    pass


class DataPreparationError(Exception):
    pass


class DataJoiningError(Exception):
    pass


class DataAggregationError(Exception):
    pass


class DataComparisonError(Exception):
    pass


class OutputWritingError(Exception):
    pass


class PipelineExecutionError(Exception):
    pass


class FileNotFoundError(Exception):
    """Exception raised when a file is not found"""
    pass


class InvalidConfigurationError(Exception):
    """Exception raised when configuration is invalid"""
    pass 