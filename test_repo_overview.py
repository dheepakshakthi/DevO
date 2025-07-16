#!/usr/bin/env python3
"""
Test script to verify repository overview functionality
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from chat import DevOChatSession

def test_repository_overview():
    """Test repository overview functionality"""
    print("Testing DevO Chat Repository Overview...")
    
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No API key found. Please set GEMINI_API_KEY environment variable.")
        return False
    
    try:
        # Create chat session
        session = DevOChatSession(api_key, '.')
        
        # Test repository context
        if session.repo_context:
            print("✅ Repository context created successfully")
            print(f"   - Language: {session.repo_context.get('language', 'Unknown')}")
            print(f"   - Framework: {session.repo_context.get('framework', 'Unknown')}")
            print(f"   - Package Manager: {session.repo_context.get('package_manager', 'Unknown')}")
            print(f"   - Total Files: {session.repo_context.get('total_files', 0)}")
            print(f"   - Dependencies: {len(session.repo_context.get('dependencies', []))}")
            print(f"   - Config Files: {len(session.repo_context.get('config_files', {}))}")
            
            # Test display function
            print("\n📊 Repository Overview Display:")
            session._display_repository_overview()
            
            return True
        else:
            print("❌ Repository context not created")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == '__main__':
    success = test_repository_overview()
    if success:
        print("\n🎉 Repository overview test passed!")
        sys.exit(0)
    else:
        print("\n❌ Repository overview test failed!")
        sys.exit(1)
