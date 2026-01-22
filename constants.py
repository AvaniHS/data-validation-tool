SUPPORTED_EXTENSIONS = ['.csv', '.xlsx', '.xls', '.json']
VALID_FILE_FORMATS = ['.csv', '.xlsx', '.json', 'mixed']
CSV_EXTENSION = '.csv'
JSON_EXTENSION = '.json'
EXCEL_EXTENSIONS = ['.xlsx', '.xls']

VALID_NUMBER_OF_FILES = [1, 2]

VALID_AGGREGATION_TYPES = ['sum', 'avg', 'count', 'min', 'max']
AGGREGATION_SUM = 'sum'
AGGREGATION_AVG = 'avg'
AGGREGATION_COUNT = 'count'
AGGREGATION_MIN = 'min'
AGGREGATION_MAX = 'max'

# Aggregation Step Constants
AGGREGATION_STEP_FILE1 = 'file1'
AGGREGATION_STEP_FILE2 = 'file2'
AGGREGATION_STEP_FINAL = 'final'
VALID_AGGREGATION_STEPS = [AGGREGATION_STEP_FILE1, AGGREGATION_STEP_FILE2, AGGREGATION_STEP_FINAL]

# Aggregation Configuration Keys
AGGREGATION_CONFIG_FILE1_COLUMNS = 'file1_columns'
AGGREGATION_CONFIG_FILE2_COLUMNS = 'file2_columns'
AGGREGATION_CONFIG_FINAL_COLUMNS = 'final_aggregated_columns'
AGGREGATION_CONFIG_FILE1_GROUPBY = 'file1_groupby_columns'
AGGREGATION_CONFIG_FILE2_GROUPBY = 'file2_groupby_columns'
AGGREGATION_CONFIG_FINAL_GROUPBY = 'final_groupby_columns'
AGGREGATION_CONFIG_GROUPBY = 'groupby_columns'

DEFAULT_OUTPUT_PATH = 'comparison_results.xlsx'
DEFAULT_OUTPUT_SHEET = 'Results'
DEFAULT_FILE1_SHEET1 = 'Sheet1'
DEFAULT_FILE1_SHEET2 = 'Sheet2'
DEFAULT_FILE2_SHEET = 'Sheet1'
DEFAULT_NA_VALUE = 'NA'

FILE_MODE_WRITE = 'w'
FILE_MODE_APPEND = 'a'
FILE_MODE_READ = 'r'

EXIT_COMMANDS = ['exit', 'quit', 'q']
EXIT_MESSAGE = "Type exit, quit, q to quit at any time."

USER_CHOICE_OVERWRITE = 'o'
USER_CHOICE_RENAME = 'r'
USER_CHOICE_YES = 'y'
USER_CHOICE_NO = 'n'
USER_CHOICE_ENTER = 'e'

YES_CHOICES = ['y', 'yes', '']
NO_CHOICES = ['n', 'no']
ENTER_CHOICES = ['e', 'enter']

COLUMN_CATEGORY_FILE_ONE = 'File One'
COLUMN_CATEGORY_FILE_TWO = 'File Two'
COLUMN_CATEGORY_COMPARISON = 'Comparison'

FILE_ONE_COLUMNS = ['customer_id', 'product_id', 'quantity', 'price']

FILE_TWO_COLUMNS = ['qty', 'amount', 'product_code']

COMPARISON_KEYWORDS = ['diff', 'delta', '_vs_']

VALIDATION_MESSAGES = {
    'CONFIG_VALIDATED': '✓ Configuration file validated successfully',
    'FILE_NOT_FOUND': 'File not found: {}',
    'INVALID_JSON': 'Invalid JSON format. Please enter a valid JSON mapping.',
    'MAPPING_MUST_BE_DICT': 'Mapping must be a JSON object (dictionary).',
    'INVALID_COLUMN_NUMBERS': 'Invalid column numbers. Please enter valid numbers.',
    'INVALID_FORMAT': 'Invalid format. Please enter comma-separated numbers (e.g., 1,3,5).',
    'REQUIRED_FIELD': 'This field is required. Please enter a value or type \'exit\' to quit.',
    'CONFIGURATION_ERROR': 'Configuration error: {}',
    'FIX_CONFIG_AND_RETRY': 'Please fix the configuration file and try again.'
}

CONSOLE_MESSAGES = {
    'WELCOME': 'DATA VALIDATION TOOL',
    'FILE_INPUT_SECTION': '=== File Input ===',
    'CONFIG_FILE_PROMPT': 'Enter path to configuration file:',
    'ADDITIONAL_COLUMNS_SECTION': '=== Additional Columns Selection ===',
    'DATASET_SUMMARY_HEADER': '=== DATASET SUMMARY ===',
    'DATASET_SUMMARY_FOOTER': '=== END SUMMARY ==='
}

# Pipeline Messages
PIPELINE_HEADER = "DATA VALIDATION PIPELINE"
PIPELINE_BORDER_WIDTH = 80
SAMPLE_CONFIG_HEADER = "Sample Configuration Format:"
SAMPLE_CONFIG_BORDER_WIDTH = 50
SAMPLE_CONFIG_FOOTER = "For more examples, see files in tests/sample/ directory"
INTERACTIVE_MODE_HEADER = "🚀 Starting Data Validation Tool in Interactive Mode"
INTERACTIVE_MODE_BORDER_WIDTH = 60
EXIT_MESSAGE = "👋 Exiting..."
CONFIG_FILE_NOT_FOUND = "Configuration file not found:"
VALIDATION_ERROR = "Error during validation:"

# Environment Variables
LOG_LEVEL_ENV = 'LOG_LEVEL'
LOG_DIR_ENV = 'LOG_DIR'
DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_LOG_DIR = 'logs'

# Exit Codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1

# Help Text
HELP_DESCRIPTION = "Data Validation Tool - Complete pipeline for data comparison and validation"
HELP_EXAMPLES = """
Examples:
  python run_validation.py --config config.json
  
  python run_validation.py --sample-config
  
  python run_validation.py
  
  python run_validation.py --config tests/sample/config_two_csv_files.json
"""

ERROR_MESSAGES = {
    'MISSING_REQUIRED_FIELDS': 'Missing required fields in configuration: {}',
    'INVALID_FILE_FORMAT': 'Invalid file_format: {}. Must be {}.',
    'INVALID_NUMBER_OF_FILES': 'Invalid number_of_files: {}. Must be {}.',
    'FILE2_PATH_REQUIRED': 'file2_path is required when number_of_files = 2',
    'FILE1_CSV_EXTENSION': 'file1_path must end with .csv when file_format = \'.csv\'',
    'FILE2_CSV_EXTENSION': 'file2_path must end with .csv when file_format = \'.csv\'',
    'FILE1_EXCEL_EXTENSION': 'file1_path must end with .xlsx when file_format = \'.xlsx\'',
    'FILE2_EXCEL_EXTENSION': 'file2_path must end with .xlsx when file_format = \'.xlsx\'',
    'FILE1_SHEET1_REQUIRED': 'file1_sheet1 is required when file_format = \'.xlsx\'',
    'FILE1_SHEET2_REQUIRED': 'file1_sheet2 is required when number_of_files = 1 and file_format = \'.xlsx\'',
    'FILE2_SHEET_REQUIRED': 'file2_sheet is required when file_format = \'.xlsx\' and number_of_files = 2',
    'INVALID_FILE_EXTENSION': '{} must end with .csv or .xlsx, got: {}',
    'SINGLE_FILE_EXCEL_ONLY': 'When number_of_files = 1, file_format must be \'.xlsx\' with two sheets',
    'FILE_NOT_FOUND': 'File not found: {}',
    'FILE_PERMISSION_DENIED': 'Permission denied: Cannot read file {}',
    'FILE_DIR_PERMISSION_DENIED': 'Permission denied: Cannot access directory {}',
    'OUTPUT_DIR_CREATION_FAILED': 'Failed to create output directory {}: {}',
    'OUTPUT_DIR_PERMISSION_DENIED': 'Permission denied: Cannot create/write to directory {}: {}',
    'OUTPUT_FILE_PERMISSION_DENIED': 'Permission denied: Cannot write to output file {}',
    'CONFIG_FILE_NOT_FOUND': 'Configuration file not found: {}',
    'CONFIG_FILE_PERMISSION_DENIED': 'Permission denied: Cannot read configuration file {}',
    'COLUMN_MAPPING_DICT': 'column_mapping must be a dictionary',
    'INVALID_JSON_FORMAT': 'Invalid JSON format in configuration file: {}',
    'CONFIGURATION_VALIDATION_ERROR': 'Configuration validation error: {}',
    'CONFIGURATION_ERROR': 'Configuration error: {}',
    'MISSING_AGGREGATION_KEY': 'Missing required aggregation key: {}',
    'AGGREGATION_MUST_BE_DICT': '{} must be a dictionary with aggregation types as keys',
    'AGGREGATION_COLUMN_DICT': '{} must be a dictionary with aggregation types as keys',
    'INVALID_AGGREGATION_TYPE': 'Invalid aggregation type \'{}\' in {}. Valid types: {}',
    'INVALID_AGGREGATION_VALUE': 'Invalid value for {}.{}. Must be \'NA\' or a list of column names.',
    'AGGREGATION_COLUMN_LIST': 'All column names in {}.{} must be strings',
    'GROUPBY_COLUMNS_INVALID': 'groupby_columns must be \'NA\' or a list of column names',
    'GROUPBY_COLUMN_LIST': 'All groupby_columns must be strings',
    'GROUPBY_COLUMN_VALUE': 'groupby_columns must be \'NA\' or a list of column names',
    'MISSING_GROUPBY_FIELD': 'Missing required groupby field: {}',
    'INVALID_GROUPBY_FIELD': 'Invalid groupby field: {}. Must be \'NA\' or a list of column names',
    'FINAL_AGGREGATION_INVALID': 'final_aggregated_columns must be a dictionary with aggregation types as keys',
    'ALL_COLUMNS_STRINGS': 'All column names in {}.{} must be strings',
    'ALL_GROUPBY_STRINGS': 'All groupby_columns must be strings',
    'INVALID_JOIN_KEY_TYPE': 'Invalid join key type \'{}\' for key \'{}\'. Must be \'numeric\', \'non_numeric\', or \'NA\'',
    'JOIN_KEYS_TYPES_MISMATCH': 'join_keys_types must have the same keys as join_keys'
}

EXAMPLE_MESSAGES = {
    'JSON_MAPPING_EXAMPLE': 'Example: {"column1": "column2", "column3": "column4"}',
    'COLUMN_NUMBERS_EXAMPLE': 'Example: 1,3,5 or just press Enter to skip',
    'EXIT_COMMAND': 'Type \'exit\' to quit'
}

PATHS = {
    'TEMPLATES_DIR': 'config_ops/templates/',
    'TESTS_SAMPLE_DIR': 'tests/sample/',
    'CONFIG_TEMPLATE': 'config_ops/templates/configuration_template.py',
    'CONFIG_GUIDELINES': 'config_ops/templates/configuration_guidelines.py',
    'DOWNLOADS_DIR': 'downloads',
    'CONFIG_TEMPLATE_JSON': 'config_template.json',
    'CONFIG_GUIDELINES_JSONC': 'config_guidelines.jsonc'
} 