# Data Validation Tool - Installation Guide

> **Quick Setup**: For immediate setup, see [QUICKSTART.md](QUICKSTART.md)
> 
> **Detailed Setup**: For comprehensive setup instructions, see [SETUP.md](SETUP.md)

## Prerequisites

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM (8GB recommended for large datasets)
- **Disk Space**: At least 500MB free space

## Installation Methods

### Method 1: Using pip (Recommended)

#### For Production Use
```bash
# Clone the repository
git clone https://github.com/your-org/data-validation-tool.git
cd data-validation-tool

# Install core dependencies
pip install -r requirements.txt

# Run the tool
python run_validation.py --help
```

#### For Development
```bash
# Clone the repository
git clone https://github.com/your-org/data-validation-tool.git
cd data-validation-tool

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

### Method 2: Using conda

```bash
# Create a new conda environment
conda create -n datavalidation python=3.9
conda activate datavalidation

# Install dependencies
conda install pandas numpy openpyxl

# Clone and install the tool
git clone https://github.com/your-org/data-validation-tool.git
cd data-validation-tool
pip install -e .
```

### Method 3: Using Docker

```bash
# Build the Docker image
docker build -t data-validation-tool .

# Run the tool
docker run -v $(pwd)/data:/app/data data-validation-tool python run_validation.py --config /app/data/config.json
```

## Verification

After installation, verify that everything is working:

```bash
# Check if the tool runs
python run_validation.py --help

# Run a quick test
python run_validation.py --config tests/sample/config_two_csv_files.json
```

## Dependencies

### Core Dependencies
- **pandas** (>=1.5.0): Data manipulation and analysis
- **numpy** (>=1.21.0): Numerical computing
- **openpyxl** (>=3.0.0): Excel file handling

### Development Dependencies (Optional)
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Code linting
- **mypy**: Type checking
- **sphinx**: Documentation generation

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# If you get import errors, ensure you're in the correct directory
cd /path/to/data-validation-tool
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 2. Permission Errors
```bash
# On Linux/macOS, you might need to use sudo
sudo pip install -r requirements.txt

# Or install for current user only
pip install --user -r requirements.txt
```

#### 3. Excel File Issues
```bash
# If you have issues with Excel files, ensure openpyxl is installed
pip install openpyxl>=3.0.0
```

#### 4. Memory Issues
```bash
# For large datasets, increase Python memory limit
export PYTHONMALLOC=malloc
python -X maxsize=4GB run_validation.py --config your_config.json
```

### Platform-Specific Notes

#### Windows
- Ensure you have Visual C++ build tools installed for some packages
- Use `py` instead of `python` if you have multiple Python versions

#### macOS
- You might need to install Xcode command line tools
- Use Homebrew for easier dependency management

#### Linux
- Install system dependencies: `sudo apt-get install python3-dev build-essential`
- For Ubuntu/Debian: `sudo apt-get install python3-pip python3-venv`

## Environment Setup

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv datavalidation_env

# Activate virtual environment
# On Windows:
datavalidation_env\Scripts\activate
# On macOS/Linux:
source datavalidation_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### IDE Setup

#### VS Code
1. Install Python extension
2. Select the correct Python interpreter
3. Install recommended extensions for Python development

#### PyCharm
1. Open the project
2. Configure Python interpreter
3. Install requirements from `requirements.txt`

## Next Steps

After successful installation:

1. **Read the Documentation**: Check `documentation/README.md`
2. **Try Sample Configurations**: Look in `tests/sample/` directory
3. **Run Tests**: `python -m pytest tests/`
4. **Create Your First Configuration**: Use the sample configs as templates

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the documentation
3. Search existing issues on GitHub
4. Create a new issue with detailed information

## Uninstallation

```bash
# Remove the package
pip uninstall data-validation-tool

# Remove virtual environment (if used)
rm -rf datavalidation_env
``` 