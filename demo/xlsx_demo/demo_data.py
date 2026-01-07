"""Script to create demo Excel file with sample data for validation tool demonstration."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def create_demo_data():
    """Create realistic business data for demonstration."""
    
    # Set random seed for reproducible data
    np.random.seed(42)
    random.seed(42)
    
    # Create base data for both sheets
    regions = ['North', 'South', 'East', 'West', 'Central']
    products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    customers = ['CUST001', 'CUST002', 'CUST003', 'CUST004', 'CUST005', 'CUST006', 'CUST007', 'CUST008']
    
    # Generate 50 records for each sheet
    n_records = 50
    
    # Sheet 1: Q1 Sales Data (Before)
    q1_data = []
    for i in range(n_records):
        record = {
            'Month_No': 202501 + (i % 3),  # Jan, Feb, Mar 2025
            'Reporter_HQ_ID': f"HQ{random.randint(100, 999)}",
            'Buyer_HQ_ID': f"HQ{random.randint(100, 999)}",
            'Customer_ID': random.choice(customers),
            'Product_Code': random.choice(products),
            'Region': random.choice(regions),
            'Sales_Amount': round(random.uniform(1000, 50000), 2),
            'Quantity_Sold': random.randint(1, 100),
            'Discount_Percent': round(random.uniform(0, 20), 2),
            'Sales_Rep': f"Rep{random.randint(1, 10)}"
        }
        q1_data.append(record)
    
    # Sheet 2: Q1 Sales Data (After) - with some intentional differences
    q2_data = []
    for i in range(n_records):
        # Copy most data from Q1 but introduce some changes
        base_record = q1_data[i].copy()
        
        # Introduce some data quality issues for demonstration
        if i % 10 == 0:  # Every 10th record has issues
            if i % 30 == 0:
                # Missing data
                base_record['Customer_ID'] = None
            elif i % 30 == 10:
                # Different value
                base_record['Sales_Amount'] = round(base_record['Sales_Amount'] * 1.1, 2)
            elif i % 30 == 20:
                # Different format
                base_record['Reporter_HQ_ID'] = f"HQ-{random.randint(100, 999)}"
        
        # Some records have different data types
        if i % 15 == 0:
            base_record['Month_No'] = str(base_record['Month_No'])  # String instead of int
        
        # Some records have different values
        if i % 20 == 0:
            base_record['Quantity_Sold'] = base_record['Quantity_Sold'] + 5
        
        q2_data.append(base_record)
    
    # Create DataFrames
    df_q1 = pd.DataFrame(q1_data)
    df_q2 = pd.DataFrame(q2_data)
    
    # Add some additional columns for metrics demonstration
    df_q1['Profit_Margin'] = round(df_q1['Sales_Amount'] * 0.15, 2)
    df_q1['Commission'] = round(df_q1['Sales_Amount'] * 0.05, 2)
    
    df_q2['Profit_Margin'] = round(df_q2['Sales_Amount'] * 0.12, 2)  # Different margin
    df_q2['Commission'] = round(df_q2['Sales_Amount'] * 0.06, 2)     # Different commission
    
    return df_q1, df_q2

def create_demo_excel():
    """Create the demo Excel file."""
    df_q1, df_q2 = create_demo_data()
    
    # Create Excel file with two sheets
    with pd.ExcelWriter('demo/sales_demo_data.xlsx', engine='openpyxl') as writer:
        df_q1.to_excel(writer, sheet_name='Q1_Before', index=False)
        df_q2.to_excel(writer, sheet_name='Q1_After', index=False)
    
    print("Demo Excel file created: demo/sales_demo_data.xlsx")
    print(f"Q1_Before sheet: {len(df_q1)} records")
    print(f"Q1_After sheet: {len(df_q2)} records")
    print("\nSample data from Q1_Before:")
    print(df_q1.head())
    print("\nSample data from Q1_After:")
    print(df_q2.head())

if __name__ == "__main__":
    create_demo_excel()
