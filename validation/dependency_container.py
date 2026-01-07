from typing import Dict, Any
from validation.data_preparer import DataPreparer
from validation.data_joiner import DataJoiner
from validation.data_aggregator import DataAggregator
from validation.data_comparer import DataComparer
from validation.output_writer import OutputWriter
from config_ops import ConfigProcessor, ConfigurationService
from validation.contracts import (
    IDataPreparer,
    IDataJoiner,
    IAggregator,
    IDataComparer,
    IOutputWriter,
    IConfigurationService
)


class DependencyContainer:
    
    def __init__(self):
        self._registered_services: Dict[str, Any] = {}
        self._initialize_services()
    
    def _initialize_services(self) -> None:
        self._registered_services[IDataPreparer] = DataPreparer()
        self._registered_services[IDataJoiner] = DataJoiner()
        self._registered_services[IAggregator] = DataAggregator()
        self._registered_services[IDataComparer] = DataComparer()
        self._registered_services[IOutputWriter] = OutputWriter()
        self._registered_services[ConfigProcessor] = ConfigProcessor()
        self._registered_services[IConfigurationService] = ConfigurationService()
    
    def get_service(self, service_type: type) -> Any:
        if service_type not in self._registered_services:
            raise KeyError(f"Service type {service_type.__name__} is not registered")
        return self._registered_services[service_type]
    
    def get_pipeline_orchestrator(self):
        from validation.pipeline_orchestrator import IPipelineOrchestrator, ValidationPipelineOrchestrator
        
        if IPipelineOrchestrator not in self._registered_services:
            orchestrator = ValidationPipelineOrchestrator(
                data_preparer=self._registered_services[IDataPreparer],
                data_joiner=self._registered_services[IDataJoiner],
                data_aggregator=self._registered_services[IAggregator],
                data_comparer=self._registered_services[IDataComparer],
                output_writer=self._registered_services[IOutputWriter],
                config_processor=self._registered_services[IConfigurationService]
            )
            self._registered_services[IPipelineOrchestrator] = orchestrator
        
        return self._registered_services[IPipelineOrchestrator]
    
    def register_service(self, service_type: type, service_instance: Any) -> None:
        self._registered_services[service_type] = service_instance
    
    def reset(self) -> None:
        self._registered_services.clear()
        self._initialize_services()


_global_container = DependencyContainer()


def get_container() -> DependencyContainer:
    return _global_container


def get_pipeline_orchestrator():
    return _global_container.get_pipeline_orchestrator()


def register_service(service_type: type, service_instance: Any) -> None:
    _global_container.register_service(service_type, service_instance) 