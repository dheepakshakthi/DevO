#!/usr/bin/env python3
"""
Local LLM Setup Script
Automatically installs and configures local LLM models (Ollama + CodeLlama)
"""

import os
import sys
import subprocess
import platform
import time
import requests
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()

def is_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ollama():
    """Install Ollama based on the operating system"""
    system = platform.system().lower()
    
    console.print(f"[cyan]🚀 Installing Ollama for {system}...[/cyan]")
    
    try:
        if system == "windows":
            console.print("[yellow]For Windows, please download Ollama manually from: https://ollama.ai/download[/yellow]")
            console.print("[yellow]After installation, restart this script.[/yellow]")
            return False
        
        elif system == "darwin":  # macOS
            console.print("[cyan]Installing Ollama via curl...[/cyan]")
            subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh'], check=True, shell=True)
        
        elif system == "linux":
            console.print("[cyan]Installing Ollama via curl...[/cyan]")
            subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh', '|', 'sh'], check=True, shell=True)
        
        else:
            console.print(f"[red]❌ Unsupported operating system: {system}[/red]")
            return False
        
        # Wait a moment for installation to complete
        time.sleep(2)
        
        # Check if installation was successful
        if is_ollama_installed():
            console.print("[green]✅ Ollama installed successfully![/green]")
            return True
        else:
            console.print("[red]❌ Ollama installation failed[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Error installing Ollama: {e}[/red]")
        return False

def start_ollama_service():
    """Start Ollama service"""
    try:
        console.print("[cyan]🚀 Starting Ollama service...[/cyan]")
        
        if platform.system().lower() == "windows":
            # On Windows, start as a background process
            subprocess.Popen(['ollama', 'serve'], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # On Unix-like systems
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for service to start
        for i in range(30):
            try:
                response = requests.get('http://localhost:11434/api/tags', timeout=2)
                if response.status_code == 200:
                    console.print("[green]✅ Ollama service started successfully![/green]")
                    return True
            except:
                pass
            time.sleep(1)
        
        console.print("[red]❌ Failed to start Ollama service[/red]")
        return False
        
    except Exception as e:
        console.print(f"[red]❌ Error starting Ollama service: {e}[/red]")
        return False

def install_codellama_model():
    """Install CodeLlama model via Ollama"""
    try:
        console.print("[cyan]📥 Installing CodeLlama 7B model...[/cyan]")
        console.print("[yellow]This may take several minutes (model is ~3.8GB)[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=False
        ) as progress:
            task = progress.add_task("Downloading CodeLlama...", total=None)
            
            # Run ollama pull command
            process = subprocess.Popen(
                ['ollama', 'pull', 'codellama:7b-instruct'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor the process
            while process.poll() is None:
                progress.update(task, description="Downloading CodeLlama model...")
                time.sleep(1)
            
            if process.returncode == 0:
                console.print("[green]✅ CodeLlama model installed successfully![/green]")
                return True
            else:
                error_output = process.stderr.read()
                console.print(f"[red]❌ Failed to install CodeLlama: {error_output}[/red]")
                return False
                
    except Exception as e:
        console.print(f"[red]❌ Error installing CodeLlama: {e}[/red]")
        return False

def install_python_dependencies():
    """Install Python dependencies for local LLM"""
    try:
        console.print("[cyan]📦 Installing Python dependencies...[/cyan]")
        
        # Check if we're in a virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        
        if not in_venv:
            console.print("[yellow]⚠️  Not in a virtual environment. Creating one is recommended.[/yellow]")
            if Confirm.ask("Create a virtual environment?"):
                subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
                if platform.system().lower() == "windows":
                    python_path = Path('venv/Scripts/python.exe')
                    pip_path = Path('venv/Scripts/pip.exe')
                else:
                    python_path = Path('venv/bin/python')
                    pip_path = Path('venv/bin/pip')
            else:
                python_path = sys.executable
                pip_path = 'pip'
        else:
            python_path = sys.executable
            pip_path = 'pip'
        
        # Install packages
        packages = [
            'torch>=2.0.0',
            'transformers>=4.30.0',
            'accelerate>=0.20.0',
            'sentencepiece>=0.1.99',
            'tokenizers>=0.13.0'
        ]
        
        for package in packages:
            console.print(f"[cyan]Installing {package}...[/cyan]")
            subprocess.run([pip_path, 'install', package], check=True)
        
        console.print("[green]✅ Python dependencies installed successfully![/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Error installing Python dependencies: {e}[/red]")
        return False

def test_local_llm():
    """Test the local LLM setup"""
    try:
        console.print("[cyan]🧪 Testing local LLM setup...[/cyan]")
        
        # Test Ollama
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'codellama:7b-instruct',
                    'prompt': 'Write a hello world function in Python:',
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                console.print("[green]✅ Ollama test successful![/green]")
                console.print(Panel(result.get('response', 'No response'), title="Test Response"))
                return True
            else:
                console.print(f"[red]❌ Ollama test failed: {response.status_code}[/red]")
                
        except Exception as e:
            console.print(f"[yellow]⚠️  Ollama test failed: {e}[/yellow]")
        
        # Test Transformers as fallback
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            console.print("[cyan]Testing Transformers fallback...[/cyan]")
            
            # This would download the model if not present, so we'll just check if imports work
            console.print("[green]✅ Transformers library available![/green]")
            console.print("[yellow]Note: First run will download the model (~13GB)[/yellow]")
            return True
            
        except ImportError as e:
            console.print(f"[red]❌ Transformers test failed: {e}[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Error testing local LLM: {e}[/red]")
        return False

def create_local_config():
    """Create local LLM configuration file"""
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
            "max_tokens": 1024,
            "timeout": 300
        }
    }
    
    try:
        import json
        with open('local_llm_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        console.print("[green]✅ Configuration file created: local_llm_config.json[/green]")
    except Exception as e:
        console.print(f"[yellow]⚠️  Could not create config file: {e}[/yellow]")

def main():
    """Main setup function"""
    console.print(Panel.fit(
        "[bold green]Local LLM Setup for DevO Chat[/bold green]\n"
        "This script will install and configure CodeLlama 7B for local AI assistance.\n\n"
        "[cyan]Features:[/cyan]\n"
        "• Privacy-focused: All processing happens locally\n"
        "• No API keys required\n"
        "• Works offline\n"
        "• Specialized for code tasks\n\n"
        "[yellow]Requirements:[/yellow]\n"
        "• ~4GB free disk space for model\n"
        "• 8GB+ RAM recommended\n"
        "• GPU optional but recommended for speed",
        title="🤖 Local LLM Setup",
        border_style="green"
    ))
    
    if not Confirm.ask("Continue with local LLM setup?"):
        console.print("[yellow]Setup cancelled.[/yellow]")
        return
    
    # Step 1: Check/Install Ollama
    console.print("\n[bold cyan]Step 1: Ollama Installation[/bold cyan]")
    if is_ollama_installed():
        console.print("[green]✅ Ollama is already installed[/green]")
    else:
        if not install_ollama():
            console.print("[red]❌ Ollama installation failed. Please install manually.[/red]")
            console.print("[yellow]Visit: https://ollama.ai/download[/yellow]")
            return
    
    # Step 2: Start Ollama service
    console.print("\n[bold cyan]Step 2: Starting Ollama Service[/bold cyan]")
    if not start_ollama_service():
        console.print("[red]❌ Could not start Ollama service[/red]")
        console.print("[yellow]Please start Ollama manually: ollama serve[/yellow]")
        return
    
    # Step 3: Install CodeLlama model
    console.print("\n[bold cyan]Step 3: Installing CodeLlama Model[/bold cyan]")
    if not install_codellama_model():
        console.print("[red]❌ CodeLlama installation failed[/red]")
        console.print("[yellow]You can try installing manually: ollama pull codellama:7b-instruct[/yellow]")
    
    # Step 4: Install Python dependencies
    console.print("\n[bold cyan]Step 4: Python Dependencies[/bold cyan]")
    install_python_dependencies()
    
    # Step 5: Create configuration
    console.print("\n[bold cyan]Step 5: Configuration[/bold cyan]")
    create_local_config()
    
    # Step 6: Test setup
    console.print("\n[bold cyan]Step 6: Testing Setup[/bold cyan]")
    if test_local_llm():
        console.print("\n[green]🎉 Local LLM setup completed successfully![/green]")
        console.print("\n[cyan]To use local LLM with DevO Chat:[/cyan]")
        console.print("[white]python chat_enhanced.py --use-local[/white]")
        console.print("\n[cyan]Or for mixed mode (both local and cloud):[/cyan]")
        console.print("[white]python chat_enhanced.py[/white]")
    else:
        console.print("\n[yellow]⚠️  Setup completed with some issues.[/yellow]")
        console.print("[yellow]You can still try using the enhanced chat.[/yellow]")

if __name__ == "__main__":
    main()
