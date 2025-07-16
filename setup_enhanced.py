#!/usr/bin/env python3
"""
Enhanced Setup Script for DevO Chat
Handles GPU detection, memory management, and unified AI setup
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Tuple
import json

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
except ImportError:
    print("Installing rich for better output...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.table import Table

console = Console()

class EnhancedSetupManager:
    """Enhanced setup for DevO Chat with GPU and memory management"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.venv_path = self.base_dir / "venv"
        self.models_dir = self.base_dir / "models"
        self.config_file = self.base_dir / "enhanced_config.json"
        
    def run_setup(self):
        """Run complete enhanced setup"""
        console.print(Panel.fit(
            "🚀 [bold green]Enhanced DevO Chat Setup[/bold green]\n"
            "Setting up unified AI development assistant\n"
            "with GPU support and memory management",
            title="Setup Manager",
            border_style="green"
        ))
        
        try:
            # Step 1: System checks
            self._check_system_requirements()
            
            # Step 2: Create virtual environment
            self._setup_virtual_environment()
            
            # Step 3: Install dependencies
            self._install_dependencies()
            
            # Step 4: GPU setup
            self._setup_gpu_support()
            
            # Step 5: Model directories
            self._setup_model_directories()
            
            # Step 6: Configuration
            self._create_configuration()
            
            # Step 7: Test installation
            self._test_installation()
            
            # Step 8: Show usage instructions
            self._show_usage_instructions()
            
            console.print("\n🎉 [bold green]Setup completed successfully![/bold green]")
            
        except Exception as e:
            console.print(f"\n❌ [red]Setup failed: {e}[/red]")
            console.print("[yellow]Please check the error and try again.[/yellow]")
            sys.exit(1)
    
    def _check_system_requirements(self):
        """Check system requirements and compatibility"""
        console.print("\n[cyan]🔍 Checking system requirements...[/cyan]")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            raise Exception(f"Python 3.8+ required, got {python_version.major}.{python_version.minor}")
        
        console.print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check platform
        system = platform.system()
        arch = platform.machine()
        console.print(f"✅ Platform: {system} {arch}")
        
        # Check available memory
        try:
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            console.print(f"✅ RAM: {memory_gb:.1f} GB")
            
            if memory_gb < 4:
                console.print("[yellow]⚠️  Warning: Less than 4GB RAM. Local LLM may be slow.[/yellow]")
        except ImportError:
            console.print("[yellow]⚠️  Cannot check memory (psutil not installed)[/yellow]")
        
        # Check disk space
        free_space = self._get_free_space()
        if free_space < 5:
            console.print(f"[yellow]⚠️  Warning: Only {free_space:.1f}GB free space. Models need space.[/yellow]")
        else:
            console.print(f"✅ Free space: {free_space:.1f} GB")
    
    def _get_free_space(self) -> float:
        """Get free disk space in GB"""
        try:
            if platform.system() == "Windows":
                import shutil
                return shutil.disk_usage(self.base_dir)[2] / (1024**3)
            else:
                import os
                statvfs = os.statvfs(self.base_dir)
                return statvfs.f_frsize * statvfs.f_bavail / (1024**3)
        except:
            return 10.0  # Default assumption
    
    def _setup_virtual_environment(self):
        """Create and setup virtual environment"""
        console.print("\n[cyan]🐍 Setting up virtual environment...[/cyan]")
        
        if self.venv_path.exists():
            if Confirm.ask("Virtual environment exists. Recreate?", default=False):
                import shutil
                shutil.rmtree(self.venv_path)
            else:
                console.print("✅ Using existing virtual environment")
                return
        
        # Create virtual environment
        subprocess.check_call([
            sys.executable, "-m", "venv", str(self.venv_path)
        ])
        console.print("✅ Virtual environment created")
        
        # Get pip path
        if platform.system() == "Windows":
            pip_path = self.venv_path / "Scripts" / "pip.exe"
        else:
            pip_path = self.venv_path / "bin" / "pip"
        
        # Upgrade pip
        subprocess.check_call([str(pip_path), "install", "--upgrade", "pip"])
        console.print("✅ Pip upgraded")
    
    def _install_dependencies(self):
        """Install Python dependencies with progress"""
        console.print("\n[cyan]📦 Installing dependencies...[/cyan]")
        
        # Get pip path
        if platform.system() == "Windows":
            pip_path = self.venv_path / "Scripts" / "pip.exe"
        else:
            pip_path = self.venv_path / "bin" / "pip"
        
        requirements_file = self.base_dir / "requirements_unified.txt"
        
        if not requirements_file.exists():
            # Create minimal requirements if file doesn't exist
            minimal_deps = [
                "rich>=13.0.0",
                "click>=8.0.0", 
                "python-dotenv>=1.0.0",
                "requests>=2.28.0",
                "google-generativeai>=0.3.0"
            ]
            
            console.print("[yellow]Installing minimal dependencies...[/yellow]")
            for dep in minimal_deps:
                console.print(f"Installing {dep}...")
                subprocess.check_call([str(pip_path), "install", dep])
        else:
            console.print(f"Installing from {requirements_file}...")
            subprocess.check_call([
                str(pip_path), "install", "-r", str(requirements_file)
            ])
        
        console.print("✅ Dependencies installed")
    
    def _setup_gpu_support(self):
        """Setup GPU support if available"""
        console.print("\n[cyan]🚀 Checking GPU support...[/cyan]")
        
        # Get python path
        if platform.system() == "Windows":
            python_path = self.venv_path / "Scripts" / "python.exe"
        else:
            python_path = self.venv_path / "bin" / "python"
        
        try:
            # Check if torch is available and has CUDA
            result = subprocess.run([
                str(python_path), "-c", 
                "import torch; print(torch.cuda.is_available()); print(torch.cuda.device_count() if torch.cuda.is_available() else 0)"
            ], capture_output=True, text=True)
            
            lines = result.stdout.strip().split('\n')
            cuda_available = lines[0] == "True"
            gpu_count = int(lines[1]) if len(lines) > 1 else 0
            
            if cuda_available and gpu_count > 0:
                console.print(f"✅ CUDA GPU support available ({gpu_count} GPU(s))")
                
                # Ask if user wants to install GPU-optimized packages
                if Confirm.ask("Install GPU-optimized PyTorch?", default=True):
                    self._install_gpu_pytorch(python_path)
                    
            else:
                console.print("ℹ️  No CUDA GPU detected, using CPU")
                console.print("   For better performance, consider using a CUDA-capable GPU")
                
        except Exception as e:
            console.print(f"[yellow]⚠️  Could not check GPU: {e}[/yellow]")
            console.print("   Continuing with CPU support")
    
    def _install_gpu_pytorch(self, python_path: Path):
        """Install GPU-optimized PyTorch"""
        console.print("[cyan]Installing GPU-optimized PyTorch...[/cyan]")
        
        # Get pip path
        pip_path = python_path.parent / ("pip.exe" if platform.system() == "Windows" else "pip")
        
        try:
            # Install CUDA version of PyTorch
            subprocess.check_call([
                str(pip_path), "install", "torch", "torchvision", "torchaudio", 
                "--index-url", "https://download.pytorch.org/whl/cu118"
            ])
            console.print("✅ GPU PyTorch installed")
        except Exception as e:
            console.print(f"[yellow]⚠️  GPU PyTorch installation failed: {e}[/yellow]")
            console.print("   Continuing with CPU version")
    
    def _setup_model_directories(self):
        """Create model directories and setup"""
        console.print("\n[cyan]📁 Setting up model directories...[/cyan]")
        
        # Create models directory
        self.models_dir.mkdir(exist_ok=True)
        console.print(f"✅ Models directory: {self.models_dir}")
        
        # Create subdirectories for different model types
        (self.models_dir / "ggml").mkdir(exist_ok=True)
        (self.models_dir / "transformers").mkdir(exist_ok=True)
        (self.models_dir / "ollama").mkdir(exist_ok=True)
        
        # Check if user has any GGML models
        ggml_files = list(self.models_dir.glob("*.bin")) + list(self.models_dir.glob("*.gguf"))
        if ggml_files:
            console.print(f"✅ Found {len(ggml_files)} GGML model(s)")
        else:
            console.print("ℹ️  No GGML models found. You can add them to the models/ directory")
    
    def _create_configuration(self):
        """Create enhanced configuration file"""
        console.print("\n[cyan]⚙️  Creating configuration...[/cyan]")
        
        config = {
            "version": "2.0",
            "setup_date": str(Path(__file__).stat().st_mtime),
            "ai_providers": {
                "gemini": {
                    "enabled": True,
                    "api_key_env": "GEMINI_API_KEY",
                    "model": "gemini-2.0-flash-exp"
                },
                "local_llm": {
                    "enabled": True,
                    "preferred_provider": "ollama",
                    "fallback_provider": "transformers"
                }
            },
            "models": {
                "codellama": {
                    "ollama_name": "codellama:7b-instruct",
                    "transformers_name": "codellama/CodeLlama-7b-Instruct-hf",
                    "ggml_name": "codellama-7b-instruct.q4_0.gguf",
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
                    "ggml_name": "mistral-7b-instruct-v0.1.q4_0.gguf",
                    "description": "Efficient general purpose LLM"
                }
            },
            "memory_management": {
                "max_memory_usage": "auto",
                "enable_model_offloading": True,
                "cache_models": True
            },
            "gpu_settings": {
                "auto_detect": True,
                "device_map": "auto",
                "load_in_8bit": False,
                "load_in_4bit": False
            },
            "generation_params": {
                "temperature": 0.7,
                "max_tokens": 2048,
                "timeout": 300
            },
            "paths": {
                "models_dir": str(self.models_dir),
                "cache_dir": str(self.base_dir / "cache"),
                "logs_dir": str(self.base_dir / "logs")
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        console.print(f"✅ Configuration saved: {self.config_file}")
    
    def _test_installation(self):
        """Test the installation"""
        console.print("\n[cyan]🧪 Testing installation...[/cyan]")
        
        # Get python path
        if platform.system() == "Windows":
            python_path = self.venv_path / "Scripts" / "python.exe"
        else:
            python_path = self.venv_path / "bin" / "python"
        
        # Test basic imports
        test_script = '''
import sys
try:
    import rich
    print("✅ Rich imported")
except ImportError as e:
    print(f"❌ Rich import failed: {e}")
    sys.exit(1)

try:
    import click
    print("✅ Click imported")
except ImportError as e:
    print(f"❌ Click import failed: {e}")
    sys.exit(1)

try:
    import google.generativeai
    print("✅ Gemini API available")
except ImportError:
    print("⚠️  Gemini API not available (optional)")

try:
    import torch
    print(f"✅ PyTorch imported (CUDA: {torch.cuda.is_available()})")
except ImportError:
    print("⚠️  PyTorch not available (needed for local LLM)")

try:
    import transformers
    print("✅ Transformers imported")
except ImportError:
    print("⚠️  Transformers not available (needed for local LLM)")

print("🎉 Basic installation test passed!")
'''
        
        try:
            result = subprocess.run([str(python_path), "-c", test_script], 
                                  capture_output=True, text=True, check=True)
            console.print(result.stdout)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ Installation test failed:[/red]")
            console.print(e.stdout)
            console.print(e.stderr)
            raise Exception("Installation test failed")
    
    def _show_usage_instructions(self):
        """Show usage instructions"""
        console.print("\n" + "="*70)
        console.print(Panel.fit(
            "🎉 [bold green]Enhanced DevO Chat Setup Complete![/bold green]\n\n"
            "[bold cyan]How to run:[/bold cyan]\n"
            "• Windows: [white]launch_enhanced_chat.bat[/white]\n"
            "• Cross-platform: [white]python chat_enhanced.py[/white]\n\n"
            "[bold cyan]Command examples:[/bold cyan]\n"
            "• [white]launch_enhanced_chat.bat --local[/white] (use local AI)\n"
            "• [white]launch_enhanced_chat.bat --model mistral[/white] (specific model)\n"
            "• [white]python chat_enhanced.py --use-local --local-model codellama[/white]\n\n"
            "[bold cyan]Environment setup:[/bold cyan]\n"
            "• Set [white]GEMINI_API_KEY[/white] for cloud AI\n"
            "• Or create [white].env[/white] file with API key\n"
            "• Or use [white]--use-local[/white] for offline AI\n\n"
            "[bold cyan]GPU acceleration:[/bold cyan]\n"
            "• Install CUDA drivers for GPU support\n"
            "• Use [white]--use-local[/white] with GPU models\n"
            "• Configure memory settings in config file",
            title="🚀 Ready to Go!",
            border_style="green"
        ))


def main():
    """Main setup function"""
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        console.print("""
Enhanced DevO Chat Setup

Usage:
    python setup_enhanced.py          # Run complete setup
    python setup_enhanced.py --help   # Show this help

This will:
1. Check system requirements  
2. Create virtual environment
3. Install dependencies
4. Setup GPU support (if available)
5. Create model directories
6. Generate configuration
7. Test installation
8. Show usage instructions

Requirements:
- Python 3.8+
- 4GB+ RAM recommended
- 5GB+ free disk space
- Optional: CUDA GPU for acceleration
        """)
        return
    
    try:
        setup_manager = EnhancedSetupManager()
        setup_manager.run_setup()
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Setup failed: {e}[/red]")
        console.print("[yellow]Please check the error and try again[/yellow]")
        sys.exit(1)


if __name__ == "__main__":
    main()
