#!/usr/bin/env python3
"""
Quick Test for Enhanced DevO Chat
Tests both local and cloud AI functionality
"""

import os
import sys
from pathlib import Path

def test_basic_imports():
    """Test basic imports"""
    print("🧪 Testing basic imports...")
    
    try:
        import rich
        print("✅ Rich available")
    except ImportError:
        print("❌ Rich not available - install with: pip install rich")
        return False
    
    try:
        import click
        print("✅ Click available")
    except ImportError:
        print("❌ Click not available - install with: pip install click")
        return False
    
    return True

def test_gemini_api():
    """Test Gemini API functionality"""
    print("\n🌤️  Testing Gemini API...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  GEMINI_API_KEY not set - cloud AI unavailable")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Test with a simple prompt
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content("Hello! Say 'AI test successful' if you can hear me.")
        
        if "successful" in response.text.lower():
            print("✅ Gemini API working")
            return True
        else:
            print("⚠️  Gemini API responding but unexpected output")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API failed: {e}")
        return False

def test_local_ai():
    """Test local AI functionality"""
    print("\n🧠 Testing Local AI...")
    
    try:
        # Try importing torch
        import torch
        cuda_available = torch.cuda.is_available()
        print(f"✅ PyTorch available (CUDA: {cuda_available})")
        
        if cuda_available:
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
            print(f"🚀 GPU: {gpu_name} ({gpu_count} device(s))")
    except ImportError:
        print("⚠️  PyTorch not available - install for local AI support")
        return False
    
    try:
        import transformers
        print("✅ Transformers available")
    except ImportError:
        print("⚠️  Transformers not available - install for local AI support")
        return False
    
    # Test local LLM manager if available
    try:
        from local_llm import LocalLLMManager
        llm = LocalLLMManager()
        print("✅ Local LLM manager available")
        
        # Test model listing
        models = llm.list_available_models()
        print(f"📋 Available models: {len(models)} configurations")
        
        return True
    except Exception as e:
        print(f"⚠️  Local LLM manager failed: {e}")
        return False

def test_enhanced_chat():
    """Test enhanced chat system"""
    print("\n💬 Testing Enhanced Chat System...")
    
    try:
        # Test imports
        from chat_enhanced import EnhancedDevOChatSession
        print("✅ Enhanced chat imports successful")
        
        # Test initialization (dry run)
        session = EnhancedDevOChatSession(
            api_key=os.getenv('GEMINI_API_KEY'),
            repo_path='.',
            use_local=True,
            local_model='codellama'
        )
        print("✅ Enhanced chat session creation successful")
        
        return True
    except Exception as e:
        print(f"❌ Enhanced chat test failed: {e}")
        return False

def test_automation():
    """Test automation features"""
    print("\n🔧 Testing Automation Features...")
    
    try:
        from auto_setup import AutoSetupManager
        print("✅ Auto setup manager available")
    except Exception as e:
        print(f"⚠️  Auto setup manager failed: {e}")
    
    try:
        from local_llm import AutomationManager, LocalLLMManager
        print("✅ Automation manager available")
    except Exception as e:
        print(f"⚠️  Automation manager failed: {e}")
    
    return True

def main():
    """Run all tests"""
    print("="*60)
    print("🚀 Enhanced DevO Chat - System Test")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Basic Imports", test_basic_imports()))
    results.append(("Gemini API", test_gemini_api()))
    results.append(("Local AI", test_local_ai()))
    results.append(("Enhanced Chat", test_enhanced_chat()))
    results.append(("Automation", test_automation()))
    
    # Show results
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Enhanced DevO Chat is ready to use.")
        print("\n🚀 Run with: python chat_enhanced.py")
        print("   Or use: launch_enhanced_chat.bat")
    else:
        print("\n⚠️  Some tests failed. Check installation and configuration.")
        print("\n💡 Setup help:")
        print("   1. Run: python setup_enhanced.py")
        print("   2. Set GEMINI_API_KEY environment variable")
        print("   3. Install: pip install -r requirements_unified.txt")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
