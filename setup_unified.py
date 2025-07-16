#!/usr/bin/env python3
"""
Enhanced Setup for DevO Unified Chat System
Handles GPU detection, memory optimization, and dependency management
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path
from typing import Dict, List, Optional
import importlib.util

class UnifiedSetup:
    """Setup manager for DevO Unified Chat System"""
    
    def __init__(self):
        self.system = platform.system()
        self.python_version = sys.version_info
        self.requirements = {
            'core': [
                'rich>=13.0.0',
                'click>=8.0.0',
                'google-generativeai>=0.7.0',
                'psutil>=5.9.0',
                'python-dotenv>=1.0.0',
                'requests>=2.31.0'
            ],
            'local_llm': [
                'torch>=2.0.0',
                'transformers>=4.30.0',
                'accelerate>=0.20.0'
            ],
            'optional': [
                'ollama-python>=0.1.0',
                'llama-cpp-python>=0.2.0'
            ]
        }
        
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("🐍 Checking Python version...")
        
        if self.python_version < (3, 8):
            print("❌ Python 3.8+ required")
            print(f"   Current version: {sys.version}")
            return False
        
        print(f"✅ Python {sys.version.split()[0]} is compatible")
        return True
    
    def check_gpu_availability(self):
        """Check for GPU availability and CUDA support"""
        print("\n🚀 Checking GPU availability...")
        
        gpu_info = {
            'cuda_available': False,
            'gpu_count': 0,
            'gpu_names': [],
            'cuda_version': None,
            'recommended_install': None
        }
        
        try:
            # Check if NVIDIA GPU is available
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ NVIDIA GPU detected")
                
                # Try to get CUDA version
                try:
                    result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'release' in line:
                                cuda_version = line.split('release ')[1].split(',')[0]
                                gpu_info['cuda_version'] = cuda_version
                                print(f"✅ CUDA {cuda_version} detected")
                                break
                except FileNotFoundError:
                    print("⚠️  CUDA toolkit not found in PATH")
                
                # Recommend PyTorch installation based on CUDA version
                if gpu_info['cuda_version']:
                    if gpu_info['cuda_version'].startswith('12'):
                        gpu_info['recommended_install'] = 'cu121'
                    elif gpu_info['cuda_version'].startswith('11'):
                        gpu_info['recommended_install'] = 'cu118'
                    else:
                        gpu_info['recommended_install'] = 'cu118'  # Default
                else:
                    gpu_info['recommended_install'] = 'cu121'  # Latest
                
                gpu_info['cuda_available'] = True
                
        except FileNotFoundError:
            print("ℹ️  No NVIDIA GPU detected or nvidia-smi not available")
        
        # Check for other GPUs (AMD, Intel)
        try:
            if self.system == "Windows":
                result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    gpu_names = [line.strip() for line in lines if line.strip()]
                    gpu_info['gpu_names'] = gpu_names
                    gpu_info['gpu_count'] = len(gpu_names)
                    
                    for gpu in gpu_names:
                        if gpu:
                            print(f"🎮 Detected GPU: {gpu}")
        except:
            pass
        
        if not gpu_info['cuda_available']:
            print("💻 Will use CPU-only mode")
            gpu_info['recommended_install'] = 'cpu'
        
        return gpu_info
    
    def create_virtual_environment(self):
        """Create virtual environment if it doesn't exist"""
        venv_path = Path("venv")
        
        if venv_path.exists():
            print("✅ Virtual environment already exists")
            return True
        
        print("📦 Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✅ Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def get_pip_command(self):
        """Get the correct pip command for the platform"""
        if self.system == "Windows":
            return "venv\\Scripts\\pip.exe"
        else:
            return "venv/bin/pip"
    
    def install_dependencies(self, gpu_info: Dict):
        """Install required dependencies"""
        pip_cmd = self.get_pip_command()
        
        print("\n📦 Installing core dependencies...")
        
        # Upgrade pip first
        try:
            subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        except subprocess.CalledProcessError:
            print("⚠️  Failed to upgrade pip, continuing...")
        
        # Install core dependencies
        core_deps = ' '.join(self.requirements['core'])
        try:
            subprocess.run(f"{pip_cmd} install {core_deps}", shell=True, check=True)
            print("✅ Core dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install core dependencies: {e}")
            return False
        
        # Install PyTorch based on GPU availability
        print("\n🔥 Installing PyTorch...")
        
        if gpu_info['cuda_available']:
            torch_cmd = f"{pip_cmd} install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/{gpu_info['recommended_install']}"
            print(f"   Installing CUDA-enabled PyTorch ({gpu_info['recommended_install']})...")
        else:
            torch_cmd = f"{pip_cmd} install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
            print("   Installing CPU-only PyTorch...")
        
        try:
            subprocess.run(torch_cmd, shell=True, check=True)
            print("✅ PyTorch installed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  PyTorch installation failed: {e}")
            print("   Will continue with CPU-only mode")
        
        # Install transformers and related
        print("\n🤖 Installing transformers and LLM dependencies...")
        llm_deps = ' '.join(self.requirements['local_llm'])
        try:
            subprocess.run(f"{pip_cmd} install {llm_deps}", shell=True, check=True)
            print("✅ LLM dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Some LLM dependencies failed: {e}")
        
        # Install optional dependencies
        print("\n🔧 Installing optional dependencies...")
        for dep in self.requirements['optional']:
            try:
                subprocess.run(f"{pip_cmd} install {dep}", shell=True, check=True)
                print(f"✅ {dep} installed")
            except subprocess.CalledProcessError:
                print(f"⚠️  {dep} installation failed (optional)")
        
        return True
    
    def test_installation(self):
        """Test if the installation is working"""
        print("\n🧪 Testing installation...")
        
        # Test core imports
        test_imports = [
            ('rich', 'Rich library'),
            ('click', 'Click library'),
            ('google.generativeai', 'Google Generative AI'),
            ('psutil', 'PSUtil'),
            ('requests', 'Requests')
        ]
        
        for module, name in test_imports:
            try:
                importlib.import_module(module)
                print(f"✅ {name} working")
            except ImportError:
                print(f"❌ {name} failed")
        
        # Test PyTorch and GPU
        try:
            import torch
            print(f"✅ PyTorch {torch.__version__} working")
            
            if torch.cuda.is_available():
                device_name = torch.cuda.get_device_name(0)
                print(f"🚀 CUDA available: {device_name}")
            else:
                print("💻 CUDA not available, using CPU")
                
        except ImportError:
            print("❌ PyTorch not available")
        
        # Test transformers
        try:
            import transformers
            print(f"✅ Transformers {transformers.__version__} working")
        except ImportError:
            print("⚠️  Transformers not available")
    
    def create_config_files(self):
        """Create default configuration files"""
        print("\n⚙️  Creating configuration files...")
        
        # Create .env template if it doesn't exist
        env_file = Path(".env")
        if not env_file.exists():
            env_content = """# DevO Unified Chat Configuration
# Get your Gemini API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_api_key_here

# Memory management (optional)
MAX_MEMORY_GB=8.0
ENABLE_GPU=true
AUTO_CLEANUP=true

# Local LLM settings (optional)
PREFERRED_PROVIDER=auto
DEFAULT_MODEL=codellama
"""
            with open(env_file, 'w') as f:
                f.write(env_content)
            print("✅ Created .env template")
        
        # Create local LLM config
        config = {
            "preferred_provider": "ollama",
            "models": {
                "codellama": {
                    "ollama_name": "codellama:7b-instruct",
                    "transformers_name": "codellama/CodeLlama-7b-Instruct-hf",
                    "description": "Code-focused LLM for programming tasks"
                },
                "llama2": {
                    "ollama_name": "llama2:7b-chat",
                    "transformers_name": "meta-llama/Llama-2-7b-chat-hf",
                    "ggml_name": "llama-2-7b-chat.ggmlv3.q8_0.bin",
                    "description": "General purpose conversational LLM"
                },
                "mistral": {
                    "ollama_name": "mistral:7b-instruct",
                    "transformers_name": "mistralai/Mistral-7B-Instruct-v0.1",
                    "description": "Efficient general purpose LLM"
                }
            },
            "generation_params": {
                "temperature": 0.7,
                "max_tokens": 512,
                "timeout": 300
            }
        }
        
        config_file = Path("local_llm_config.json")
        if not config_file.exists():
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Created local_llm_config.json")
        
        # Create models directory
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        print("✅ Created models directory")
    
    def create_launcher_scripts(self):
        """Create launcher scripts for different platforms"""
        print("\n🚀 Creating launcher scripts...")
        
        if self.system == "Windows":
            # Windows batch file already created
            print("✅ Windows launcher (launch_unified_chat.bat) ready")
        
        # Create cross-platform Python launcher
        launcher_content = '''#!/usr/bin/env python3
"""
DevO Unified Chat Launcher
Cross-platform launcher with automatic setup
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Launch DevO Unified Chat with proper environment"""
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # Not in virtual environment, try to activate it
        if Path("venv").exists():
            if sys.platform == "win32":
                venv_python = "venv\\\\Scripts\\\\python.exe"
            else:
                venv_python = "venv/bin/python"
            
            if Path(venv_python).exists():
                print("🔄 Activating virtual environment...")
                os.execv(venv_python, [venv_python] + sys.argv)
        
        print("⚠️  Virtual environment not found. Please run setup first.")
        sys.exit(1)
    
    # Import and run unified chat
    try:
        from unified_chat import main as chat_main
        chat_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Please run setup again or check dependencies")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        with open("launch_chat.py", 'w') as f:
            f.write(launcher_content)
        print("✅ Created launch_chat.py")
        
        # Make executable on Unix systems
        if self.system != "Windows":
            os.chmod("launch_chat.py", 0o755)
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🎯 DevO Unified Chat Setup")
        print("=" * 40)
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Check GPU availability
        gpu_info = self.check_gpu_availability()
        
        # Create virtual environment
        if not self.create_virtual_environment():
            return False
        
        # Install dependencies
        if not self.install_dependencies(gpu_info):
            return False
        
        # Test installation
        self.test_installation()
        
        # Create config files
        self.create_config_files()
        
        # Create launcher scripts
        self.create_launcher_scripts()
        
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Edit .env file and add your Gemini API key")
        print("2. Run: launch_unified_chat.bat (Windows) or python launch_chat.py")
        print("3. Use 'setup model' command to configure local LLM")
        print("\n💡 Tips:")
        print("- Use 'help' command for all available features")
        print("- Switch between Gemini and local LLM with 'switch provider'")
        print("- Monitor memory usage with 'memory status'")
        
        return True

if __name__ == "__main__":
    setup = UnifiedSetup()
    try:
        success = setup.run_setup()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
