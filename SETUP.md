# Data Validation Tool - Setup Guide

This guide provides step-by-step instructions for setting up the Data Validation Tool on your system.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Verification](#verification)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM (8GB recommended for large datasets)
- **Disk Space**: At least 500MB free space

### Python Installation
If you don't have Python installed:

#### Windows
```bash
# Download from python.org or use winget
winget install Python.Python.3.9
```

#### macOS
```bash
# Using Homebrew
brew install python@3.9

# Or download from python.org
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.9 python3-pip python3-venv
```

## 🚀 Installation Methods

### Method 1: Quick Setup (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/your-org/data-validation-tool.git
cd data-validation-tool

# 2. Create virtual environment (recommended)
python -m venv datavalidation_env

# 3. Activate virtual environment
# On Windows:
datavalidation_env\Scripts\activate
# On macOS/Linux:
source datavalidation_env/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify installation
python run_validation.py --help
```

### Method 2: Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/data-validation-tool.git
cd data-validation-tool

# 2. Create virtual environment
python -m venv datavalidation_dev
source datavalidation_dev/bin/activate  # or datavalidation_dev\Scripts\activate on Windows

# 3. Install development dependencies
pip install -r requirements-dev.txt

# 4. Install in development mode
pip install -e .

# 5. Run tests to verify
python -m pytest tests/ -v
```

### Method 3: Using Conda

```bash
# 1. Create conda environment
conda create -n datavalidation python=3.9
conda activate datavalidation

# 2. Install core dependencies
conda install pandas numpy openpyxl

# 3. Clone and install
git clone https://github.com/your-org/data-validation-tool.git
cd data-validation-tool
pip install -e .
```

### Method 4: Docker Setup

```bash
# 1. Build Docker image
docker build -t data-validation-tool .

# 2. Create data directory
mkdir -p data

# 3. Run with data mounted
docker run -v $(pwd)/data:/app/data data-validation-tool python run_validation.py --help
```

## ✅ Verification

After installation, verify everything is working:

### Basic Verification
```bash
# Check if the tool runs
python run_validation.py --help

# Should show help information
```

### Test with Sample Data
```bash
# Run a quick test with sample configuration
python run_validation.py --config tests/sample/config_two_csv_files.json

# Should process the sample data and create output files
```

### Check Dependencies
```bash
# Verify all dependencies are installed
python -c "import pandas; import numpy; import openpyxl; print('All dependencies installed successfully!')"
```

## ⚙️ Configuration

### First Configuration File
Create your first configuration file:

```json
{
  "file_format": ".csv",
  "number_of_files": 2,
  "file1_path": "your_data/file1.csv",
  "file2_path": "your_data/file2.csv",
  "output_path": "results/comparison.xlsx",
  "output_sheet": "ValidationSummary",
  "column_mapping": {
    "id": "id",
    "value": "value"
  },
  "join_keys": {
    "id": "id"
  }
}
```

### Sample Configurations
Browse ready-to-use configurations in `tests/sample/`:
- `config_two_csv_files.json` - Basic CSV comparison
- `config_single_excel_file.json` - Excel file with multiple sheets
- `config_with_aggregation.json` - With aggregation functions

## 🔧 Environment Setup

### IDE Configuration

#### VS Code
1. Install Python extension
2. Select interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"
3. Choose your virtual environment
4. Install recommended extensions

#### PyCharm
1. Open project
2. Go to Settings → Project → Python Interpreter
3. Add interpreter → Existing environment
4. Select your virtual environment

### Environment Variables (Optional)
```bash
# Set Python path (if needed)
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Set memory limits for large datasets
export PYTHONMALLOC=malloc
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Solution: Ensure you're in the correct directory
cd /path/to/data-validation-tool
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 2. Permission Errors
```bash
# On Linux/macOS
sudo pip install -r requirements.txt

# Or install for current user
pip install --user -r requirements.txt
```

#### 3. Excel File Issues
```bash
# Ensure openpyxl is installed
pip install openpyxl>=3.0.0

# Check file permissions
chmod 644 your_excel_file.xlsx
```

#### 4. Memory Issues
```bash
# Increase Python memory limit
python -X maxsize=4GB run_validation.py --config your_config.json
```

#### 5. Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf datavalidation_env
python -m venv datavalidation_env
source datavalidation_env/bin/activate
pip install -r requirements.txt
```

### Platform-Specific Issues

#### Windows
- **Issue**: Visual C++ build tools missing
- **Solution**: Install Visual Studio Build Tools
- **Issue**: Multiple Python versions
- **Solution**: Use `py` instead of `python`

#### macOS
- **Issue**: Xcode command line tools missing
- **Solution**: `xcode-select --install`
- **Issue**: Permission denied
- **Solution**: Use Homebrew or install for user only

#### Linux
- **Issue**: Missing system dependencies
- **Solution**: `sudo apt-get install python3-dev build-essential`
- **Issue**: pip not found
- **Solution**: `sudo apt-get install python3-pip`

## 📞 Getting Help

If you encounter issues:

1. **Check this guide** - Review the troubleshooting section
2. **Check logs** - Look for error messages in the output
3. **Test with samples** - Try the sample configurations first
4. **Search issues** - Check existing GitHub issues
5. **Create issue** - Report new problems with detailed information

## 🔄 Updating

To update to the latest version:

```bash
# Pull latest changes
git pull origin main

# Reinstall dependencies (if needed)
pip install -r requirements.txt --upgrade

# For development
pip install -r requirements-dev.txt --upgrade
```

## 🧹 Uninstallation

To remove the tool:

```bash
# Remove the package
pip uninstall data-validation-tool

# Remove virtual environment
rm -rf datavalidation_env

# Remove cloned repository
rm -rf data-validation-tool
```

---

**Next Steps**: After setup, read the [User Guide](documentation/README.md) to learn how to use the tool effectively. 