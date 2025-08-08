"""
Configuration service contracts.
Separated from implementations to follow proper design principles.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd


class IConfigurationService(ABC):
    """Contract for configuration service operations"""
    
    @abstractmethod
    def load_configuration(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        pass
    
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """Validate configuration"""
        pass
    
    @abstractmethod
    def enrich_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich configuration with additional information"""
        pass
    
    @abstractmethod
    def process_configuration(self, config_path: str) -> Dict[str, Any]:
        """Process configuration (load, validate, enrich)"""
        pass 