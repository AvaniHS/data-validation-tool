# JSON Demo for Data Validation Tool

This demo showcases the data validation tool using JSON input files.

## Files

- `json_demo_data.py` - Generates sample JSON data with intentional mismatches
- `json_demo_config.json` - Configuration file for the validation
- `run_json_demo.bat` - Windows batch file to run the demo
- `JSON_DEMO_README.md` - This documentation

## Demo Data

The demo creates two JSON files:

### file1_before.json
- 8 employee records
- Contains: ID, Name, Department, Salary, Bonus

### file2_after.json  
- Same 8 records with intentional changes:
  - **Row 2**: ID changed from 3→99, Name changed from Charlie→Franklin
  - **Row 0**: Salary changed from 50000→51000, Bonus changed from 5000→5100  
  - **Row 3**: Salary changed from 60000→62000, Bonus changed from 6000→6200

## Configuration

- **Join Keys**: ID, Name
- **Column Mapping**: Department, Salary, Bonus
- **Aggregation**: Sum of Salary and Bonus
- **Metrics**: Salary, Bonus (for delta calculations)
- **Join Analysis**: Enabled (will create separate join analysis file)

## Expected Output

1. `json_validation_results.json` - Main validation results
2. `json_validation_results_join_analysis.json` - Join analysis results showing mismatches

## Running the Demo

1. Generate demo data:
   ```bash
   py demo\json_demo\json_demo_data.py
   ```

2. Run validation:
   ```bash
   py run_validation.py --config demo\json_demo\json_demo_config.json
   ```

Or use the batch file:
```bash
demo\json_demo\run_json_demo.bat
```

## What to Expect

- The validation will detect join key mismatches (ID 3→99, Name Charlie→Franklin)
- Delta calculations will show changes in Salary and Bonus values
- Two output files will be created due to join analysis being enabled
- The join analysis file will contain detailed mismatch information
