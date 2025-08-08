"""Validator factory for easy validator registration and management."""

from typing import Dict, Type
from .validation_base import BaseValidator
from .validators import FileValidator, SchemaValidator, DataValidator, OutputValidator


class ValidatorFactory:
    """Factory for creating and managing validators."""
    
    def __init__(self):
        self._validators: Dict[str, Type[BaseValidator]] = {}
        self._register_default_validators()
    
    def _register_default_validators(self) -> None:
        """Register default validators."""
        self.register_validator('file', FileValidator)
        self.register_validator('schema', SchemaValidator)
        self.register_validator('data', DataValidator)
        self.register_validator('output', OutputValidator)
    
    def register_validator(self, name: str, validator_class: Type[BaseValidator]) -> None:
        """Register a new validator."""
        self._validators[name] = validator_class
    
    def get_validator(self, name: str) -> BaseValidator:
        """Get a validator instance by name."""
        if name not in self._validators:
            raise ValueError(f"Unknown validator: {name}")
        return self._validators[name]()
    
    def get_all_validators(self) -> Dict[str, BaseValidator]:
        """Get all registered validators as instances."""
        return {name: self.get_validator(name) for name in self._validators}
    
    def get_validator_names(self) -> list[str]:
        """Get list of registered validator names."""
        return list(self._validators.keys())
    
    def remove_validator(self, name: str) -> None:
        """Remove a validator."""
        if name in self._validators:
            del self._validators[name] 