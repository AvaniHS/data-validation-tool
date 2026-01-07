# Data Validation Tool

A comprehensive tool for data validation, comparison, and analysis of datasets in CSV and Excel formats.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended for large datasets)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/data-validation-tool.git
cd data-validation-tool

# Install dependencies
pip install -r requirements.txt

# Run the tool
python run_validation.py --help
```

### Quick Test
```bash
# Test with sample data
python run_validation.py --config tests/sample/config_two_csv_files.json
```

## 📋 Features

- **Multi-format Support**: CSV and Excel files
- **Data Comparison**: Compare datasets with flexible column mapping
- **Aggregation**: Built-in aggregation functions (sum, avg, count, min, max)
- **Interactive Mode**: User-friendly interactive configuration
- **Batch Processing**: Handle multiple files efficiently
- **Detailed Reporting**: Comprehensive comparison reports with differences and deltas

## 🛠️ Usage

### Interactive Mode
```bash
python run_validation.py
```

### Configuration File Mode
```bash
python run_validation.py --config your_config.json
```

### Show Sample Configuration
```bash
python run_validation.py --sample-config
```

## 📁 Project Structure

```
data-validation-tool/
├── validation/           # Core validation logic
├── config_ops/          # Configuration processing
├── services/            # File handling and user interaction
├── readers/             # File reading modules
├── writers/             # File writing modules
├── tests/               # Test suite
├── documentation/       # Detailed documentation
└── run_validation.py    # Main entry point
```

## 📖 Documentation

- **[Installation Guide](INSTALLATION.md)** - Detailed installation instructions
- **[User Guide](documentation/README.md)** - Comprehensive usage documentation
- **[Configuration Guide](documentation/Data_Validation_Tool_Documentation.md)** - Configuration file format and examples
- **[Sample Configurations](tests/sample/)** - Ready-to-use configuration examples

## 🔧 Development

### Setup Development Environment
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 🐳 Docker

```bash
# Build image
docker build -t data-validation-tool .

# Run with data mounted
docker run -v $(pwd)/data:/app/data data-validation-tool python run_validation.py --config /app/data/config.json
```

## 📊 Example Configuration

```json
{
  "file_format": ".csv",
  "number_of_files": 2,
  "file1_path": "data/before_migration.csv",
  "file2_path": "data/after_migration.csv",
  "output_path": "results/comparison.xlsx",
  "output_sheet": "ValidationSummary",
  "column_mapping": {
    "customer_id": "customer_id",
    "amount": "amount"
  },
  "join_keys": {
    "customer_id": "customer_id"
  },
  "aggregation": {
    "sum": ["amount"],
    "avg": ["amount"]
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🆘 Support

- **Documentation**: Check the [documentation](documentation/) folder
- **Issues**: Report bugs on [GitHub Issues](https://github.com/your-org/data-validation-tool/issues)
- **Examples**: See [sample configurations](tests/sample/)

## 🔄 Version History

- **v1.0.0** - Initial release with core validation features
- **v1.1.0** - Added aggregation and enhanced reporting
- **v1.2.0** - Improved Excel handling and user interaction

---

**Need help?** Start with the [Installation Guide](INSTALLATION.md) or check the [User Guide](documentation/README.md). 