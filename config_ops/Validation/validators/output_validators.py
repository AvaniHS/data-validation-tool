"""Output path validation."""

import os
from typing import Dict, Any
from ..validation_base import BaseValidator, ConfigValidatorMixin
from constants import DEFAULT_OUTPUT_PATH


class OutputValidator(BaseValidator, ConfigValidatorMixin):
    """Validates output path and creates directories if needed."""
    
    def validate(self, config: Dict[str, Any]) -> None:
        self.clear()
        self._validate_output_path(config)
    
    def _validate_output_path(self, config: Dict[str, Any]) -> None:
        output_path = config.get('output_path', DEFAULT_OUTPUT_PATH)
        output_dir = os.path.dirname(output_path)
        
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                self.add_warning(f"Created output directory: {output_dir}")
            except Exception as e:
                self.add_error(f"Failed to create output directory {output_dir}: {str(e)}")
                return
        
        if os.path.exists(output_path):
            if not os.access(output_path, os.W_OK):
                self.add_error(f"Permission denied: Cannot write to output file {output_path}")
                return
            self.add_warning(f"Output file already exists: {output_path}. The file will be overwritten.")
        else:
            if output_dir and not os.access(output_dir, os.W_OK):
                self.add_error(f"Permission denied: Cannot write to directory {output_dir}") 