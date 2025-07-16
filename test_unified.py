#!/usr/bin/env python3
"""
Quick test script for DevO Unified Chat System
Tests all components and provides system diagnostics
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test all required imports"""
    print("🧪 Testing imports...")
    
    results = {}
    
    # Core dependencies
    try:
        import rich
        results['rich'] = f"✅ {rich.__version__}"
    except ImportError as e:
        results['rich'] = f"❌ {e}"
    
    try:
        import click
        results['click'] = f"✅ {click.__version__}"
    except ImportError as e:
        results['click'] = f"❌ {e}"
    
    try:
        import google.generativeai as genai
        results['google-generativeai'] = "✅ Available"
    except ImportError as e:
        results['google-generativeai'] = f"❌ {e}"
    
    try:
        import psutil
        results['psutil'] = f"✅ {psutil.__version__}"
    except ImportError as e:
        results['psutil'] = f"❌ {e}"
    
    try:
        import requests
        results['requests'] = f"✅ {requests.__version__}"
    except ImportError as e:
        results['requests'] = f"❌ {e}"
    
    # Optional dependencies
    try:
        import torch
        cuda_info = f" (CUDA: {torch.cuda.is_available()})" if hasattr(torch.cuda, 'is_available') else ""
        results['torch'] = f"✅ {torch.__version__}{cuda_info}"
    except ImportError as e:
        results['torch'] = f"⚠️  Not available: {e}"
    
    try:
        import transformers
        results['transformers'] = f"✅ {transformers.__version__}"
    except ImportError as e:
        results['transformers'] = f"⚠️  Not available: {e}"
    
    # Print results
    print("\n📋 Import Test Results:")
    for package, status in results.items():
        print(f"   {package}: {status}")
    
    return results

def test_system_info():
    """Display system information"""
    print("\n💻 System Information:")
    
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"   RAM: {memory.total / (1024**3):.1f} GB total, {memory.available / (1024**3):.1f} GB available")
        print(f"   CPU: {psutil.cpu_count()} cores")
    except:
        print("   System info not available")
    
    try:
        import torch
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                name = torch.cuda.get_device_name(i)
                memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                print(f"   GPU {i}: {name} ({memory:.1f} GB)")
        else:
            print("   GPU: Not available or no CUDA support")
    except:
        print("   GPU: PyTorch not available")

def test_local_modules():
    """Test local module imports"""
    print("\n🔧 Testing local modules...")
    
    modules = ['local_llm', 'utils', 'templates', 'auto_setup']
    
    for module in modules:
        try:
            __import__(module)
            print(f"   ✅ {module}.py")
        except ImportError as e:
            print(f"   ❌ {module}.py: {e}")
        except Exception as e:
            print(f"   ⚠️  {module}.py: {e}")

def test_config_files():
    """Test configuration files"""
    print("\n⚙️  Testing configuration files...")
    
    files = {
        '.env': 'Environment variables',
        'local_llm_config.json': 'Local LLM configuration',
        'models/': 'Models directory'
    }
    
    for file_path, description in files.items():
        path = Path(file_path)
        if path.exists():
            if path.is_dir():
                contents = list(path.iterdir())
                print(f"   ✅ {description}: {len(contents)} items")
            else:
                print(f"   ✅ {description}")
        else:
            print(f"   ⚠️  {description}: Not found")

def test_api_key():
    """Test API key availability"""
    print("\n🔑 Testing API configuration...")
    
    # Check environment variable
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"   ✅ GEMINI_API_KEY: {masked_key}")
    else:
        print("   ⚠️  GEMINI_API_KEY: Not set")
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        print("   ✅ .env file exists")
        try:
            content = env_file.read_text()
            if 'GEMINI_API_KEY' in content:
                print("   ✅ .env contains GEMINI_API_KEY")
            else:
                print("   ⚠️  .env missing GEMINI_API_KEY")
        except:
            print("   ⚠️  Could not read .env file")
    else:
        print("   ⚠️  .env file not found")

def test_unified_chat():
    """Test unified chat module"""
    print("\n🤖 Testing unified chat...")
    
    try:
        from unified_chat import UnifiedChatSession, MemoryManager, MemoryConfig
        print("   ✅ UnifiedChatSession import successful")
        
        # Test memory manager
        config = MemoryConfig()
        memory_manager = MemoryManager(config)
        usage = memory_manager.get_memory_usage()
        print(f"   ✅ Memory manager working: {usage['used_gb']:.1f}GB used")
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")

def main():
    """Run all tests"""
    print("🎯 DevO Unified Chat System Test")
    print("=" * 40)
    
    # Run all tests
    test_imports()
    test_system_info()
    test_local_modules()
    test_config_files()
    test_api_key()
    test_unified_chat()
    
    print("\n" + "=" * 40)
    print("🎉 Test completed!")
    print("\n💡 Tips:")
    print("   - If imports fail, run: python setup_unified.py")
    print("   - Set GEMINI_API_KEY in .env file for cloud AI")
    print("   - Use 'launch_unified_chat.bat' to start the assistant")

if __name__ == "__main__":
    main()
