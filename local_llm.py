#!/usr/bin/env python3
"""
Local LLM Integration Module
Supports CodeLlama 7B and other local models via Ollama/Transformers
Handles timeout prevention and efficient model management
"""

import os
import sys
import json
import asyncio
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import requests
import subprocess
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

console = Console()

@dataclass
class ModelConfig:
    """Configuration for local LLM models"""
    name: str
    type: str  # 'ollama', 'transformers', 'llamacpp'
    model_path: str
    context_length: int = 4096
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 300  # 5 minutes
    
class OllamaManager:
    """Manages Ollama local LLM integration"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 300  # 5 minute timeout
        
    def is_running(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_ollama(self) -> bool:
        """Start Ollama service if not running"""
        if self.is_running():
            return True
            
        try:
            console.print("[yellow]🚀 Starting Ollama service...[/yellow]")
            
            # Try to start Ollama
            if sys.platform == "win32":
                subprocess.Popen(["ollama", "serve"], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for service to start
            for _ in range(30):  # Wait up to 30 seconds
                if self.is_running():
                    console.print("[green]✅ Ollama service started successfully[/green]")
                    return True
                time.sleep(1)
                
            console.print("[red]❌ Failed to start Ollama service[/red]")
            return False
            
        except Exception as e:
            console.print(f"[red]❌ Error starting Ollama: {e}[/red]")
            return False
    
    def list_models(self) -> List[str]:
        """List available models in Ollama"""
        try:
            if not self.is_running():
                return []
                
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            console.print(f"[yellow]Warning: Could not list models: {e}[/yellow]")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull/download a model to Ollama"""
        try:
            console.print(f"[cyan]📥 Downloading model: {model_name}[/cyan]")
            console.print("[yellow]This may take several minutes for large models...[/yellow]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=False
            ) as progress:
                task = progress.add_task(f"Downloading {model_name}...", total=None)
                
                response = self.session.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model_name},
                    stream=True,
                    timeout=1800  # 30 minute timeout for model download
                )
                
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                status = data.get('status', '')
                                if 'progress' in data:
                                    progress.update(task, description=f"Downloading {model_name}: {status}")
                                elif 'success' in data and data['success']:
                                    progress.update(task, description=f"✅ {model_name} downloaded successfully")
                                    break
                            except json.JSONDecodeError:
                                continue
                    
                    console.print(f"[green]✅ Model {model_name} downloaded successfully[/green]")
                    return True
                else:
                    console.print(f"[red]❌ Failed to download model: {response.status_code}[/red]")
                    return False
                    
        except Exception as e:
            console.print(f"[red]❌ Error downloading model: {e}[/red]")
            return False
    
    def generate(self, model: str, prompt: str, **kwargs) -> str:
        """Generate text using Ollama model with timeout handling"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "num_predict": kwargs.get("max_tokens", 2048),
                    "top_p": kwargs.get("top_p", 0.9),
                    "repeat_penalty": kwargs.get("repeat_penalty", 1.1),
                }
            }
            
            # Set longer timeout for generation
            timeout = kwargs.get("timeout", 300)
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            raise Exception("Model generation timed out. Try reducing input length or increasing timeout.")
        except Exception as e:
            raise Exception(f"Error generating response: {e}")

class TransformersManager:
    """Manages local models via Transformers library"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        
    def load_model(self, model_name: str = "codellama/CodeLlama-7b-Instruct-hf") -> bool:
        """Load CodeLlama or other Transformers model"""
        try:
            console.print(f"[cyan]🤖 Loading model: {model_name}[/cyan]")
            console.print("[yellow]This may take a few minutes on first load...[/yellow]")
            
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            # Determine device
            if torch.cuda.is_available():
                self.device = "cuda"
                console.print("[green]🚀 Using GPU acceleration[/green]")
            else:
                self.device = "cpu"
                console.print("[yellow]⚠️  Using CPU (slower but works)[/yellow]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("Loading tokenizer...", total=1)
                
                # Load tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                progress.update(task, completed=1)
                
                # Load model
                task2 = progress.add_task("Loading model...", total=1)
                
                if self.device == "cuda":
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_name,
                        torch_dtype=torch.float16,
                        device_map="auto",
                        trust_remote_code=True
                    )
                else:
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_name,
                        torch_dtype=torch.float32,
                        trust_remote_code=True
                    )
                    self.model.to(self.device)
                
                progress.update(task2, completed=1)
            
            console.print(f"[green]✅ Model {model_name} loaded successfully[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error loading model: {e}[/red]")
            console.print("[yellow]💡 Try: pip install torch transformers accelerate[/yellow]")
            return False
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using loaded model"""
        if not self.model or not self.tokenizer:
            raise Exception("Model not loaded. Call load_model() first.")
        
        try:
            import torch
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=kwargs.get("max_tokens", 512),
                    temperature=kwargs.get("temperature", 0.7),
                    do_sample=True,
                    top_p=kwargs.get("top_p", 0.9),
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the input prompt from response
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            raise Exception(f"Error generating response: {e}")

class LlamaCppManager:
    """Manages local GGML models via llama-cpp-python"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.model = None
        self.current_model_path = None
        
    def list_local_models(self) -> List[str]:
        """List available GGML models in the models directory"""
        model_files = []
        for ext in ['.bin', '.gguf', '.ggml']:
            model_files.extend(self.models_dir.glob(f'*{ext}'))
        return [f.name for f in model_files]
    
    def load_model(self, model_path: str, **kwargs) -> bool:
        """Load a GGML model from file"""
        try:
            from llama_cpp import Llama
        except ImportError:
            console.print("[red]❌ llama-cpp-python not installed![/red]")
            console.print("[yellow]💡 Install with: pip install llama-cpp-python[/yellow]")
            return False
        
        try:
            # Handle both absolute and relative paths
            if not Path(model_path).is_absolute():
                model_path = self.models_dir / model_path
            
            if not Path(model_path).exists():
                console.print(f"[red]❌ Model file not found: {model_path}[/red]")
                return False
            
            console.print(f"[cyan]🤖 Loading GGML model: {model_path}[/cyan]")
            console.print("[yellow]This may take a moment...[/yellow]")
            
            # Default parameters for GGML models
            model_params = {
                'model_path': str(model_path),
                'n_ctx': kwargs.get('n_ctx', 4096),  # Context length
                'n_threads': kwargs.get('n_threads', os.cpu_count()),  # Use all CPU cores
                'n_gpu_layers': kwargs.get('n_gpu_layers', 0),  # GPU layers (0 for CPU only)
                'verbose': False
            }
            
            # Load the model
            self.model = Llama(**model_params)
            self.current_model_path = str(model_path)
            
            console.print(f"[green]✅ GGML model loaded successfully![/green]")
            console.print(f"[dim]Model: {Path(model_path).name}[/dim]")
            console.print(f"[dim]Context length: {model_params['n_ctx']}[/dim]")
            console.print(f"[dim]Threads: {model_params['n_threads']}[/dim]")
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Error loading GGML model: {e}[/red]")
            console.print("[yellow]💡 Make sure the model file is a valid GGML/GGUF format[/yellow]")
            return False
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using the loaded GGML model"""
        if not self.model:
            raise Exception("No GGML model loaded. Call load_model() first.")
        
        try:
            # Generation parameters
            gen_params = {
                'max_tokens': kwargs.get('max_tokens', 512),
                'temperature': kwargs.get('temperature', 0.7),
                'top_p': kwargs.get('top_p', 0.9),
                'top_k': kwargs.get('top_k', 40),
                'repeat_penalty': kwargs.get('repeat_penalty', 1.1),
                'stop': kwargs.get('stop', []),
                'echo': False  # Don't echo the prompt
            }
            
            # Generate response
            response = self.model(prompt, **gen_params)
            
            # Extract the generated text
            generated_text = response['choices'][0]['text']
            
            return generated_text.strip()
            
        except Exception as e:
            raise Exception(f"Error generating response with GGML model: {e}")
    
    def get_model_info(self) -> Dict:
        """Get information about the currently loaded model"""
        if not self.model or not self.current_model_path:
            return {}
        
        model_path = Path(self.current_model_path)
        return {
            'name': model_path.name,
            'path': str(model_path),
            'size_mb': round(model_path.stat().st_size / (1024 * 1024), 2),
            'type': 'GGML/GGUF'
        }

class LocalLLMManager:
    """Unified manager for local LLM models"""
    
    def __init__(self):
        self.ollama = OllamaManager()
        self.transformers = TransformersManager()
        self.llamacpp = LlamaCppManager()
        self.current_provider = None
        self.current_model = None
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load local LLM configuration"""
        config_path = Path(__file__).parent / "local_llm_config.json"
        
        default_config = {
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
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    default_config.update(user_config)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")
        else:
            # Save default config
            try:
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not save config: {e}[/yellow]")
        
        return default_config
    
    def setup_model(self, model_name: str = "codellama", provider: str = None) -> bool:
        """Setup and initialize a local model"""
        try:
            if provider is None:
                provider = self.config.get("preferred_provider", "ollama")
            
            model_info = self.config["models"].get(model_name)
            if not model_info:
                console.print(f"[red]❌ Unknown model: {model_name}[/red]")
                return False
            
            console.print(f"[cyan]🚀 Setting up {model_name} via {provider}[/cyan]")
            
            if provider == "ollama":
                return self._setup_ollama_model(model_name, model_info)
            elif provider == "transformers":
                return self._setup_transformers_model(model_name, model_info)
            elif provider == "ggml" or provider == "llamacpp":
                return self._setup_ggml_model(model_name, model_info)
            else:
                console.print(f"[red]❌ Unknown provider: {provider}[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ Error setting up model: {e}[/red]")
            return False
    
    def _setup_ollama_model(self, model_name: str, model_info: Dict) -> bool:
        """Setup model via Ollama"""
        ollama_model = model_info["ollama_name"]
        
        # Start Ollama if needed
        if not self.ollama.start_ollama():
            return False
        
        # Check if model exists
        available_models = self.ollama.list_models()
        if ollama_model not in available_models:
            console.print(f"[yellow]📥 Model {ollama_model} not found, downloading...[/yellow]")
            if not self.ollama.pull_model(ollama_model):
                return False
        
        self.current_provider = "ollama"
        self.current_model = ollama_model
        console.print(f"[green]✅ {model_name} ready via Ollama[/green]")
        return True
    
    def _setup_transformers_model(self, model_name: str, model_info: Dict) -> bool:
        """Setup model via Transformers"""
        transformers_model = model_info["transformers_name"]
        
        if not self.transformers.load_model(transformers_model):
            return False
        
        self.current_provider = "transformers"
        self.current_model = transformers_model
        console.print(f"[green]✅ {model_name} ready via Transformers[/green]")
        return True
    
    def _setup_ggml_model(self, model_name: str, model_info: Dict) -> bool:
        """Setup model via GGML/llama-cpp-python"""
        ggml_model = model_info.get("ggml_name")
        if not ggml_model:
            console.print(f"[red]❌ No GGML model specified for {model_name}[/red]")
            return False
        
        if not self.llamacpp.load_model(ggml_model):
            return False
        
        self.current_provider = "ggml"
        self.current_model = ggml_model
        console.print(f"[green]✅ {model_name} ready via GGML[/green]")
        return True
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using the current model"""
        if not self.current_provider or not self.current_model:
            raise Exception("No model loaded. Call setup_model() first.")
        
        # Merge with default generation params
        gen_params = self.config["generation_params"].copy()
        gen_params.update(kwargs)
        
        try:
            if self.current_provider == "ollama":
                return self.ollama.generate(self.current_model, prompt, **gen_params)
            elif self.current_provider == "transformers":
                return self.transformers.generate(prompt, **gen_params)
            elif self.current_provider == "ggml":
                return self.llamacpp.generate(prompt, **gen_params)
            else:
                raise Exception(f"Unknown provider: {self.current_provider}")
                
        except Exception as e:
            console.print(f"[red]❌ Generation error: {e}[/red]")
            raise
    
    def list_available_models(self) -> Dict:
        """List all available models and their status"""
        status = {}
        
        # Check Ollama models
        if self.ollama.is_running():
            ollama_models = self.ollama.list_models()
            status["ollama"] = {
                "service_running": True,
                "models": ollama_models
            }
        else:
            status["ollama"] = {
                "service_running": False,
                "models": []
            }
        
        # Check configured models
        status["configured"] = self.config["models"]
        
        # Check local GGML models
        local_ggml_models = self.llamacpp.list_local_models()
        status["ggml"] = {
            "models_available": local_ggml_models,
            "models_directory": str(self.llamacpp.models_dir)
        }
        
        return status
    
    def get_status(self) -> Dict:
        """Get current status of local LLM setup"""
        return {
            "current_provider": self.current_provider,
            "current_model": self.current_model,
            "ollama_running": self.ollama.is_running(),
            "config": self.config
        }

# Automation helper functions
class AutomationManager:
    """Manages automation tasks using local LLM"""
    
    def __init__(self, llm_manager: LocalLLMManager):
        self.llm = llm_manager
        
    def generate_code(self, task_description: str, language: str = "python") -> str:
        """Generate code for automation tasks"""
        prompt = f"""
You are an expert {language} developer. Generate clean, well-documented code for the following task:

Task: {task_description}

Requirements:
- Write production-ready code
- Include proper error handling
- Add clear comments
- Follow best practices for {language}
- Make it modular and reusable

Code:
"""
        return self.llm.generate(prompt, max_tokens=1024)
    
    def fix_code_issues(self, code: str, error_message: str) -> str:
        """Fix code issues using LLM"""
        prompt = f"""
Fix the following code that has an error:

Error: {error_message}

Code:
{code}

Please provide the corrected code with explanation of what was fixed:
"""
        return self.llm.generate(prompt, max_tokens=1024)
    
    def optimize_code(self, code: str, focus: str = "performance") -> str:
        """Optimize code for performance, readability, etc."""
        prompt = f"""
Optimize the following code focusing on {focus}:

{code}

Provide the optimized version with explanation of improvements:
"""
        return self.llm.generate(prompt, max_tokens=1024)

# CLI functions for testing
def test_local_llm():
    """Test local LLM functionality"""
    console.print("[cyan]🧪 Testing Local LLM Setup[/cyan]")
    
    llm = LocalLLMManager()
    
    # Show status
    status = llm.get_status()
    console.print(Panel(json.dumps(status, indent=2), title="Current Status"))
    
    # Setup model
    if llm.setup_model("codellama", "ollama"):
        # Test generation
        test_prompt = "Write a Python function to calculate fibonacci numbers:"
        console.print(f"\n[yellow]Test prompt: {test_prompt}[/yellow]")
        
        try:
            response = llm.generate(test_prompt, max_tokens=512)
            console.print(Panel(response, title="Generated Response", border_style="green"))
        except Exception as e:
            console.print(f"[red]Generation failed: {e}[/red]")

if __name__ == "__main__":
    test_local_llm()
