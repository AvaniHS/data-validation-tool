# Data Validation Tool - Quick Start Guide

Get up and running with the Data Validation Tool in 5 minutes!

## ⚡ 5-Minute Setup

### 1. Prerequisites Check
```bash
# Check Python version (needs 3.8+)
python --version

# Check if pip is available
pip --version
```

### 2. Download and Install
```bash
# Clone the repository
git clone https://github.com/your-org/data-validation-tool.git
cd data-validation-tool

# Install dependencies
pip install -r requirements.txt
```

### 3. Quick Test
```bash
# Test the installation
python run_validation.py --help

# Run with sample data
python run_validation.py --config tests/sample/config_two_csv_files.json
```

## 🎯 Your First Validation

### Step 1: Prepare Your Data
Place your CSV or Excel files in a folder:
```
your_data/
├── before_data.csv
└── after_data.csv
```

### Step 2: Create Configuration
Create `my_config.json`:
```json
{
  "file_format": ".csv",
  "number_of_files": 2,
  "file1_path": "your_data/before_data.csv",
  "file2_path": "your_data/after_data.csv",
  "output_path": "results/my_comparison.xlsx",
  "output_sheet": "ValidationSummary",
  "column_mapping": {
    "id": "id",
    "amount": "amount"
  },
  "join_keys": {
    "id": "id"
  }
}
```

### Step 3: Run Validation
```bash
python run_validation.py --config my_config.json
```

### Step 4: Check Results
Open `results/my_comparison.xlsx` to see your comparison results!

## 🚀 Interactive Mode

Don't want to create a config file? Use interactive mode:

```bash
python run_validation.py
```

The tool will guide you through:
- Selecting your data files
- Choosing columns to compare
- Setting up join keys
- Configuring output options

## 📊 Common Use Cases

### Compare Two CSV Files
```bash
python run_validation.py --config tests/sample/config_two_csv_files.json
```

### Compare Excel Sheets
```bash
python run_validation.py --config tests/sample/config_single_excel_file.json
```

### With Aggregation
```bash
python run_validation.py --config tests/sample/config_with_aggregation.json
```

## 🔧 Configuration Examples

### Basic CSV Comparison
```json
{
  "file_format": ".csv",
  "number_of_files": 2,
  "file1_path": "data1.csv",
  "file2_path": "data2.csv",
  "output_path": "comparison.xlsx",
  "column_mapping": {
    "customer_id": "customer_id",
    "sales": "sales"
  },
  "join_keys": {
    "customer_id": "customer_id"
  }
}
```

### Excel with Multiple Sheets
```json
{
  "file_format": ".xlsx",
  "number_of_files": 1,
  "file1_path": "data.xlsx",
  "file1_sheet1": "Sheet1",
  "file1_sheet2": "Sheet2",
  "output_path": "comparison.xlsx",
  "column_mapping": {
    "id": "id",
    "value": "value"
  },
  "join_keys": {
    "id": "id"
  }
}
```

### With Aggregation
```json
{
  "file_format": ".csv",
  "number_of_files": 2,
  "file1_path": "data1.csv",
  "file2_path": "data2.csv",
  "output_path": "aggregated_comparison.xlsx",
  "column_mapping": {
    "region": "region",
    "sales": "sales"
  },
  "join_keys": {
    "region": "region"
  },
  "aggregation": {
    "sum": ["sales"],
    "avg": ["sales"]
  }
}
```

## 🐛 Quick Troubleshooting

### "Module not found" error
```bash
# Make sure you're in the right directory
cd data-validation-tool
pip install -r requirements.txt
```

### "File not found" error
```bash
# Check your file paths in the config
# Use absolute paths or relative to the project root
```

### "Permission denied" error
```bash
# On Windows: Run as administrator
# On Linux/macOS: Use sudo or install for user
pip install --user -r requirements.txt
```

## 📖 Next Steps

- **Detailed Setup**: Read [SETUP.md](SETUP.md) for comprehensive installation
- **User Guide**: Check [documentation/README.md](documentation/README.md) for advanced features
- **Examples**: Browse [tests/sample/](tests/sample/) for more configuration examples
- **Troubleshooting**: See [INSTALLATION.md](INSTALLATION.md) for detailed troubleshooting

## 🆘 Need Help?

- **Quick Issues**: Check this guide's troubleshooting section
- **Setup Problems**: Read [SETUP.md](SETUP.md)
- **Usage Questions**: Check [documentation/README.md](documentation/README.md)
- **Bug Reports**: Create an issue on GitHub

---

**Ready to validate your data?** Start with the interactive mode or use one of the sample configurations! 