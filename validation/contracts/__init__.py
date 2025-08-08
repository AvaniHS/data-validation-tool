"""
Contracts package for validation modules.
Contains all contract definitions separated from implementations.
"""

from .data_preparer_contracts import (
    IDataValidator,
    IDataLoader,
    IDataCleaner,
    ITypeDetector,
    IDataPreparer
)

from .data_joiner_contracts import (
    IJoinKeyExtractor,
    IJoinKeyValidator,
    IJoinExecutor,
    IJoinResultValidator,
    IDataJoiner
)

from .data_aggregator_contracts import (
    IAggregationStrategy,
    IAggregationConfigValidator,
    IAggregationConfigExtractor,
    IAggregationExecutor,
    IAggregationResultValidator,
    IAggregator
)

from .data_comparer_contracts import (
    IComparisonStrategy,
    IComparisonConfigValidator,
    IComparisonConfigExtractor,
    IComparisonStrategySelector,
    IComparisonExecutor,
    IComparisonResultValidator,
    IDataComparer
)

from .output_writer_contracts import (
    IOutputConfigValidator,
    IOutputConfigExtractor,
    IDataFormatter,
    IFileWriter,
    IOutputResultValidator,
    IOutputWriter
)

from .configuration_service_contracts import (
    IConfigurationService
)

__all__ = [
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
    'IComparisonConfigValidator',
    'IComparisonConfigExtractor',
    'IComparisonStrategySelector',
    'IComparisonExecutor',
    'IComparisonResultValidator',
    'IDataComparer',
    
    # Output Writer Contracts
    'IOutputConfigValidator',
    'IOutputConfigExtractor',
    'IDataFormatter',
    'IFileWriter',
    'IOutputResultValidator',
    'IOutputWriter',
    
    # Configuration Service Contracts
    'IConfigurationService'
] 