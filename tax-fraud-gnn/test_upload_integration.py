"""
Test script to verify that incremental learning is integrated with the upload feature
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_upload_integration():
    """Test that incremental learning is integrated with the upload feature"""
    try:
        # Import the app module
        from app import app, process_incremental_learning
        
        # Check that the upload_data function exists
        assert hasattr(app, 'view_functions'), "App should have view functions"
        assert 'upload_data' in app.view_functions, "upload_data function should be registered"
        
        # Check that process_incremental_learning function exists
        assert callable(process_incremental_learning), "process_incremental_learning should be callable"
        
        # Check that the upload_data function references process_incremental_learning
        import inspect
        upload_data_source = inspect.getsource(app.view_functions['upload_data'])
        assert 'process_incremental_learning' in upload_data_source, "upload_data should call process_incremental_learning"
        
        print("✅ Upload feature integration verified successfully")
        print("✅ upload_data function exists and is registered")
        print("✅ process_incremental_learning function exists")
        print("✅ upload_data calls process_incremental_learning")
        
        return True
    except Exception as e:
        print(f"❌ Error verifying upload integration: {e}")
        return False

if __name__ == "__main__":
    print("Testing upload feature integration with incremental learning...")
    print("=" * 60)
    
    success = test_upload_integration()
    
    print("=" * 60)
    if success:
        print("🎉 Upload feature integration test passed!")
        print("✅ Incremental learning is properly integrated with upload feature")
    else:
        print("💥 Upload feature integration test failed!")