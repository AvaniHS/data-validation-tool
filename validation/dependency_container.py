"""
Dependency Injection Container for Data Validation Tool.
Manages all dependencies and provides clean instantiation of services.
"""

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
    """Dependency injection container for the validation tool"""
    
    def __init__(self):
        """Initialize the dependency container"""
        self._services: Dict[str, Any] = {}
        self._configure_services()
    
    def _configure_services(self) -> None:
        """Configure all services in the container"""
        # Register core services
        self._services[IDataPreparer] = DataPreparer()
        self._services[IDataJoiner] = DataJoiner()
        self._services[IAggregator] = DataAggregator()
        self._services[IDataComparer] = DataComparer()
        self._services[IOutputWriter] = OutputWriter()
        self._services[ConfigProcessor] = ConfigProcessor()
        self._services[IConfigurationService] = ConfigurationService()
    
    def get_service(self, service_type: type) -> Any:
        """
        Get a service by its type
        
        Args:
            service_type: Type of the service to retrieve
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service type is not registered
        """
        if service_type not in self._services:
            raise KeyError(f"Service type {service_type.__name__} is not registered")
        return self._services[service_type]
    
    def get_pipeline_orchestrator(self):
        """
        Get the pipeline orchestrator with lazy initialization
        
        Returns:
            Pipeline orchestrator instance
        """
        # Import here to avoid circular imports
        from validation.pipeline_orchestrator import IPipelineOrchestrator, ValidationPipelineOrchestrator
        
        # Check if orchestrator is already registered
        if IPipelineOrchestrator not in self._services:
            # Create orchestrator with all dependencies
            orchestrator = ValidationPipelineOrchestrator(
                data_preparer=self._services[IDataPreparer],
                data_joiner=self._services[IDataJoiner],
                data_aggregator=self._services[IAggregator],
                data_comparer=self._services[IDataComparer],
                output_writer=self._services[IOutputWriter],
                config_processor=self._services[IConfigurationService]
            )
            self._services[IPipelineOrchestrator] = orchestrator
        
        return self._services[IPipelineOrchestrator]
    
    def register_service(self, service_type: type, service_instance: Any) -> None:
        """
        Register a new service or override existing one
        
        Args:
            service_type: Type of the service
            service_instance: Service instance
        """
        self._services[service_type] = service_instance
    
    def reset(self) -> None:
        """Reset the container and reconfigure services"""
        self._services.clear()
        self._configure_services()


# Global container instance
_container = DependencyContainer()


def get_container() -> DependencyContainer:
    """Get the global dependency container"""
    return _container


def get_pipeline_orchestrator():
    """Get the pipeline orchestrator from the global container"""
    return _container.get_pipeline_orchestrator()


def register_service(service_type: type, service_instance: Any) -> None:
    """Register a service in the global container"""
    _container.register_service(service_type, service_instance) 