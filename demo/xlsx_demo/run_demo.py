"""Quick script to run the demo validation."""

import subprocess
import sys
import os

def run_demo():
    """Run the demo validation."""
    print("🚀 Starting Data Validation Tool Demo...")
    print("=" * 50)
    
    # Check if demo files exist
    if not os.path.exists("demo/sales_demo_data.xlsx"):
        print("❌ Demo Excel file not found. Please run demo_data.py first.")
        return
    
    if not os.path.exists("demo/demo_config.json"):
        print("❌ Demo config file not found.")
        return
    
    print("✅ Demo files found")
    print("📊 Running validation with demo data...")
    print()
    
    # Run the validation
    try:
        result = subprocess.run([
            sys.executable, "run_validation.py", 
            "--config", "demo/demo_config.json"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Validation completed successfully!")
            print()
            print("📁 Output files generated:")
            print("   - demo/validation_results.xlsx")
            print()
            print("📋 Review the results to see:")
            print("   - Validation_Summary sheet: Row-by-row comparison")
            print("   - join_analysis sheet: Detailed join failure analysis")
            print()
            print("🎯 Demo scenarios demonstrated:")
            print("   - Data type mismatches (Month_No: int vs string)")
            print("   - Format differences (HQ123 vs HQ-123)")
            print("   - Missing data (NULL Customer_ID values)")
            print("   - Value differences (Sales_Amount, Quantity_Sold)")
            print("   - Metrics comparison (Delta and Percentage Delta)")
            print("   - Join key analysis (5 different join keys)")
        else:
            print("❌ Validation failed:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error running demo: {e}")

if __name__ == "__main__":
    run_demo()
