"""User interaction messages and help text."""

def get_help_examples() -> str:
    """Return help examples text."""
    return """
Examples:
  python run_validation.py --config config.json
  
  python run_validation.py --sample-config
  
  python run_validation.py
  
  python run_validation.py --config tests/sample/config_two_csv_files.json
        """

def get_interactive_mode_welcome() -> str:
    """Return interactive mode welcome message."""
    return """🚀 Starting Data Validation Tool in Interactive Mode
============================================================="""

def get_exit_message() -> str:
    """Return exit message."""
    return "👋 Exiting..."

def get_config_not_found_error(config_file: str) -> str:
    """Return configuration file not found error message."""
    return f"❌ Error: Configuration file not found: {config_file}"

def get_sample_config_header() -> str:
    """Return sample configuration header."""
    return """Sample Configuration Format:
=================================================="""

def get_sample_config_footer() -> str:
    """Return sample configuration footer."""
    return "\nFor more examples, see files in tests/sample/ directory"
