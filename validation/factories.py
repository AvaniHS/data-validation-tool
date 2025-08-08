"""
Factory classes for creating data processors.
Enables easy extension for new file types and follows the Factory pattern.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Type, Optional
import pandas as pd

from readers.reader_contract import IDataReader
from readers.csv_reader import CSVReader
from readers.excel_reader import ExcelReader
from writers.csv_writer import CSVFileWriter
from writers.excel_writer import ExcelFileWriter
from validation.file_validators import FileValidator, StrictFileValidator, PermissiveFileValidator
from validation.contracts.data_aggregator_contracts import IAggregator
from validation.contracts.data_comparer_contracts import IDataComparer
from validation.contracts.data_joiner_contracts import IDataJoiner
from validation.contracts.data_preparer_contracts import IDataPreparer
from validation.contracts.output_writer_contracts import IOutputWriter
from validation.contracts.configuration_service_contracts import IConfigurationService
from validation.contracts.data_aggregator_contracts import IAggregationConfigValidator, IAggregationConfigExtractor, IAggregationExecutor, IAggregationResultValidator
from validation.contracts.data_comparer_contracts import IComparisonStrategy, IComparisonExecutor, IComparisonResultValidator
from validation.contracts.data_joiner_contracts import IJoinKeyExtractor, IJoinExecutor, IJoinResultValidator
from validation.contracts.data_preparer_contracts import IDataValidator, IDataLoader, IDataCleaner, ITypeDetector
from validation.contracts.output_writer_contracts import IOutputConfigValidator, IOutputConfigExtractor, IDataFormatter, IFileWriter, IOutputResultValidator
from validation.contracts.configuration_service_contracts import IConfigurationService
from validation.data_aggregator import DataAggregator, AggregationConfigValidator, AggregationConfigExtractor, AggregationExecutor, AggregationResultValidator
from validation.data_comparer import DataComparer, ComparisonStrategySelector, ComparisonExecutor, ComparisonResultValidator
from validation.data_joiner import DataJoiner, JoinKeyExtractor, JoinExecutor, JoinResultValidator
from validation.data_preparer import DataPreparer, DataValidator, DataLoader, DataCleaner, TypeDetectionService
from validation.output_writer import OutputWriter, OutputConfigValidator, OutputConfigExtractor, DataFormatter, FileWriter, OutputResultValidator
from config_ops.configuration_service import ConfigurationService
from constants import CSV_EXTENSION, EXCEL_EXTENSIONS


class IDataReaderFactory(ABC):
    """Interface for data reader factory"""
    
    @abstractmethod
    def create_reader(self, file_path: str) -> IDataReader:
        """Create appropriate reader for the given file path"""
        pass


class DataReaderFactory:
    """Factory for creating data readers based on file extension"""
    
    _readers: Dict[str, Type] = {
        CSV_EXTENSION: CSVReader,
        EXCEL_EXTENSIONS[0]: ExcelReader,  # .xlsx
        EXCEL_EXTENSIONS[1]: ExcelReader   # .xls
    }
    
    @classmethod
    def create_reader(cls, file_path: str):
        """Create appropriate reader based on file extension"""
        import os
        _, ext = os.path.splitext(file_path)
        
        if ext not in cls._readers:
            raise ValueError(f"Unsupported file extension: {ext}")
        
        return cls._readers[ext]()
    
    def register_reader(self, file_extension: str, reader_class: Type[IDataReader]) -> None:
        """
        Register a new reader for a file extension
        
        Args:
            file_extension: File extension (e.g., '.json')
            reader_class: Reader class to register
        """
        self._readers[file_extension.lower()] = reader_class


class IDataWriterFactory(ABC):
    """Interface for data writer factory"""
    
    @abstractmethod
    def create_writer(self, file_path: str) -> Any:
        """Create appropriate writer for the given file path"""
        pass


class DataWriterFactory:
    """Factory for creating data writers based on file extension"""
    
    _writers: Dict[str, Type] = {
        CSV_EXTENSION: CSVFileWriter,
        EXCEL_EXTENSIONS[0]: ExcelFileWriter,  # .xlsx
        EXCEL_EXTENSIONS[1]: ExcelFileWriter   # .xls
    }
    
    @classmethod
    def create_writer(cls, file_path: str):
        """Create appropriate writer based on file extension"""
        import os
        _, ext = os.path.splitext(file_path)
        
        if ext not in cls._writers:
            raise ValueError(f"Unsupported file extension: {ext}")
        
        return cls._writers[ext]()
    
    def register_writer(self, file_extension: str, writer_class: Type) -> None:
        """
        Register a new writer for a file extension
        
        Args:
            file_extension: File extension (e.g., '.json')
            writer_class: Writer class to register
        """
        self._writers[file_extension.lower()] = writer_class


class IFileValidatorFactory(ABC):
    """Interface for file validator factory"""
    
    @abstractmethod
    def create_validator(self, file_path: str) -> FileValidator:
        """Create appropriate validator for the given file path"""
        pass


class FileValidatorFactory:
    """Factory for creating file validators based on file extension"""
    
    _validators: Dict[str, Type] = {
        CSV_EXTENSION: FileValidator,
        EXCEL_EXTENSIONS[0]: FileValidator,  # .xlsx
        EXCEL_EXTENSIONS[1]: FileValidator   # .xls
    }
    
    @classmethod
    def create_validator(cls, file_path: str):
        """Create appropriate validator based on file extension"""
        import os
        _, ext = os.path.splitext(file_path)
        
        if ext not in cls._validators:
            raise ValueError(f"Unsupported file extension: {ext}")
        
        return cls._validators[ext]()
    
    def register_validator(self, file_extension: str, validator_class: Type[FileValidator]) -> None:
        """
        Register a new validator for a file extension
        
        Args:
            file_extension: File extension (e.g., '.json')
            validator_class: Validator class to register
        """
        self._validators[file_extension.lower()] = validator_class


class AggregatorFactory:
    """Factory for creating data aggregators"""
    
    @staticmethod
    def create_aggregator() -> IAggregator:
        """Create a data aggregator instance"""
        return DataAggregator()
    
    @staticmethod
    def create_aggregation_config_validator() -> IAggregationConfigValidator:
        """Create an aggregation config validator instance"""
        return AggregationConfigValidator()
    
    @staticmethod
    def create_aggregation_config_extractor() -> IAggregationConfigExtractor:
        """Create an aggregation config extractor instance"""
        return AggregationConfigExtractor()
    
    @staticmethod
    def create_aggregation_executor() -> IAggregationExecutor:
        """Create an aggregation executor instance"""
        return AggregationExecutor()
    
    @staticmethod
    def create_aggregation_result_validator() -> IAggregationResultValidator:
        """Create an aggregation result validator instance"""
        return AggregationResultValidator()


class ComparerFactory:
    """Factory for creating data comparers"""
    
    @staticmethod
    def create_comparer() -> IDataComparer:
        """Create a data comparer instance"""
        return DataComparer()
    
    @staticmethod
    def create_comparison_strategy() -> IComparisonStrategy:
        """Create a comparison strategy instance"""
        return ComparisonStrategySelector()
    
    @staticmethod
    def create_comparison_executor() -> IComparisonExecutor:
        """Create a comparison executor instance"""
        return ComparisonExecutor()
    
    @staticmethod
    def create_comparison_result_validator() -> IComparisonResultValidator:
        """Create a comparison result validator instance"""
        return ComparisonResultValidator()


class JoinerFactory:
    """Factory for creating data joiners"""
    
    @staticmethod
    def create_joiner() -> IDataJoiner:
        """Create a data joiner instance"""
        return DataJoiner()
    
    @staticmethod
    def create_join_strategy() -> IJoinKeyExtractor:
        """Create a join strategy instance"""
        return JoinKeyExtractor()
    
    @staticmethod
    def create_join_executor() -> IJoinExecutor:
        """Create a join executor instance"""
        return JoinExecutor()
    
    @staticmethod
    def create_join_result_validator() -> IJoinResultValidator:
        """Create a join result validator instance"""
        return JoinResultValidator()


class PreparerFactory:
    """Factory for creating data preparers"""
    
    @staticmethod
    def create_preparer() -> IDataPreparer:
        """Create a data preparer instance"""
        return DataPreparer()
    
    @staticmethod
    def create_data_validator() -> IDataValidator:
        """Create a data validator instance"""
        return DataValidator()
    
    @staticmethod
    def create_data_loader() -> IDataLoader:
        """Create a data loader instance"""
        return DataLoader()
    
    @staticmethod
    def create_data_cleaner() -> IDataCleaner:
        """Create a data cleaner instance"""
        return DataCleaner()
    
    @staticmethod
    def create_type_detector() -> ITypeDetector:
        """Create a type detector instance"""
        return TypeDetector()


class OutputWriterFactory:
    """Factory for creating output writers"""
    
    @staticmethod
    def create_output_writer() -> IOutputWriter:
        """Create an output writer instance"""
        return OutputWriter()
    
    @staticmethod
    def create_output_config_validator() -> IOutputConfigValidator:
        """Create an output config validator instance"""
        return OutputConfigValidator()
    
    @staticmethod
    def create_output_config_extractor() -> IOutputConfigExtractor:
        """Create an output config extractor instance"""
        return OutputConfigExtractor()
    
    @staticmethod
    def create_data_formatter() -> IDataFormatter:
        """Create a data formatter instance"""
        return DataFormatter()
    
    @staticmethod
    def create_file_writer() -> IFileWriter:
        """Create a file writer instance"""
        return FileWriter()
    
    @staticmethod
    def create_output_result_validator() -> IOutputResultValidator:
        """Create an output result validator instance"""
        return OutputResultValidator()


class ConfigurationServiceFactory:
    """Factory for creating configuration services"""
    
    @staticmethod
    def create_configuration_service() -> IConfigurationService:
        """Create a configuration service instance"""
        return ConfigurationService()
    
    @staticmethod
    def create_configuration_service() -> IConfigurationService:
        """Create a configuration service instance"""
        return ConfigurationService() 