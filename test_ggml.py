#!/usr/bin/env python3
"""
Quick GGML Model Test
Test your llama-2-7b-chat.ggmlv3.q8_0.bin model
"""

import sys
from pathlib import Path

def test_ggml_model():
    """Quick test of GGML model functionality"""
    print("🤖 Testing GGML Model Support...")
    
    # Test 1: Check if llama-cpp-python is available
    try:
        from llama_cpp import Llama
        print("✅ llama-cpp-python is available")
    except ImportError:
        print("❌ llama-cpp-python not installed")
        print("💡 Install with: pip install llama-cpp-python")
        return False
    
    # Test 2: Check if models directory exists
    models_dir = Path("models")
    if models_dir.exists():
        print(f"✅ Models directory found: {models_dir.resolve()}")
    else:
        print("❌ Models directory not found")
        print("💡 Create with: mkdir models")
        return False
    
    # Test 3: Look for GGML model files
    ggml_files = []
    for ext in ['.bin', '.gguf', '.ggml']:
        ggml_files.extend(models_dir.glob(f'*{ext}'))
    
    if ggml_files:
        print(f"✅ Found {len(ggml_files)} GGML model(s):")
        for model_file in ggml_files:
            size_mb = round(model_file.stat().st_size / (1024 * 1024), 2)
            print(f"   📄 {model_file.name} ({size_mb} MB)")
    else:
        print("❌ No GGML models found in models directory")
        print("💡 Copy your llama-2-7b-chat.ggmlv3.q8_0.bin to the models folder")
        return False
    
    # Test 4: Try to load a model
    print("\n🚀 Testing model loading...")
    
    # Find llama-2 model specifically
    llama2_model = None
    for model_file in ggml_files:
        if 'llama' in model_file.name.lower() and '2' in model_file.name:
            llama2_model = model_file
            break
    
    if not llama2_model:
        # Use the first available model
        llama2_model = ggml_files[0]
    
    try:
        print(f"📂 Loading model: {llama2_model.name}")
        
        # Load with basic settings
        model = Llama(
            model_path=str(llama2_model),
            n_ctx=2048,  # Context length
            n_threads=4,  # CPU threads
            verbose=False
        )
        
        print("✅ Model loaded successfully!")
        
        # Test 5: Try generation
        print("\n💬 Testing text generation...")
        
        test_prompt = "Hello! Please write a simple Python function that adds two numbers:"
        
        response = model(
            test_prompt,
            max_tokens=150,
            temperature=0.7,
            echo=False
        )
        
        generated_text = response['choices'][0]['text']
        
        print("✅ Generation successful!")
        print(f"\n📝 Test prompt: {test_prompt}")
        print(f"🤖 Response: {generated_text.strip()}")
        
        # Model info
        print(f"\n📊 Model Info:")
        print(f"   Name: {llama2_model.name}")
        print(f"   Size: {round(llama2_model.stat().st_size / (1024 * 1024), 2)} MB")
        print(f"   Context: 2048 tokens")
        print(f"   Threads: 4")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        print("💡 This might be due to:")
        print("   - Incompatible model format")
        print("   - Insufficient memory")
        print("   - Corrupted model file")
        return False

def main():
    print("=" * 60)
    print("🤖 GGML Model Quick Test for DevO Chat")
    print("=" * 60)
    print()
    
    if test_ggml_model():
        print("\n🎉 Your GGML model is working!")
        print("\n🚀 Next steps:")
        print("1. Run: python chat_enhanced.py --use-local --local-model llama2")
        print("2. Or setup via: python setup_ggml.py")
        print("3. Use automation: python automation_demo.py")
        print("\n💡 Your model can now be used for:")
        print("   • Code generation")
        print("   • Code fixing")
        print("   • Code optimization")
        print("   • Natural conversation")
    else:
        print("\n❌ GGML model test failed")
        print("\n🔧 To fix:")
        print("1. Install: pip install llama-cpp-python")
        print("2. Create models directory: mkdir models")
        print("3. Copy your llama-2-7b-chat.ggmlv3.q8_0.bin to models/")
        print("4. Run this test again")

if __name__ == "__main__":
    main()
