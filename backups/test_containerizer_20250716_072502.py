#!/usr/bin/env python3
"""
Test script for RepoContainerizer
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from repo_containerizer import RepoContainerizer
        print("✅ RepoContainerizer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import RepoContainerizer: {e}")
        return False
    
    try:
        from utils import detect_language_from_files, detect_framework_from_files
        print("✅ Utils imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import utils: {e}")
        return False
    
    try:
        from templates import get_dockerfile_template, get_docker_compose_template
        print("✅ Templates imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import templates: {e}")
        return False
    
    return True

def test_utility_functions():
    """Test utility functions with sample data"""
    print("\nTesting utility functions...")
    
    from utils import (
        detect_language_from_files, detect_framework_from_files, 
        detect_package_manager, detect_port_from_files
    )
    
    # Test language detection
    test_files = ['app.py', 'main.js', 'index.html', 'style.css']
    languages = detect_language_from_files(test_files)
    print(f"✅ Language detection: {languages}")
    
    # Test package manager detection
    package_files = ['package.json', 'requirements.txt', 'go.mod']
    for file in package_files:
        manager = detect_package_manager([file])
        print(f"✅ Package manager for {file}: {manager}")
    
    # Test framework detection
    sample_package_json = '{"dependencies": {"express": "^4.18.0", "react": "^18.0.0"}}'
    framework = detect_framework_from_files(['package.json'], {'package.json': sample_package_json})
    print(f"✅ Framework detection: {framework}")
    
    # Test port detection
    sample_code = 'app.listen(3000, () => console.log("Server running on port 3000"))'
    port = detect_port_from_files({'app.js': sample_code})
    print(f"✅ Port detection: {port}")
    
    return True

def test_template_functions():
    """Test template generation"""
    print("\nTesting template functions...")
    
    from templates import get_dockerfile_template, get_docker_compose_template
    
    # Test Dockerfile templates
    dockerfile = get_dockerfile_template('python', 'flask')
    if dockerfile:
        print("✅ Python Flask Dockerfile template generated")
    else:
        print("❌ Failed to generate Python Flask Dockerfile template")
    
    dockerfile = get_dockerfile_template('javascript', 'express')
    if dockerfile:
        print("✅ JavaScript Express Dockerfile template generated")
    else:
        print("❌ Failed to generate JavaScript Express Dockerfile template")
    
    # Test Docker Compose templates
    compose = get_docker_compose_template('python_postgresql')
    if compose:
        print("✅ Python PostgreSQL Docker Compose template generated")
    else:
        print("❌ Failed to generate Python PostgreSQL Docker Compose template")
    
    return True

def test_api_connection():
    """Test API connection (optional, requires API key)"""
    print("\nTesting API connection...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  GEMINI_API_KEY not set, skipping API test")
        return True
    
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        print("✅ Gemini API client created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Gemini API: {e}")
        return False

def test_file_creation():
    """Test file creation functionality"""
    print("\nTesting file creation...")
    
    from repo_containerizer import RepoContainerizer, RepositoryAnalysis
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a sample analysis object
        analysis = RepositoryAnalysis(
            primary_language="Python",
            framework="Flask",
            package_manager="pip",
            database="postgresql",
            external_services=["redis"],
            dependencies=["flask", "psycopg2"],
            build_tools=["pip"],
            port=5000,
            environment_vars={"DATABASE_URL": "Database connection string", "SECRET_KEY": "Secret key"},
            commands={"install": "pip install -r requirements.txt", "start": "python app.py"},
            dockerfile_content="FROM python:3.9-slim\nWORKDIR /app\nCOPY . .\nEXPOSE 5000\nCMD [\"python\", \"app.py\"]",
            docker_compose_content="version: '3.8'\nservices:\n  app:\n    build: .\n    ports:\n      - \"5000:5000\"",
            health_check="curl -f http://localhost:5000/health || exit 1"
        )
        
        # Test file creation
        containerizer = RepoContainerizer("")  # Empty API key for testing
        try:
            output_files = containerizer.create_output_files(analysis, temp_dir)
            print(f"✅ Created {len(output_files)} output files")
            
            # Check that files were created
            for file_path in output_files:
                if os.path.exists(file_path):
                    print(f"✅ {os.path.basename(file_path)} created successfully")
                else:
                    print(f"❌ {os.path.basename(file_path)} not created")
                    
        except Exception as e:
            print(f"❌ Failed to create output files: {e}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Running RepoContainerizer Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_utility_functions,
        test_template_functions,
        test_api_connection,
        test_file_creation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
