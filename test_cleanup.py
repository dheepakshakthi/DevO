#!/usr/bin/env python3
"""
Test script to verify the cleanup function works correctly on Windows
"""
import os
import sys
import tempfile
import stat
import shutil
from pathlib import Path

def test_cleanup_function():
    """Test the Windows-compatible cleanup function"""
    print("Testing Windows-compatible cleanup function...")
    
    # Create a temporary directory structure similar to a Git repo
    test_dir = tempfile.mkdtemp(prefix="test_cleanup_")
    print(f"Created test directory: {test_dir}")
    
    try:
        # Create some nested directories and files
        nested_dir = os.path.join(test_dir, "nested", "deep", "structure")
        os.makedirs(nested_dir, exist_ok=True)
        
        # Create some files
        test_file = os.path.join(nested_dir, "test_file.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        
        # Make one file readonly to simulate Git object files
        readonly_file = os.path.join(nested_dir, "readonly_file.txt")
        with open(readonly_file, "w") as f:
            f.write("readonly content")
        os.chmod(readonly_file, stat.S_IREAD)
        
        print("✅ Test directory structure created successfully")
        
        # Test the cleanup function
        def force_remove_directory(path: str):
            """Force remove directory on Windows by handling file permissions"""
            def handle_remove_readonly(func, path, exc):
                """Handle removal of readonly files on Windows"""
                if os.path.exists(path):
                    # Make the file writable and try again
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
            
            # Use onerror parameter to handle permission issues
            shutil.rmtree(path, onerror=handle_remove_readonly)
        
        # Try to remove the directory
        force_remove_directory(test_dir)
        
        # Check if directory was removed
        if not os.path.exists(test_dir):
            print("✅ Cleanup function works correctly!")
            return True
        else:
            print("❌ Cleanup function failed - directory still exists")
            return False
            
    except Exception as e:
        print(f"❌ Error during cleanup test: {str(e)}")
        # Try to clean up manually
        try:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir, ignore_errors=True)
        except:
            self.log(f"Exception occurred: {e}", "ERROR")
        return False

if __name__ == "__main__":
    success = test_cleanup_function()
    sys.exit(0 if success else 1)