# Simple CSV Demo - Data Validation Tool

This is a minimal demo showcasing the Data Validation Tool with CSV files.

## 📁 Files

- **`file1_before.csv`** - Original data (8 records)
- **`file2_after.csv`** - Modified data (8 records) 
- **`simple_demo_config.json`** - Configuration file
- **`simple_validation_results.xlsx`** - Output file (generated after validation)

## 📊 Data Structure

### Columns:
- **Join Keys**: `ID`, `Name` (2 columns)
- **Include Columns**: `Department` (1 column)
- **Metrics**: `Salary`, `Bonus` (2 columns)

### Sample Data:
```
ID | Name    | Department | Salary | Bonus
1  | Alice   | IT         | 50000  | 5000
2  | Bob     | HR         | 45000  | 4000
3  | Charlie | IT         | 55000  | 5500
4  | Diana   | Finance    | 60000  | 6000
```

## 🎯 Demo Scenarios

1. **Perfect Matches**: Bob, Charlie, Eve, Frank, Grace, Henry (no changes)
2. **Salary Changes**: Alice (+1000), Diana (+2000)
3. **Bonus Changes**: Alice (+100), Diana (+200)
4. **Join Key Analysis**: All records match on ID and Name

## 🚀 How to Run

```bash
py run_validation.py --config demo/simple_demo_config.json
```

## 📋 Expected Output

### Validation Summary Sheet:
- **8 rows** of comparison data
- **Join Key Columns**: ID, Name (with comparison results)
- **Include Columns**: Department (with comparison results)
- **Metric Columns**: Salary, Bonus (with comparison, delta, and delta% results)

### Join Analysis Sheet:
- **Failed join patterns** (if any)
- **Key-value analysis** for mismatches

## 🔍 Key Learning Points

- **Minimal Data**: Easy to understand and verify manually
- **Clear Differences**: Obvious salary and bonus changes to validate
- **All Column Types**: Join keys, include columns, and metrics
- **CSV Format**: Shows how the tool works with CSV files

This demo is perfect for quick testing and understanding the tool's capabilities!
