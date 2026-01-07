from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd


class IValidator(ABC):
    
    @abstractmethod
    def validate(self, config: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def add_error(self, message: str) -> None:
        pass
    
    @abstractmethod
    def add_warning(self, message: str) -> None:
        pass
    
    @abstractmethod
    def has_errors(self) -> bool:
        pass
    
    @abstractmethod
    def get_errors(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_warnings(self) -> List[str]:
        pass
    
    @abstractmethod
    def clear(self) -> None:
        pass


class IFileValidator(IValidator):
    
    @abstractmethod
    def validate_file_exists(self, file_path: str, file_label: str) -> bool:
        pass
    
    @abstractmethod
    def validate_file_readable(self, file_path: str, file_label: str) -> bool:
        pass


class IConfigValidator(IValidator):
    
    @abstractmethod
    def validate_required_fields(self, config: Dict[str, Any], required_fields: List[str]) -> bool:
        pass
    
    @abstractmethod
    def validate_field_type(self, config: Dict[str, Any], field: str, expected_type: type) -> bool:
        pass
    
    @abstractmethod
    def validate_field_value(self, config: Dict[str, Any], field: str, valid_values: List[Any]) -> bool:
        pass 