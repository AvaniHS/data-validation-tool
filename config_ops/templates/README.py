"""README documentation for configuration templates."""


def get_templates_readme() -> str:
    """Return the README documentation for configuration templates."""
    return """
# Sample Configuration Files

This directory contains sample configuration files for the Data Validation Tool.

## 📁 Files

### **📝 configuration_template.json**
- **Purpose**: Template file for users to edit with their configuration values
- **Usage**: Copy this file, edit it with your file paths and column mappings, then use it to run the validation tool
- **Content**: Clean template with empty/default values

### **📚 configuration_guidelines.jsonc**
- **Purpose**: Reference documentation with detailed field descriptions and examples
- **Usage**: Read this file to understand what each configuration field does
- **Content**: Template with detailed comments and examples

## 🚀 Getting Started

1. **Download** these files using the tool's sample download feature
2. **Edit** `configuration_template.json` with your data file paths and column mappings
3. **Refer** to `configuration_guidelines.jsonc` for detailed field descriptions
4. **Run** the validation tool with your edited configuration file

## 📋 Example Workflow

```bash
# 1. Run the tool and download samples
python run_validation.py

# 2. Edit the downloaded template file
# 3. Run validation with your configuration
python run_validation.py --file1 your_config.json
```

## 📖 Documentation

For detailed configuration field descriptions and examples, see `configuration_guidelines.jsonc`.

For test scenarios and sample data files, see `tests/sample/` directory.
""" 