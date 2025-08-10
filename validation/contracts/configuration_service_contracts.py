from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd


class IConfigurationService(ABC):
    
    @abstractmethod
    def load_configuration(self, config_path: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def enrich_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def process_configuration(self, config_path: str) -> Dict[str, Any]:
        pass 