"""Sample configuration for data validation tool."""

from typing import Dict, Any


def get_sample_configuration() -> Dict[str, Any]:
    """Return a sample configuration with example values."""
    return {
        "file_format": ".csv",
        "number_of_files": 2,
        "file1_path": "path/to/file1.csv",
        "file2_path": "path/to/file2.csv",
        "file1_sheet1": "NA",
        "file1_sheet2": "NA",
        "file2_sheet": "NA",
        "output_path": "path/to/output.xlsx",
        "output_sheet": "Results",
        "column_mapping": {
            "column1": "column1",
            "column2": "column2"
        },
        "join_keys": {
            "key1": "key1"
        },
        "additional_columns_file1": {},
        "additional_columns_file2": {},
        "aggregation": "NA",
        "file1_metric_list": [],
        "file2_metric_list": [],
        "detailed_join_analysis": "no"
    }
