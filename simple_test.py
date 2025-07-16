#!/usr/bin/env python3
"""
Simple Test for Enhanced DevO Chat - Windows Compatible
Avoids Unicode/emoji issues that cause encoding errors
"""

import os
import sys
import subprocess
from pathlib import Path

def print_safe(message):
    """Print message safely, handling encoding issues"""
    try:
        print(message)
    except UnicodeEncodeError:
        # Fallback to ASCII-safe version
        safe_message = message.encode('ascii', 'replace').decode('ascii')
        print(safe_message)

def test_basic_imports():
    """Test basic imports"""
    print_safe("Testing basic imports...")
    
    try:
        import rich
        print_safe("Rich: OK")
    except ImportError:
        print_safe("Rich: FAILED - install with: pip install rich")
        return False
    
    try:
        import click
        print_safe("Click: OK")
    except ImportError:
        print_safe("Click: FAILED - install with: pip install click")
        return False
    
    try:
        import requests
        print_safe("Requests: OK")
    except ImportError:
        print_safe("Requests: FAILED - install with: pip install requests")
        return False
    
    return True

def test_optional_imports():
    """Test optional imports"""
    print_safe("\nTesting optional dependencies...")
    
    results = {}
    
    try:
        import google.generativeai
        print_safe("Gemini API: OK")
        results['gemini'] = True
    except ImportError:
        print_safe("Gemini API: Not available (optional)")
        results['gemini'] = False
    
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        print_safe(f"PyTorch: OK (CUDA: {cuda_available})")
        results['torch'] = True
    except ImportError:
        print_safe("PyTorch: Not available (local AI disabled)")
        results['torch'] = False
    
    try:
        import transformers
        print_safe("Transformers: OK")
        results['transformers'] = True
    except ImportError:
        print_safe("Transformers: Not available (local AI disabled)")
        results['transformers'] = False
    
    return results

def test_file_structure():
    """Test file structure"""
    print_safe("\nChecking file structure...")
    
    required_files = [
        'chat_enhanced.py',
        'local_llm.py', 
        'utils.py',
        'templates.py',
        'auto_setup.py'
    ]
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print_safe(f"{file}: Found")
        else:
            print_safe(f"{file}: Missing")
            missing_files.append(file)
    
    # Check models directory
    models_dir = Path("models")
    if models_dir.exists():
        ggml_files = list(models_dir.glob("*.bin")) + list(models_dir.glob("*.gguf"))
        ggml_files += list(models_dir.glob("ggml/*.bin")) + list(models_dir.glob("ggml/*.gguf"))
        print_safe(f"Models directory: Found ({len(ggml_files)} GGML files)")
    else:
        print_safe("Models directory: Not found")
    
    return len(missing_files) == 0

def test_simple_ai():
    """Test simple AI functionality without complex imports"""
    print_safe("\nTesting AI functionality...")
    
    # Test Gemini API if available
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            
            # Simple test
            response = model.generate_content("Say 'test successful' if you can read this.")
            if "successful" in response.text.lower():
                print_safe("Gemini API: Working")
                return True
            else:
                print_safe("Gemini API: Responding but unexpected output")
        except Exception as e:
            print_safe(f"Gemini API: Error - {str(e)[:50]}...")
    else:
        print_safe("Gemini API: No API key set (optional)")
    
    # Test local imports
    try:
        from local_llm import LocalLLMManager
        print_safe("Local LLM imports: OK")
        return True
    except Exception as e:
        print_safe(f"Local LLM imports: Failed - {str(e)[:50]}...")
    
    return False

def main():
    """Run all tests"""
    print_safe("=" * 60)
    print_safe("Enhanced DevO Chat - Simple Test")
    print_safe("=" * 60)
    
    # Test basic functionality
    basic_ok = test_basic_imports()
    optional_results = test_optional_imports()
    files_ok = test_file_structure()
    ai_ok = test_simple_ai()
    
    # Summary
    print_safe("\n" + "=" * 60)
    print_safe("Test Results Summary")
    print_safe("=" * 60)
    
    print_safe(f"Basic imports: {'PASS' if basic_ok else 'FAIL'}")
    print_safe(f"File structure: {'PASS' if files_ok else 'FAIL'}")
    print_safe(f"AI functionality: {'PASS' if ai_ok else 'FAIL'}")
    
    if optional_results.get('gemini'):
        print_safe("Gemini API: Available")
    if optional_results.get('torch'):
        print_safe("PyTorch: Available")
    if optional_results.get('transformers'):
        print_safe("Transformers: Available")
    
    # Overall result
    if basic_ok and files_ok:
        print_safe("\nResult: BASIC FUNCTIONALITY READY")
        print_safe("You can run: python chat_enhanced.py")
        if optional_results.get('gemini'):
            print_safe("Cloud AI: Available (set GEMINI_API_KEY)")
        if optional_results.get('torch') and optional_results.get('transformers'):
            print_safe("Local AI: Available (use --use-local)")
    else:
        print_safe("\nResult: SETUP INCOMPLETE")
        print_safe("Run setup script: quick_setup.bat")
    
    return basic_ok and files_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print_safe(f"Test failed with error: {e}")
        sys.exit(1)
