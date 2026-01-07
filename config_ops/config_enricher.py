import json
from typing import Dict, Any
from constants import DEFAULT_OUTPUT_PATH, DEFAULT_OUTPUT_SHEET, DEFAULT_NA_VALUE


class ConfigEnricher:
    
    @staticmethod
    def enrich_config(config: Dict[str, Any]) -> Dict[str, Any]:
        enriched_config = config.copy()
        
        ConfigEnricher._set_defaults(enriched_config)
        ConfigEnricher._cleanup_data(enriched_config)
        
        return enriched_config
    
    @staticmethod
    def _set_defaults(config: Dict[str, Any]) -> None:
        config.setdefault('output_path', DEFAULT_OUTPUT_PATH)
        config.setdefault('output_sheet', DEFAULT_OUTPUT_SHEET)
    
    @staticmethod
    def _cleanup_data(config: Dict[str, Any]) -> None:
        if config.get('join_keys') == DEFAULT_NA_VALUE:
            config['join_keys'] = {}
        
        if config.get('aggregation') == DEFAULT_NA_VALUE:
            config['aggregation'] = {}
    
    @staticmethod
    def extract_file_paths(config: Dict[str, Any]) -> tuple[str, str | None]:
        file1 = config['file1_path']
        file2 = config.get('file2_path') if config['number_of_files'] == 2 else None
        return file1, file2 