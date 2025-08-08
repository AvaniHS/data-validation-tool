#!/usr/bin/env python3

import os
import sys
import json
import argparse
from typing import Dict, Any

from validation.dependency_container import get_pipeline_orchestrator
from validation.pipeline_orchestrator import PipelineResult
from services.user_interaction.console import ConsoleUserInputProvider
from services.user_interaction.interaction import UserInteraction


def run_validation_pipeline(config_path: str) -> PipelineResult:
    try:
        print("=" * 80)
        print("DATA VALIDATION PIPELINE")
        print("=" * 80)
        
        orchestrator = get_pipeline_orchestrator()
        result = orchestrator.execute_pipeline(config_path)
        
        if result.success:
            config = result.execution_summary.get('config', {})
            orchestrator.print_pipeline_summary(result, config)
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
        return PipelineResult(
            success=False,
            error_message=str(e)
        )


def create_sample_config() -> Dict[str, Any]:
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
        "join_keys_types": {
            "key1": "NA"
        },
        "additional_columns_file1": "NA",
        "additional_columns_file1_types": "NA",
        "additional_columns_file2": "NA",
        "additional_columns_file2_types": "NA",
        "aggregation": "NA",
        "file1_metric_list": [],
        "file2_metric_list": []
    }


def main():
    parser = argparse.ArgumentParser(
        description='Data Validation Tool - Complete pipeline for data comparison and validation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with configuration file
  python run_validation.py --config config.json
  
  # Show sample configuration
  python run_validation.py --sample-config
  
  # Run interactively (no arguments)
  python run_validation.py
  
  # Run with sample files
  python run_validation.py --config tests/sample/config_two_csv_files.json
        """
    )
    
    parser.add_argument(
        '--config', 
        help='Path to configuration JSON file'
    )
    
    parser.add_argument(
        '--sample-config', 
        action='store_true',
        help='Display sample configuration format'
    )
    
    parser.add_argument(
        '--interactive', 
        action='store_true',
        help='Run in interactive mode (default when no arguments provided)'
    )
    
    args = parser.parse_args()
    
    if args.sample_config:
        print("Sample Configuration Format:")
        print("=" * 50)
        print(json.dumps(create_sample_config(), indent=2))
        print("\nFor more examples, see files in tests/sample/ directory")
        return
    
    if not args.config:
        print("🚀 Starting Data Validation Tool in Interactive Mode")
        print("=" * 60)
        
        user_interaction = UserInteraction(ConsoleUserInputProvider())
        result = user_interaction.get_input_files()
        
        if not result or not result[0]:
            print("👋 Exiting...")
            sys.exit(0)
        
        config_file = result[0]
        
        if not os.path.exists(config_file):
            print(f"❌ Error: Configuration file not found: {config_file}")
            sys.exit(1)
        
        result = run_validation_pipeline(config_file)
        if not result.success:
            sys.exit(1)
    else:
        if not os.path.exists(args.config):
            print(f"❌ Error: Configuration file not found: {args.config}")
            sys.exit(1)
        
        result = run_validation_pipeline(args.config)
        if not result.success:
            sys.exit(1)


if __name__ == '__main__':
    main() 