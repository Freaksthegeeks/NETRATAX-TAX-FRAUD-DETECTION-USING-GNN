"""
Test script to verify that the incremental learning process is working
"""

import sys
from pathlib import Path
import tempfile
import os

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_incremental_process():
    """Test that the incremental learning process works"""
    try:
        # Import the app module
        from app import process_incremental_learning, load_model_and_data
        import pandas as pd
        
        # Load model and data first
        print("Loading model and data...")
        load_model_and_data()
        
        # Create a sample invoices CSV file
        invoices_data = """invoice_id,seller_id,buyer_id,amount,date,itc_claimed
INV001,GST000001,GST000002,50000,2023-01-15,5000
INV002,GST000002,GST000003,30000,2023-01-20,3000
INV003,GST000003,GST000001,25000,2023-01-25,2500"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(invoices_data)
            temp_file_path = f.name
        
        print(f"Created temporary file: {temp_file_path}")
        
        # Test the incremental learning process
        print("Testing incremental learning process...")
        process_incremental_learning(temp_file_path, "test_invoices.csv")
        
        # Clean up
        os.unlink(temp_file_path)
        
        print("✅ Incremental learning process completed successfully")
        return True
    except Exception as e:
        print(f"❌ Error in incremental learning process: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing incremental learning process...")
    print("=" * 50)
    
    success = test_incremental_process()
    
    print("=" * 50)
    if success:
        print("🎉 Incremental learning process test passed!")
    else:
        print("💥 Incremental learning process test failed!")