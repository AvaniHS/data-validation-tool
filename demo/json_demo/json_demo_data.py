#!/usr/bin/env python3
"""
JSON Demo Data Generator
Creates sample JSON files for data validation demo with intentional mismatches.
"""

import json
import os
from datetime import datetime

def create_json_demo_data():
    """Create JSON demo data with intentional mismatches for testing."""
    
    # Create demo directory if it doesn't exist
    os.makedirs('demo/json_demo', exist_ok=True)
    
    # Sample data for file1_before.json
    file1_data = [
        {"ID": 1, "Name": "Alice", "Department": "IT", "Salary": 50000, "Bonus": 5000},
        {"ID": 2, "Name": "Bob", "Department": "HR", "Salary": 45000, "Bonus": 4000},
        {"ID": 3, "Name": "Charlie", "Department": "IT", "Salary": 55000, "Bonus": 5500},
        {"ID": 4, "Name": "Diana", "Department": "Finance", "Salary": 60000, "Bonus": 6000},
        {"ID": 5, "Name": "Eve", "Department": "HR", "Salary": 48000, "Bonus": 4800},
        {"ID": 6, "Name": "Frank", "Department": "IT", "Salary": 52000, "Bonus": 5200},
        {"ID": 7, "Name": "Grace", "Department": "Finance", "Salary": 58000, "Bonus": 5800},
        {"ID": 8, "Name": "Henry", "Department": "HR", "Salary": 47000, "Bonus": 4700}
    ]
    
    # Sample data for file2_after.json with intentional mismatches
    file2_data = [
        {"ID": 1, "Name": "Alice", "Department": "IT", "Salary": 51000, "Bonus": 5100},  # Salary/Bonus changed
        {"ID": 2, "Name": "Bob", "Department": "HR", "Salary": 45000, "Bonus": 4000},    # No change
        {"ID": 99, "Name": "Franklin", "Department": "IT", "Salary": 55000, "Bonus": 5500},  # ID and Name changed
        {"ID": 4, "Name": "Diana", "Department": "Finance", "Salary": 62000, "Bonus": 6200},  # Salary/Bonus changed
        {"ID": 5, "Name": "Eve", "Department": "HR", "Salary": 48000, "Bonus": 4800},    # No change
        {"ID": 6, "Name": "Frank", "Department": "IT", "Salary": 52000, "Bonus": 5200},  # No change
        {"ID": 7, "Name": "Grace", "Department": "Finance", "Salary": 58000, "Bonus": 5800},  # No change
        {"ID": 8, "Name": "Henry", "Department": "HR", "Salary": 47000, "Bonus": 4700}   # No change
    ]
    
    # Write file1_before.json
    file1_path = os.path.abspath('demo/json_demo/file1_before.json')
    with open(file1_path, 'w') as f:
        json.dump(file1_data, f, indent=2)
    print(f"✓ Created: {file1_path}")
    
    # Write file2_after.json
    file2_path = os.path.abspath('demo/json_demo/file2_after.json')
    with open(file2_path, 'w') as f:
        json.dump(file2_data, f, indent=2)
    print(f"✓ Created: {file2_path}")
    
    print(f"\n📊 Demo Data Summary:")
    print(f"  File1 records: {len(file1_data)}")
    print(f"  File2 records: {len(file2_data)}")
    print(f"  Intentional mismatches:")
    print(f"    - Row 2: ID 3→99, Name Charlie→Franklin")
    print(f"    - Row 0: Salary 50000→51000, Bonus 5000→5100")
    print(f"    - Row 3: Salary 60000→62000, Bonus 6000→6200")
    
    return file1_path, file2_path

if __name__ == "__main__":
    create_json_demo_data()
