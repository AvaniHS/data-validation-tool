"""
Data Validation Tool - Main Package
"""

# Export exceptions
from .exceptions import (
    FileOperationError,
    FileValidationError,
    ConfigValidationError,
    DataValidationError,
    DataPreparationError,
    DataJoiningError,
    DataAggregationError,
    DataComparisonError,
    OutputWritingError,
    PipelineExecutionError,
    FileNotFoundError,
    InvalidConfigurationError
)

# Export pipeline orchestrator components
from .pipeline_orchestrator import (
    ValidationPipelineOrchestrator,
    IPipelineOrchestrator,
    PipelineResult
)

# Export dependency injection components
from .dependency_container import (
    DependencyContainer,
    get_container,
    get_pipeline_orchestrator,
    register_service
)

# Export factory components
from .factories import (
    DataReaderFactory,
    DataWriterFactory,
    FileValidatorFactory,
    AggregatorFactory,
    ComparerFactory,
    JoinerFactory,
    PreparerFactory,
    OutputWriterFactory,
    ConfigurationServiceFactory
)

# Export contracts
from .contracts import (
    # Data Preparer Contracts
    IDataValidator,
    IDataLoader,
    IDataCleaner,
    ITypeDetector,
    IDataPreparer,
    
    # Data Joiner Contracts
    IJoinKeyExtractor,
    IJoinKeyValidator,
    IJoinExecutor,
    IJoinResultValidator,
    IDataJoiner,
    
    # Data Aggregator Contracts
    IAggregationStrategy,
    IAggregationConfigValidator,
    IAggregationConfigExtractor,
    IAggregationExecutor,
    IAggregationResultValidator,
    IAggregator,
    
    # Data Comparer Contracts
    IComparisonStrategy,
    IDataComparer,
    
    # Output Writer Contracts
    IOutputWriter
)

__all__ = [
    # Exceptions
    'FileOperationError',
    'FileValidationError',
    'ConfigValidationError',
    'DataValidationError',
    'DataPreparationError',
    'DataJoiningError',
    'DataAggregationError',
    'DataComparisonError',
    'OutputWritingError',
    'PipelineExecutionError',
    'FileNotFoundError',
    'InvalidConfigurationError',
    
    # Pipeline Orchestrator
    'ValidationPipelineOrchestrator',
    'IPipelineOrchestrator',
    'PipelineResult',
    
    # Dependency Injection
    'DependencyContainer',
    'get_container',
    'get_pipeline_orchestrator',
    'register_service',
    
    # Factories
    'DataReaderFactory',
    'DataWriterFactory',
    'FileValidatorFactory',
    'AggregatorFactory',
    'ComparerFactory',
    'JoinerFactory',
    'PreparerFactory',
    'OutputWriterFactory',
    'ConfigurationServiceFactory',
    
    # Data Preparer Contracts
    'IDataValidator',
    'IDataLoader',
    'IDataCleaner',
    'ITypeDetector',
    'IDataPreparer',
    
    # Data Joiner Contracts
    'IJoinKeyExtractor',
    'IJoinKeyValidator',
    'IJoinExecutor',
    'IJoinResultValidator',
    'IDataJoiner',
    
    # Data Aggregator Contracts
    'IAggregationStrategy',
    'IAggregationConfigValidator',
    'IAggregationConfigExtractor',
    'IAggregationExecutor',
    'IAggregationResultValidator',
    'IAggregator',
    
    # Data Comparer Contracts
    'IComparisonStrategy',
    'IDataComparer',
    
    # Output Writer Contracts
    'IOutputWriter'
]
