"""Main configuration processor that orchestrates validation and enrichment."""

from typing import Dict, Any, List
from .Validation import ConfigValidator
from .config_enricher import ConfigEnricher
from constants import ERROR_MESSAGES, VALIDATION_MESSAGES


class ConfigProcessor:
    """Main configuration processor that orchestrates validation and enrichment."""
    
    @staticmethod
    def process_config_file(config_file_path: str) -> Dict[str, Any]:
        """Process configuration file: validate and enrich."""
        try:
            # Validate and load config
            validator = ConfigValidator()
            config = validator._validate_config_file(config_file_path)
            
            ConfigProcessor._print_warnings(validator.get_warnings())
            enriched_config = ConfigEnricher.enrich_config(config)
            
            print(VALIDATION_MESSAGES['CONFIG_VALIDATED'])
            return enriched_config
            
        except Exception as e:
            raise ValueError(ERROR_MESSAGES['CONFIGURATION_VALIDATION_ERROR'].format(str(e)))
    
    @staticmethod
    def _print_warnings(warnings: List[str]) -> None:
        """Print validation warnings."""
        for warning in warnings:
            print(f"⚠️  {warning}") 