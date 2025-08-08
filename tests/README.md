# Test Structure

This directory contains all tests for the Data Validation project, organized into logical categories for better maintainability.

## Directory Structure

```
tests/
├── __init__.py
├── run_tests.py              # Main test runner
├── README.md                 # This file
├── unit/                     # Unit tests for individual components
│   ├── __init__.py
│   ├── test_readers.py       # Tests for CSV/Excel readers
│   ├── test_writers.py       # Tests for CSV/Excel writers
│   ├── test_validation.py    # Tests for validation logic
│   └── test_strategies.py    # Tests for comparison strategies (removed - legacy)
├── integration/              # Integration tests
│   ├── __init__.py
│   └── test_workflow.py      # End-to-end workflow tests
├── user_interaction/         # User interaction tests
│   ├── __init__.py
│   └── test_scenarios.py     # Individual user scenarios
└── utils/                    # Test utilities and helpers
    ├── __init__.py
    └── test_helpers.py       # Common test utilities
```

## Test Categories

### Unit Tests (`unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single classes, methods, or functions
- **Dependencies**: Mocked external dependencies
- **Examples**: 
  - CSV reader functionality
  - Excel writer functionality
  - Validation logic
  - Data validation pipeline

### Integration Tests (`integration/`)
- **Purpose**: Test how components work together
- **Scope**: Multiple components interacting
- **Dependencies**: Real file I/O, but controlled test data
- **Examples**:
  - Complete workflow from input to output
  - File reading → validation → writing pipeline
  - Configuration processing and validation

### User Interaction Tests (`user_interaction/`)
- **Purpose**: Test interactive user scenarios
- **Scope**: User input handling and validation
- **Dependencies**: Mocked user input, controlled scenarios
- **Examples**:
  - Missing file prompts
  - Invalid input handling
  - Exit command handling
  - Retry logic

### Test Utilities (`utils/`)
- **Purpose**: Common testing helpers and utilities
- **Scope**: Reusable test functions and classes
- **Examples**:
  - Temporary file creation
  - Mock data generation
  - Common assertions

## Running Tests

### Run All Tests
```bash
python tests/run_tests.py
```

### Run Specific Test Categories
```bash
# Unit tests only
python tests/run_tests.py --type unit

# Integration tests only
python tests/run_tests.py --type integration

# User interaction tests only
python tests/run_tests.py --type user
```

### Run Individual Test Files
```bash
# Run a specific test file
python -m unittest tests/unit/test_readers.py

# Run with verbose output
python -m unittest tests/unit/test_readers.py -v
```

### Run Specific Test Classes or Methods
```bash
# Run a specific test class
python -m unittest tests.unit.test_readers.TestCSVReader

# Run a specific test method
python -m unittest tests.unit.test_readers.TestCSVReader.test_read_csv_file
```

## Test Guidelines

### Writing Unit Tests
1. **Isolation**: Each test should be independent
2. **Mocking**: Use mocks for external dependencies
3. **Naming**: Use descriptive test method names
4. **Assertions**: Test one thing per test method

### Writing Integration Tests
1. **Real Data**: Use realistic but controlled test data
2. **Cleanup**: Always clean up test files
3. **Scope**: Test complete workflows
4. **Error Handling**: Test both success and failure scenarios

### Writing User Interaction Tests
1. **Mocking**: Mock all user input
2. **Scenarios**: Test one scenario per test
3. **Validation**: Test input validation logic
4. **Error Recovery**: Test retry and exit logic

### Best Practices
1. **Setup/Teardown**: Use `setUp()` and `tearDown()` methods
2. **Temporary Files**: Use `tempfile` module for test files
3. **Cleanup**: Always clean up resources in `tearDown()`
4. **Documentation**: Add docstrings to test methods
5. **Edge Cases**: Test boundary conditions and error cases

## Adding New Tests

1. **Choose Category**: Decide which test category your test belongs to
2. **Create File**: Create a new test file in the appropriate directory
3. **Follow Naming**: Use `test_*.py` naming convention
4. **Import Helpers**: Import test utilities from `tests.utils.test_helpers`
5. **Run Tests**: Test your new tests before committing

## Common Test Patterns

### Testing File I/O
```python
from tests.utils.test_helpers import create_temp_csv_file, cleanup_temp_file

class TestFileIO(unittest.TestCase):
    def setUp(self):
        self.temp_file = create_temp_csv_file([{'col1': 'value1'}])
    
    def tearDown(self):
        cleanup_temp_file(self.temp_file)
    
    def test_read_file(self):
        # Test file reading logic
        pass
```

### Testing User Input
```python
from tests.utils.test_helpers import MockUserInputProvider

class TestUserInput(unittest.TestCase):
    def test_missing_file_prompt(self):
        provider = MockUserInputProvider(['test.csv'])
        # Test user input handling
        pass
```

### Testing with Mocks
```python
from unittest.mock import patch, MagicMock

class TestWithMocks(unittest.TestCase):
    @patch('os.path.exists', return_value=True)
    def test_file_exists(self, mock_exists):
        # Test with mocked file existence
        pass
``` 