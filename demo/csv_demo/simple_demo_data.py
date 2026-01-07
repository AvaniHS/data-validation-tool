"""Script to create simple CSV demo files for validation tool."""

import pandas as pd
import numpy as np

def create_simple_csv_demo():
    """Create simple CSV files with minimal data for demonstration."""
    
    # Create 8 records for each file
    n_records = 8
    
    # File 1: Before data
    file1_data = {
        'ID': [1, 2, 3, 4, 5, 6, 7, 8],
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry'],
        'Department': ['IT', 'HR', 'IT', 'Finance', 'HR', 'IT', 'Finance', 'HR'],
        'Salary': [50000, 45000, 55000, 60000, 48000, 52000, 58000, 47000],
        'Bonus': [5000, 4000, 5500, 6000, 4800, 5200, 5800, 4700]
    }
    
    # File 2: After data (with some intentional differences and join key mismatches)
    file2_data = {
        'ID': [1, 2, 99, 4, 5, 6, 7, 8],  # Charlie's ID changed from 3 to 99
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Franklin', 'Grace', 'Henry'],  # Frank's name changed to Franklin
        'Department': ['IT', 'HR', 'IT', 'Finance', 'HR', 'IT', 'Finance', 'HR'],
        'Salary': [51000, 45000, 55000, 62000, 48000, 52000, 58000, 47000],  # Some salary changes
        'Bonus': [5100, 4000, 5500, 6200, 4800, 5200, 5800, 4700]  # Some bonus changes
    }
    
    # Create DataFrames
    df1 = pd.DataFrame(file1_data)
    df2 = pd.DataFrame(file2_data)
    
    # Write CSV files
    df1.to_csv('demo/file1_before.csv', index=False)
    df2.to_csv('demo/file2_after.csv', index=False)
    
    print("Simple CSV demo files created:")
    print("  - demo/file1_before.csv (8 records)")
    print("  - demo/file2_after.csv (8 records)")
    print("\nSample data from file1_before.csv:")
    print(df1.head())
    print("\nSample data from file2_after.csv:")
    print(df2.head())
    
    return df1, df2

if __name__ == "__main__":
    create_simple_csv_demo()
