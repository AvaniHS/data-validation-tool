# Data Validation Tool - Demo

This demo showcases all the capabilities of the Data Validation Tool using realistic business data.

## 📁 Demo Files

- **`sales_demo_data.xlsx`** - Sample Excel file with two sheets
  - `Q1_Before` - Original sales data (50 records)
  - `Q1_After` - Modified sales data with intentional differences (50 records)
- **`demo_config.json`** - Configuration file for the validation
- **`validation_results.xlsx`** - Output file (generated after running validation)

## 🎯 Demo Scenarios Covered

### 1. **Data Type Validation**
- **String vs Numeric**: `Month_No` field has mixed data types (int vs string)
- **Format Differences**: `Reporter_HQ_ID` has different formats (HQ123 vs HQ-123)

### 2. **Missing Data Detection**
- **NULL Values**: Some `Customer_ID` fields are missing in the "After" data
- **Data Completeness**: Shows how the tool identifies incomplete records

### 3. **Value Mismatches**
- **Sales Amount**: Some records have different sales amounts (10% increase)
- **Quantity**: Some quantities are different (+5 units)
- **Calculated Fields**: Different profit margins and commission rates

### 4. **Join Key Analysis**
- **Multiple Join Keys**: Uses 5 different join keys for comprehensive analysis
- **Key Mismatches**: Shows which specific key combinations are failing
- **Detailed Analysis**: Enabled to show failed join patterns

### 5. **Metrics Comparison**
- **Delta Calculation**: Shows absolute differences between metrics
- **Percentage Delta**: Shows percentage differences for better insights
- **Multiple Metrics**: Compares Sales_Amount, Quantity_Sold, Profit_Margin, Commission

## 🚀 How to Run the Demo

### Step 1: Run the Validation
```bash
py run_validation.py --config demo/demo_config.json
```

### Step 2: Review Results
The tool will generate `validation_results.xlsx` with:
- **Validation_Summary** sheet - Main comparison results
- **join_analysis** sheet - Detailed join failure analysis

## 📊 Expected Demo Outcomes

### Validation Summary Sheet
- **Row-by-row comparison** of all 50 records
- **Match/No Match indicators** for each field
- **Delta columns** showing exact differences
- **Percentage delta columns** showing relative differences
- **Aggregated metrics** for overall comparison

### Join Analysis Sheet
- **Failed join patterns** showing which key combinations don't match
- **Value-level analysis** of specific mismatches
- **Count of occurrences** for each mismatch pattern
- **Sorted by key names** for easy analysis

## 🔍 Key Learning Points

1. **Data Quality Issues**: The demo shows common real-world data quality problems
2. **Comprehensive Validation**: Every field is validated against its counterpart
3. **Flexible Configuration**: Easy to modify for different scenarios
4. **Detailed Reporting**: Both high-level and granular analysis
5. **Performance**: Optimized for quick demonstration (50 records)

## 📈 Business Value Demonstration

- **Data Reconciliation**: Compare before/after data transformations
- **Quality Assurance**: Identify data inconsistencies
- **Audit Trail**: Track changes and differences
- **Root Cause Analysis**: Understand why data doesn't match
- **Compliance**: Ensure data integrity across systems

## 🛠️ Customization

You can modify `demo_config.json` to:
- Change join keys
- Add/remove metrics
- Enable/disable join analysis
- Modify output format
- Adjust validation rules

## 📝 Sample Data Structure

**Q1_Before Sheet:**
- Month_No, Reporter_HQ_ID, Buyer_HQ_ID, Customer_ID, Product_Code
- Region, Sales_Amount, Quantity_Sold, Discount_Percent, Sales_Rep
- Profit_Margin, Commission

**Q1_After Sheet:**
- Same structure with intentional differences for demonstration

This demo provides a complete showcase of the Data Validation Tool's capabilities in a realistic business scenario.
