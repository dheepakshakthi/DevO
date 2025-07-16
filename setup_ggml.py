#!/usr/bin/env python3
"""
GGML Model Setup Script
Helps set up and test local GGML models like llama-2-7b-chat.ggmlv3.q8_0.bin
"""

import os
import sys
import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

def find_ggml_models():
    """Find GGML model files on the system"""
    common_locations = [
        Path.home() / "Downloads",
        Path.cwd(),
        Path("C:/models") if sys.platform == "win32" else Path("/models"),
        Path.home() / "models",
        Path("models")
    ]
    
    found_models = []
    extensions = ['.bin', '.gguf', '.ggml']
    
    for location in common_locations:
        if location.exists():
            for ext in extensions:
                for model_file in location.rglob(f'*{ext}'):
                    if model_file.is_file():
                        found_models.append(model_file)
    
    return found_models

def install_llamacpp():
    """Install llama-cpp-python"""
    try:
        import subprocess
        console.print("[cyan]📦 Installing llama-cpp-python...[/cyan]")
        
        # Check if we want CPU or GPU version
        if Confirm.ask("Do you have an NVIDIA GPU and want GPU acceleration?"):
            console.print("[cyan]Installing with CUDA support...[/cyan]")
            # For CUDA support
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "llama-cpp-python[cuda]", "--force-reinstall", "--no-cache-dir"
            ], capture_output=True, text=True)
        else:
            console.print("[cyan]Installing CPU-only version...[/cyan]")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "llama-cpp-python", "--force-reinstall", "--no-cache-dir"
            ], capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("[green]✅ llama-cpp-python installed successfully![/green]")
            return True
        else:
            console.print(f"[red]❌ Installation failed: {result.stderr}[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Error installing llama-cpp-python: {e}[/red]")
        return False

def setup_model_directory():
    """Set up the models directory and copy GGML models"""
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    console.print(f"[cyan]📁 Models directory: {models_dir.resolve()}[/cyan]")
    
    # Find existing GGML models
    found_models = find_ggml_models()
    
    if found_models:
        console.print(f"\n[green]Found {len(found_models)} GGML model(s):[/green]")
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Index", style="cyan")
        table.add_column("Model Name", style="white")
        table.add_column("Location", style="dim")
        table.add_column("Size (MB)", style="yellow")
        
        for i, model_path in enumerate(found_models, 1):
            size_mb = round(model_path.stat().st_size / (1024 * 1024), 2)
            table.add_row(str(i), model_path.name, str(model_path.parent), str(size_mb))
        
        console.print(table)
        
        # Ask user which models to copy
        while True:
            choice = Prompt.ask(
                "\nEnter model index to copy to models directory (or 'all' for all, 'skip' to skip)",
                default="all"
            )
            
            if choice.lower() == "skip":
                break
            elif choice.lower() == "all":
                for model_path in found_models:
                    copy_model_to_directory(model_path, models_dir)
                break
            else:
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(found_models):
                        copy_model_to_directory(found_models[index], models_dir)
                        
                        if Confirm.ask("Copy another model?"):
                            continue
                        else:
                            break
                    else:
                        console.print("[red]Invalid index. Please try again.[/red]")
                except ValueError:
                    console.print("[red]Please enter a valid number or 'all'.[/red]")
    else:
        console.print("[yellow]⚠️  No GGML models found automatically.[/yellow]")
        console.print("[cyan]You can manually copy your model files to the models directory.[/cyan]")
        console.print(f"[cyan]Models directory: {models_dir.resolve()}[/cyan]")
        
        if Confirm.ask("Do you want to specify a model file path manually?"):
            model_path = Prompt.ask("Enter the full path to your GGML model file")
            model_file = Path(model_path)
            if model_file.exists():
                copy_model_to_directory(model_file, models_dir)
            else:
                console.print(f"[red]❌ File not found: {model_path}[/red]")

def copy_model_to_directory(model_path: Path, models_dir: Path):
    """Copy a model file to the models directory"""
    destination = models_dir / model_path.name
    
    if destination.exists():
        console.print(f"[yellow]⚠️  {model_path.name} already exists in models directory[/yellow]")
        if not Confirm.ask("Overwrite?"):
            return
    
    try:
        console.print(f"[cyan]📋 Copying {model_path.name} to models directory...[/cyan]")
        shutil.copy2(model_path, destination)
        console.print(f"[green]✅ Copied {model_path.name}[/green]")
    except Exception as e:
        console.print(f"[red]❌ Error copying {model_path.name}: {e}[/red]")

def test_ggml_model():
    """Test a GGML model"""
    try:
        # Import our local LLM manager
        from local_llm import LocalLLMManager
        
        llm = LocalLLMManager()
        
        # List available GGML models
        available_models = llm.llamacpp.list_local_models()
        
        if not available_models:
            console.print("[red]❌ No GGML models found in models directory[/red]")
            return False
        
        console.print(f"\n[green]Available GGML models:[/green]")
        for i, model in enumerate(available_models, 1):
            console.print(f"{i}. {model}")
        
        # Let user choose a model to test
        if len(available_models) == 1:
            chosen_model = available_models[0]
            console.print(f"[cyan]Testing model: {chosen_model}[/cyan]")
        else:
            while True:
                try:
                    choice = int(Prompt.ask("Choose model to test", default="1")) - 1
                    if 0 <= choice < len(available_models):
                        chosen_model = available_models[choice]
                        break
                    else:
                        console.print("[red]Invalid choice. Please try again.[/red]")
                except ValueError:
                    console.print("[red]Please enter a valid number.[/red]")
        
        # Setup the model
        console.print(f"[cyan]🚀 Setting up {chosen_model}...[/cyan]")
        if llm.llamacpp.load_model(chosen_model):
            # Test generation
            test_prompt = "Hello! Can you help me write a Python function?"
            console.print(f"\n[yellow]Test prompt: {test_prompt}[/yellow]")
            
            try:
                response = llm.llamacpp.generate(test_prompt, max_tokens=100)
                console.print(Panel(response, title="Generated Response", border_style="green"))
                
                # Show model info
                model_info = llm.llamacpp.get_model_info()
                console.print(Panel(
                    f"Model: {model_info.get('name', 'Unknown')}\n"
                    f"Size: {model_info.get('size_mb', 0):.2f} MB\n"
                    f"Type: {model_info.get('type', 'Unknown')}",
                    title="Model Information",
                    border_style="blue"
                ))
                
                console.print("[green]🎉 GGML model test successful![/green]")
                return True
                
            except Exception as e:
                console.print(f"[red]❌ Generation test failed: {e}[/red]")
                return False
        else:
            console.print("[red]❌ Failed to load GGML model[/red]")
            return False
            
    except ImportError as e:
        console.print(f"[red]❌ Import error: {e}[/red]")
        console.print("[yellow]Make sure you're in the correct directory with local_llm.py[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Error testing GGML model: {e}[/red]")
        return False

def main():
    """Main setup function"""
    console.print(Panel.fit(
        "[bold green]GGML Model Setup for DevO Chat[/bold green]\n"
        "This script will help you set up your local GGML models.\n\n"
        "[cyan]Your model: llama-2-7b-chat.ggmlv3.q8_0.bin[/cyan]\n\n"
        "[yellow]What this script does:[/yellow]\n"
        "• Install llama-cpp-python for GGML support\n"
        "• Find and organize your GGML models\n"
        "• Test model loading and generation\n"
        "• Configure DevO Chat to use your models\n\n"
        "[green]Benefits of GGML models:[/green]\n"
        "• Faster loading than full PyTorch models\n"
        "• Lower memory usage\n"
        "• CPU optimized (with optional GPU acceleration)\n"
        "• No network required after setup",
        title="🤖 GGML Model Setup",
        border_style="green"
    ))
    
    if not Confirm.ask("Continue with GGML model setup?"):
        console.print("[yellow]Setup cancelled.[/yellow]")
        return
    
    # Step 1: Check/Install llama-cpp-python
    console.print("\n[bold cyan]Step 1: Installing llama-cpp-python[/bold cyan]")
    try:
        import llama_cpp
        console.print("[green]✅ llama-cpp-python is already installed[/green]")
    except ImportError:
        if not install_llamacpp():
            console.print("[red]❌ Failed to install llama-cpp-python[/red]")
            return
    
    # Step 2: Set up models directory
    console.print("\n[bold cyan]Step 2: Setting up models directory[/bold cyan]")
    setup_model_directory()
    
    # Step 3: Test GGML model
    console.print("\n[bold cyan]Step 3: Testing GGML model[/bold cyan]")
    if test_ggml_model():
        console.print("\n[green]🎉 GGML setup completed successfully![/green]")
        console.print("\n[cyan]To use your GGML model with DevO Chat:[/cyan]")
        console.print("[white]python chat_enhanced.py --use-local --local-model llama2[/white]")
        console.print("\n[cyan]Or specify GGML provider explicitly:[/cyan]")
        console.print("[white]# In Python:[/white]")
        console.print("[white]llm = LocalLLMManager()[/white]")
        console.print("[white]llm.setup_model('llama2', 'ggml')[/white]")
    else:
        console.print("\n[yellow]⚠️  Setup completed with some issues.[/yellow]")
        console.print("[yellow]You can still try using the GGML model manually.[/yellow]")

if __name__ == "__main__":
    main()
