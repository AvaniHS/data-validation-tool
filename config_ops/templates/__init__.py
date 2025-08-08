"""Configuration templates module."""

from .configuration_template import get_configuration_template
from .configuration_guidelines import get_configuration_guidelines
from .README import get_templates_readme

__all__ = [
    'get_configuration_template',
    'get_configuration_guidelines', 
    'get_templates_readme'
] 