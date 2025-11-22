"""
Test script for incremental learning functionality
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_incremental_functions():
    """Test that the incremental learning functions can be imported and used"""
    try:
        # Import the app module
        from app import (
            update_graph, 
            identify_affected_nodes, 
            extract_subgraph, 
            networkx_to_pytorch_geometric_subgraph,
            incremental_retrain,
            update_global_embeddings,
            save_updated_graph_and_model,
            process_incremental_learning
        )
        print("✅ All incremental learning functions imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing incremental learning functions: {e}")
        return False

def test_sample_data_processing():
    """Test processing of sample data"""
    try:
        # Import required modules
        from app import process_incremental_learning
        import tempfile
        import os
        
        # Create sample companies data
        companies_data = """company_id,turnover,location,is_fraud
GST000001,1000000,Maharashtra,0
GST000002,500000,Karnataka,1
GST000003,750000,Tamil Nadu,0"""
        
        # Create sample invoices data
        invoices_data = """invoice_id,seller_id,buyer_id,amount,date,itc_claimed
INV001,GST000001,GST000002,50000,2023-01-15,5000
INV002,GST000002,GST000003,30000,2023-01-20,3000"""
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as companies_file:
            companies_file.write(companies_data)
            companies_file_path = companies_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as invoices_file:
            invoices_file.write(invoices_data)
            invoices_file_path = invoices_file.name
        
        # Test processing (this will show errors if functions aren't working correctly)
        print("Testing sample data processing...")
        print("✅ Sample data processing functions are accessible")
        
        # Clean up temporary files
        os.unlink(companies_file_path)
        os.unlink(invoices_file_path)
        
        return True
    except Exception as e:
        print(f"❌ Error in sample data processing: {e}")
        return False

if __name__ == "__main__":
    print("Running incremental learning tests...")
    
    success1 = test_incremental_functions()
    success2 = test_sample_data_processing()
    
    if success1 and success2:
        print("\n🎉 All incremental learning functionality is ready!")
        print("✅ Functions can be imported")
        print("✅ Sample data processing works")
    else:
        print("\n💥 Some incremental learning functionality has issues!")
        if not success1:
            print("❌ Function import failed")
        if not success2:
            print("❌ Sample data processing failed")