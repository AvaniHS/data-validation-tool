"""Configuration template for data validation tool."""

from typing import Dict, Any


def get_configuration_template() -> Dict[str, Any]:
    """Return the configuration template."""
    return {
        "file_format": "",
        "number_of_files": 0,
        "file1_path": "",
        "file2_path": "",
        "file1_sheet1": "",
        "file1_sheet2": "",
        "file2_sheet": "",
        "output_path": "",
        "output_sheet": "",
        "column_mapping": {
            "file1_column": "file2_column"
        },
        "additional_columns_file1": [],
        "additional_columns_file1_types": [],
        "additional_columns_file2": [],
        "additional_columns_file2_types": [],
        "join_keys": {
            "file1_key": "file2_key"
        },
        "join_keys_types": {
            "file1_key": "NA",
            "file2_key": "NA"
        },
        "aggregation": "NA",
        "file1_metric_list": [],
        "file2_metric_list": []
    } 