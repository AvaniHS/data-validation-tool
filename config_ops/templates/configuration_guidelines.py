"""Configuration guidelines for data validation tool."""


def get_configuration_guidelines() -> str:
    """Return the configuration guidelines documentation."""
    return """
======================================================================
DATA VALIDATION TOOL - CONFIGURATION FILE
======================================================================

VALIDATION RULES:
1. file_format: Must be ".csv", ".xlsx", ".json", or "mixed"
2. number_of_files: Must be 1 or 2
3. When number_of_files = 1: file_format must be ".xlsx", file2_path = "NA"
4. When number_of_files = 2: file2_path is required
5. Sheet names: Required for Excel files, use "NA" for CSV files
6. Column mapping: Must be a dictionary with at least one mapping
7. Optional fields: Use "NA" or empty arrays/objects if not needed
8. File extensions must match file_format (except for "mixed")
9. Mixed format: Each file can be .csv or .xlsx independently
10. Aggregation: All non-aggregated columns are auto-grouped by default
11. Aggregation Flow: file1_aggregation -> file2_aggregation -> join -> final_aggregation -> comparison

======================================================================

MANDATORY FIELDS - Required for all configurations
"file_format": ".csv",           // CHOICES: ".csv", ".xlsx", ".json", "mixed"
"number_of_files": 2,            // CHOICES: 1 (one Excel file with two sheets) or 2 (two separate files)
"file1_path": "path/before_migration.csv",  // Path to your first dataset file
"file2_path": "path/after_migration.csv",   // Path to second file (use "NA" if number_of_files = 1)

SHEET NAMES - Required only for Excel files, use "NA" for CSV files
"file1_sheet1": "NA",            // First sheet name if file1 is Excel, "NA" if CSV
"file1_sheet2": "NA",            // Second sheet name if file1 is Excel (for single file scenarios), "NA" if CSV or two files
"file2_sheet": "NA",             // Sheet name if file2 is Excel, "NA" if CSV

OUTPUT SETTINGS - Optional (defaults: output_path="comparison_results.xlsx", output_sheet="Results")
"output_path": "comparison_results.xlsx",  // Where to save results
"output_sheet": "Results",                 // Sheet name for results (Excel only)

MANDATORY - Column mapping between datasets
"column_mapping": {
    "customer_id": "customer_id",    // Maps column names between files
    "product_id": "product_code",    // Format: "file1_column": "file2_column"
    "quantity": "qty",               // Must have at least one mapping
    "price": "amount"                // All mapped columns must exist in both files
},

OPTIONAL FIELDS - Use "NA" or empty arrays/objects if not needed
"additional_columns_file1": ["date", "region", "category"],  // Extra columns from file1 to include
"additional_columns_file1_types": ["non_numeric", "non_numeric", "non_numeric"],  // Data types for additional columns file1
"additional_columns_file2": ["transaction_date", "location", "product_category"],  // Extra columns from file2
"additional_columns_file2_types": ["non_numeric", "non_numeric", "non_numeric"],  // Data types for additional columns file2

"join_keys": {                    // Columns to join datasets on (use "NA" if not needed)
    "customer_id": "customer_id",  // Primary keys for joining
    "product_id": "product_code"   // Must exist in both datasets
},

"join_keys_types": {              // Data types for join keys (optional)
    "customer_id": "non_numeric",  // CHOICES: "numeric", "non_numeric", or "NA" for dynamic detection
    "product_id": "NA"             // Use "NA" to automatically detect data type from the data
},

"aggregation": {                   // Aggregation settings (optional - if not specified, all non-join columns will be auto-grouped)
    "file1_columns": {             // Aggregation for file1 columns
        "sum": ["quantity", "price"],      // Columns to sum
        "avg": ["NA"],                     // Columns to average (use ["NA"] if not needed)
        "count": ["NA"],                   // Columns to count (use ["NA"] if not needed)
        "min": ["NA"],                     // Columns to find minimum (use ["NA"] if not needed)
        "max": ["NA"]                      // Columns to find maximum (use ["NA"] if not needed)
    },
    "file1_groupby_columns": ["customer_id", "product_id", "region"],  // Group by columns for file1 aggregation
    "file2_columns": {             // Aggregation for file2 columns
        "sum": ["qty", "amount"],          // Columns to sum
        "avg": ["NA"],                     // Columns to average (use ["NA"] if not needed)
        "count": ["NA"],                   // Columns to count (use ["NA"] if not needed)
        "min": ["NA"],                     // Columns to find minimum (use ["NA"] if not needed)
        "max": ["NA"]                      // Columns to find maximum (use ["NA"] if not needed)
    },
    "file2_groupby_columns": ["customer_id", "product_code", "location"],  // Group by columns for file2 aggregation
    "final_aggregated_columns": {  // Final aggregation after joining datasets
        "sum": ["quantity_sum", "price_sum", "qty_sum", "amount_sum"],  // Columns to sum in final aggregation
        "avg": ["quantity_avg", "price_avg"],                            // Columns to average in final aggregation
        "count": ["NA"],                                                 // Columns to count in final aggregation
        "min": ["NA"],                                                   // Columns to find minimum in final aggregation
        "max": ["NA"]                                                    // Columns to find maximum in final aggregation
    },
    "final_groupby_columns": ["customer_id", "product_id"]  // Group by columns for final aggregation
    // NOTE: Aggregation is OPTIONAL. If not specified, all non-join columns will be automatically grouped by default.
    // You only need to specify aggregation if you want custom aggregation behavior.
    // Use ["NA"] if not needed (all non-aggregated columns are auto-grouped by default)
    // AGGREGATION TYPES: "sum", "avg", "count", "min", "max" - use ["NA"] if not needed
    // PROCESSING FLOW: file1_aggregation -> file2_aggregation -> join -> final_aggregation -> comparison
    
    // BACKWARD COMPATIBILITY: The old "groupby_columns" field is deprecated but still supported.
    // If "final_groupby_columns" is not specified, the system will use "groupby_columns" as fallback.
    // For new configurations, use the new structure with separate groupby columns for each step.
},

OPTIONAL - Metric lists for additional analysis
"file1_metric_list": ["metric1", "metric2", "metric3"],    // Array of metrics for file1
"file2_metric_list": ["metric1", "metric2", "metric3"]     // Array of metrics for file2

======================================================================
CONFIGURATION EXAMPLES:
======================================================================

EXAMPLE 1: Two CSV Files
"file_format": ".csv", "number_of_files": 2
"file1_sheet1": "NA", "file1_sheet2": "NA", "file2_sheet": "NA"

EXAMPLE 2: Two Excel Files  
"file_format": ".xlsx", "number_of_files": 2
"file1_sheet1": "Sheet1", "file1_sheet2": "NA", "file2_sheet": "Sheet1"

EXAMPLE 3: One Excel File with Two Sheets
"file_format": ".xlsx", "number_of_files": 1
"file2_path": "NA", "file1_sheet1": "Before", "file1_sheet2": "After", "file2_sheet": "NA"

EXAMPLE 4: Two JSON Files
"file_format": ".json", "number_of_files": 2
"file1_sheet1": "NA", "file1_sheet2": "NA", "file2_sheet": "NA"

EXAMPLE 5: Mixed Format (CSV + Excel + JSON)
"file_format": "mixed", "number_of_files": 2
"file1_sheet1": "NA" (CSV), "file1_sheet2": "NA", "file2_sheet": "Sheet1" (Excel)

======================================================================
""" 