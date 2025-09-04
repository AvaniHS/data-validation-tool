from abc import ABC, abstractmethod
from typing import Dict, Any, Type, Optional
import pandas as pd

from readers.reader_contract import IDataReader
from readers.csv_reader import CSVReader
from readers.excel_reader import ExcelReader
from readers.json_reader import JSONReader
from writers.csv_writer import CSVFileWriter
from writers.excel_writer import ExcelFileWriter
from writers.json_writer import JSONFileWriter
from validation.file_validators import FileValidator, StrictFileValidator, PermissiveFileValidator
from validation.contracts.data_aggregator_contracts import IAggregator
from validation.contracts.data_comparer_contracts import IDataComparer
from validation.contracts.data_joiner_contracts import IDataJoiner
from validation.contracts.data_preparer_contracts import IDataPreparer
from validation.contracts.output_writer_contracts import IOutputWriter
from validation.contracts.configuration_service_contracts import IConfigurationService
from validation.contracts.data_aggregator_contracts import IAggregationConfigValidator, IAggregationConfigExtractor, IAggregationExecutor, IAggregationResultValidator
from validation.interfaces.comparison_strategies import IComparisonStrategy, IComparisonExecutor, IComparisonResultValidator
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
from constants import CSV_EXTENSION, JSON_EXTENSION, EXCEL_EXTENSIONS


class IDataReaderFactory(ABC):
    
    @abstractmethod
    def create_reader(self, file_path: str) -> IDataReader:
        pass


class DataReaderFactory:
    
    _supported_readers: Dict[str, Type] = {
        CSV_EXTENSION: CSVReader,
        JSON_EXTENSION: JSONReader,
        EXCEL_EXTENSIONS[0]: ExcelReader,
        EXCEL_EXTENSIONS[1]: ExcelReader
    }
    
    @classmethod
    def create_reader(cls, file_path: str):
        import os
        _, file_extension = os.path.splitext(file_path)
        
        if file_extension not in cls._supported_readers:
            raise ValueError(f"Unsupported file extension: {file_extension}")
        
        return cls._supported_readers[file_extension]()
    
    def register_reader(self, file_extension: str, reader_class: Type[IDataReader]) -> None:
        self._supported_readers[file_extension.lower()] = reader_class


class IDataWriterFactory(ABC):
    
    @abstractmethod
    def create_writer(self, file_path: str) -> Any:
        pass


class DataWriterFactory:
    
    _supported_writers: Dict[str, Type] = {
        CSV_EXTENSION: CSVFileWriter,
        JSON_EXTENSION: JSONFileWriter,
        EXCEL_EXTENSIONS[0]: ExcelFileWriter,
        EXCEL_EXTENSIONS[1]: ExcelFileWriter
    }
    
    @classmethod
    def create_writer(cls, file_path: str):
        import os
        _, file_extension = os.path.splitext(file_path)
        
        if file_extension not in cls._supported_writers:
            raise ValueError(f"Unsupported file extension: {file_extension}")
        
        return cls._supported_writers[file_extension]()
    
    def register_writer(self, file_extension: str, writer_class: Type) -> None:
        self._supported_writers[file_extension.lower()] = writer_class


class IFileValidatorFactory(ABC):
    
    @abstractmethod
    def create_validator(self, file_path: str) -> FileValidator:
        pass


class FileValidatorFactory:
    
    _supported_validators: Dict[str, Type] = {
        CSV_EXTENSION: FileValidator,
        EXCEL_EXTENSIONS[0]: FileValidator,
        EXCEL_EXTENSIONS[1]: FileValidator
    }
    
    @classmethod
    def create_validator(cls, file_path: str):
        import os
        _, file_extension = os.path.splitext(file_path)
        
        if file_extension not in cls._supported_validators:
            raise ValueError(f"Unsupported file extension: {file_extension}")
        
        return cls._supported_validators[file_extension]()
    
    def register_validator(self, file_extension: str, validator_class: Type[FileValidator]) -> None:
        self._supported_validators[file_extension.lower()] = validator_class


class AggregatorFactory:
    
    @staticmethod
    def create_aggregator() -> IAggregator:
        return DataAggregator()
    
    @staticmethod
    def create_aggregation_config_validator() -> IAggregationConfigValidator:
        return AggregationConfigValidator()
    
    @staticmethod
    def create_aggregation_config_extractor() -> IAggregationConfigExtractor:
        return AggregationConfigValidator()
    
    @staticmethod
    def create_aggregation_executor() -> IAggregationExecutor:
        return AggregationExecutor()
    
    @staticmethod
    def create_aggregation_result_validator() -> IAggregationResultValidator:
        return AggregationResultValidator()


class ComparerFactory:
    
    @staticmethod
    def create_comparer() -> IDataComparer:
        return DataComparer()
    
    @staticmethod
    def create_comparison_strategy() -> IComparisonStrategy:
        return ComparisonStrategySelector()
    
    @staticmethod
    def create_comparison_executor() -> IComparisonExecutor:
        return ComparisonExecutor()
    
    @staticmethod
    def create_comparison_result_validator() -> IComparisonResultValidator:
        return ComparisonResultValidator()


class JoinerFactory:
    
    @staticmethod
    def create_joiner() -> IDataJoiner:
        return DataJoiner()
    
    @staticmethod
    def create_join_strategy() -> IJoinKeyExtractor:
        return JoinKeyExtractor()
    
    @staticmethod
    def create_join_executor() -> IJoinExecutor:
        return JoinExecutor()
    
    @staticmethod
    def create_join_result_validator() -> IJoinResultValidator:
        return JoinResultValidator()


class PreparerFactory:
    
    @staticmethod
    def create_preparer() -> IDataPreparer:
        return DataPreparer()
    
    @staticmethod
    def create_data_validator() -> IDataValidator:
        return DataValidator()
    
    @staticmethod
    def create_data_loader() -> IDataLoader:
        return DataLoader()
    
    @staticmethod
    def create_data_cleaner() -> IDataCleaner:
        return DataCleaner()
    
    @staticmethod
    def create_type_detector() -> ITypeDetector:
        return TypeDetectionService()


class OutputWriterFactory:
    
    @staticmethod
    def create_output_writer() -> IOutputWriter:
        return OutputWriter()
    
    @staticmethod
    def create_output_config_validator() -> IOutputConfigValidator:
        return OutputConfigValidator()
    
    @staticmethod
    def create_output_config_extractor() -> IOutputConfigExtractor:
        return OutputConfigExtractor()
    
    @staticmethod
    def create_data_formatter() -> IDataFormatter:
        return DataFormatter()
    
    @staticmethod
    def create_file_writer() -> IFileWriter:
        return FileWriter()
    
    @staticmethod
    def create_output_result_validator() -> IOutputResultValidator:
        return OutputResultValidator()


class ConfigurationServiceFactory:
    
    @staticmethod
    def create_configuration_service() -> IConfigurationService:
        return ConfigurationService() 