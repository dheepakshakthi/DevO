#!/usr/bin/env python3
"""
DevO Chat - Unified AI Assistant with Local LLM & Cloud AI
Combines Gemini API, Local LLM, and automation with proper memory management and GPU support
"""

import os
import sys
import json
import asyncio
import gc
import psutil
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import traceback
import subprocess
import shutil
import tempfile
from dataclasses import dataclass
from enum import Enum

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.columns import Columns
from rich.layout import Layout
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
import google.generativeai as genai

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import local modules
from local_llm import LocalLLMManager, AutomationManager
from utils import (
    detect_language_from_files, detect_framework_from_files, 
    detect_package_manager, extract_dependencies
)
from templates import get_dockerfile_template
from auto_setup import AutoSetupManager

console = Console()

class AIProvider(Enum):
    """Available AI providers"""
    GEMINI = "gemini"
    LOCAL = "local"
    HYBRID = "hybrid"

@dataclass
class MemoryConfig:
    """Memory management configuration"""
    max_ram_usage_gb: float = 8.0
    enable_gpu: bool = True
    auto_cleanup: bool = True
    cache_limit_mb: int = 512

class MemoryManager:
    """Manages memory usage and GPU resources"""
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.initial_memory = psutil.virtual_memory().used / (1024**3)
        
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        memory = psutil.virtual_memory()
        return {
            'used_gb': memory.used / (1024**3),
            'available_gb': memory.available / (1024**3),
            'percent': memory.percent,
            'total_gb': memory.total / (1024**3)
        }
    
    def get_gpu_usage(self) -> Dict[str, Any]:
        """Get GPU usage if available"""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                gpu_allocated = torch.cuda.memory_allocated(0) / (1024**3)
                gpu_cached = torch.cuda.memory_reserved(0) / (1024**3)
                
                return {
                    'available': True,
                    'total_gb': gpu_memory,
                    'allocated_gb': gpu_allocated,
                    'cached_gb': gpu_cached,
                    'free_gb': gpu_memory - gpu_allocated,
                    'device_name': torch.cuda.get_device_name(0)
                }
        except ImportError:
            pass
        
        return {'available': False}
    
    def cleanup_memory(self):
        """Force memory cleanup"""
        gc.collect()
        
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                console.print("[dim]🧹 GPU cache cleared[/dim]")
        except ImportError:
            pass
        
        console.print("[dim]🧹 Memory cleanup completed[/dim]")
    
    def check_memory_limit(self) -> bool:
        """Check if memory usage is within limits"""
        usage = self.get_memory_usage()
        return usage['used_gb'] < self.config.max_ram_usage_gb
    
    def display_memory_status(self):
        """Display current memory and GPU status"""
        memory = self.get_memory_usage()
        gpu = self.get_gpu_usage()
        
        table = Table(title="💾 Memory & GPU Status")
        table.add_column("Resource", style="cyan")
        table.add_column("Usage", style="yellow")
        table.add_column("Status", style="green")
        
        # Memory status
        memory_status = "🟢 Good" if memory['percent'] < 80 else "🟡 High" if memory['percent'] < 90 else "🔴 Critical"
        table.add_row(
            "RAM",
            f"{memory['used_gb']:.1f}GB / {memory['total_gb']:.1f}GB ({memory['percent']:.1f}%)",
            memory_status
        )
        
        # GPU status
        if gpu['available']:
            gpu_percent = (gpu['allocated_gb'] / gpu['total_gb']) * 100
            gpu_status = "🟢 Good" if gpu_percent < 80 else "🟡 High" if gpu_percent < 90 else "🔴 Critical"
            table.add_row(
                f"GPU ({gpu['device_name']})",
                f"{gpu['allocated_gb']:.1f}GB / {gpu['total_gb']:.1f}GB ({gpu_percent:.1f}%)",
                gpu_status
            )
        else:
            table.add_row("GPU", "Not Available", "🔴 N/A")
        
        console.print(table)

class UnifiedChatSession:
    """Unified chat session with Gemini API, Local LLM, and automation features"""
    
    def __init__(self, api_key: str = None, repo_path: str = None):
        self.api_key = api_key
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.chat_history = []
        self.repo_context = None
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Memory management
        self.memory_config = MemoryConfig()
        self.memory_manager = MemoryManager(self.memory_config)
        
        # AI providers
        self.current_provider = AIProvider.GEMINI
        self.gemini_model = None
        self.local_llm = None
        self.automation = None
        
        # Initialize providers
        self._initialize_providers()
        
        # Auto setup manager
        if api_key:
            self.auto_setup = AutoSetupManager(api_key)
        else:
            self.auto_setup = None
        
        # Initialize repository context
        self._initialize_repository_context()
        
        # Display welcome message
        self._display_welcome()
    
    def _initialize_providers(self):
        """Initialize AI providers based on availability"""
        providers_status = {}
        
        # Initialize Gemini if API key available
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash-exp")
                providers_status['gemini'] = "✅ Ready"
            except Exception as e:
                providers_status['gemini'] = f"❌ Failed: {e}"
        else:
            providers_status['gemini'] = "⚠️ No API key"
        
        # Initialize Local LLM
        try:
            self.local_llm = LocalLLMManager()
            self.automation = AutomationManager(self.local_llm)
            providers_status['local_llm'] = "✅ Ready"
        except Exception as e:
            providers_status['local_llm'] = f"❌ Failed: {e}"
        
        # Set default provider
        if self.gemini_model:
            self.current_provider = AIProvider.GEMINI
        elif self.local_llm:
            self.current_provider = AIProvider.LOCAL
        else:
            console.print("[red]❌ No AI providers available![/red]")
            sys.exit(1)
        
        # Display provider status
        table = Table(title="🤖 AI Providers Status")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="white")
        
        for provider, status in providers_status.items():
            table.add_row(provider.replace('_', ' ').title(), status)
        
        console.print(table)
    
    def _display_welcome(self):
        """Display welcome message with capabilities"""
        gpu_info = self.memory_manager.get_gpu_usage()
        gpu_text = f"🚀 GPU: {gpu_info['device_name']}" if gpu_info['available'] else "💻 CPU Only"
        
        welcome_text = f"""🚀 [bold green]DevO Unified Chat Assistant[/bold green]

📁 Repository: {self.repo_path.name}
🤖 AI Provider: {self.current_provider.value.title()}
{gpu_text}
💾 Memory Management: Enabled

[bold cyan]🎯 Capabilities:[/bold cyan]
• 💬 Natural conversation with AI
• 🔍 Repository analysis & insights  
• 🛠️ Code generation & automation
• 🐛 Bug fixing & optimization
• 📦 Dependency management
• 🐳 Containerization support
• 🚀 Auto repository setup

[bold yellow]⚡ Quick Commands:[/bold yellow]
• [cyan]switch provider[/cyan] - Change AI provider
• [cyan]memory status[/cyan] - Check memory usage
• [cyan]setup model[/cyan] - Configure local model
• [cyan]analyze repo[/cyan] - Analyze repository
• [cyan]generate code[/cyan] - Create automation code
• [cyan]fix issues[/cyan] - Fix code problems
• [cyan]help[/cyan] - Show all commands
• [cyan]exit[/cyan] - Quit assistant

[dim]Type your question or command naturally...[/dim]"""
        
        console.print(Panel(welcome_text, title="DevO Unified Assistant", border_style="green"))
        
        # Show memory status
        self.memory_manager.display_memory_status()
    
    def _initialize_repository_context(self):
        """Analyze repository context on startup"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("Analyzing repository...", total=1)
                
                # Analyze repository structure
                self.repo_context = self._analyze_repository()
                
                progress.update(task, completed=1)
                
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not analyze repository: {e}[/yellow]")
    
    def _analyze_repository(self) -> Dict:
        """Comprehensive repository analysis"""
        context = {
            'path': str(self.repo_path),
            'name': self.repo_path.name,
            'size': 0,
            'file_count': 0,
            'languages': {},
            'frameworks': [],
            'package_manager': None,
            'dependencies': {},
            'structure': {},
            'last_analyzed': datetime.now().isoformat()
        }
        
        if not self.repo_path.exists():
            return context
        
        # Count files and calculate size
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file():
                context['file_count'] += 1
                context['size'] += file_path.stat().st_size
        
        # Detect languages and frameworks
        context['languages'] = detect_language_from_files(self.repo_path)
        context['frameworks'] = detect_framework_from_files(self.repo_path)
        context['package_manager'] = detect_package_manager(self.repo_path)
        
        # Extract dependencies if package manager found
        if context['package_manager']:
            context['dependencies'] = extract_dependencies(self.repo_path, context['package_manager'])
        
        return context
    
    def switch_provider(self, provider: str = None):
        """Switch between AI providers"""
        if provider is None:
            # Interactive provider selection
            available_providers = []
            if self.gemini_model:
                available_providers.append("gemini")
            if self.local_llm:
                available_providers.append("local")
            
            if len(available_providers) == 0:
                console.print("[red]❌ No providers available![/red]")
                return
            
            console.print("\n[cyan]Available AI Providers:[/cyan]")
            for i, prov in enumerate(available_providers, 1):
                current = " (current)" if prov == self.current_provider.value else ""
                console.print(f"{i}. {prov.title()}{current}")
            
            choice = Prompt.ask("Select provider", choices=[str(i) for i in range(1, len(available_providers) + 1)])
            provider = available_providers[int(choice) - 1]
        
        # Switch provider
        if provider == "gemini" and self.gemini_model:
            self.current_provider = AIProvider.GEMINI
            console.print("[green]✅ Switched to Gemini API[/green]")
        elif provider == "local" and self.local_llm:
            self.current_provider = AIProvider.LOCAL
            console.print("[green]✅ Switched to Local LLM[/green]")
        else:
            console.print(f"[red]❌ Provider '{provider}' not available[/red]")
    
    def setup_local_model(self):
        """Interactive local model setup"""
        if not self.local_llm:
            console.print("[red]❌ Local LLM manager not available[/red]")
            return
        
        # Show available models
        status = self.local_llm.list_available_models()
        
        console.print("\n[cyan]🤖 Available Local Models:[/cyan]")
        
        # Show configured models
        table = Table(title="Configured Models")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Providers", style="yellow")
        
        for model_name, model_info in status["configured"].items():
            providers = []
            if "ollama_name" in model_info:
                providers.append("Ollama")
            if "transformers_name" in model_info:
                providers.append("Transformers")
            if "ggml_name" in model_info:
                providers.append("GGML")
            
            table.add_row(model_name, model_info["description"], ", ".join(providers))
        
        console.print(table)
        
        # Show GGML models in directory
        if status["ggml"]["models_available"]:
            console.print(f"\n[cyan]📁 GGML Models in {status['ggml']['models_directory']}:[/cyan]")
            for model in status["ggml"]["models_available"]:
                console.print(f"  • {model}")
        
        # Interactive setup
        model_name = Prompt.ask("\nEnter model name to setup", choices=list(status["configured"].keys()))
        
        # Choose provider
        model_info = status["configured"][model_name]
        available_providers = []
        
        if "ollama_name" in model_info:
            available_providers.append("ollama")
        if "transformers_name" in model_info:
            available_providers.append("transformers")
        if "ggml_name" in model_info:
            available_providers.append("ggml")
        
        if len(available_providers) > 1:
            provider = Prompt.ask("Choose provider", choices=available_providers)
        else:
            provider = available_providers[0]
        
        # Setup model
        console.print(f"\n[cyan]🚀 Setting up {model_name} via {provider}...[/cyan]")
        
        # Check memory before loading
        if not self.memory_manager.check_memory_limit():
            if not Confirm.ask("⚠️ Memory usage is high. Continue anyway?"):
                return
        
        if self.local_llm.setup_model(model_name, provider):
            self.current_provider = AIProvider.LOCAL
            console.print(f"[green]✅ {model_name} ready! Switched to local provider.[/green]")
        else:
            console.print(f"[red]❌ Failed to setup {model_name}[/red]")
    
    def generate_response(self, user_input: str) -> str:
        """Generate response using current AI provider"""
        try:
            # Check memory before generation
            if self.memory_config.auto_cleanup and not self.memory_manager.check_memory_limit():
                console.print("[yellow]⚠️ High memory usage detected, cleaning up...[/yellow]")
                self.memory_manager.cleanup_memory()
            
            # Add repository context if available
            context_prompt = ""
            if self.repo_context:
                context_prompt = f"""
Repository Context:
- Name: {self.repo_context['name']}
- Languages: {', '.join(self.repo_context['languages'].keys())}
- Frameworks: {', '.join(self.repo_context['frameworks'])}
- Package Manager: {self.repo_context['package_manager']}

"""
            
            full_prompt = context_prompt + user_input
            
            if self.current_provider == AIProvider.GEMINI:
                return self._generate_gemini_response(full_prompt)
            elif self.current_provider == AIProvider.LOCAL:
                return self._generate_local_response(full_prompt)
            else:
                raise Exception(f"Unknown provider: {self.current_provider}")
                
        except Exception as e:
            console.print(f"[red]❌ Error generating response: {e}[/red]")
            return f"Sorry, I encountered an error: {e}"
    
    def _generate_gemini_response(self, prompt: str) -> str:
        """Generate response using Gemini API"""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {e}")
    
    def _generate_local_response(self, prompt: str) -> str:
        """Generate response using Local LLM"""
        try:
            if not self.local_llm.current_provider:
                raise Exception("No local model loaded. Use 'setup model' command first.")
            
            return self.local_llm.generate(prompt, max_tokens=1024)
        except Exception as e:
            raise Exception(f"Local LLM error: {e}")
    
    def handle_automation_command(self, command: str, params: str = ""):
        """Handle automation-specific commands"""
        if not self.automation:
            console.print("[red]❌ Automation not available (requires local LLM)[/red]")
            return
        
        try:
            if command == "generate_code":
                language = Prompt.ask("Programming language", default="python")
                task = Prompt.ask("Describe the task")
                
                console.print("[cyan]🔧 Generating code...[/cyan]")
                code = self.automation.generate_code(task, language)
                
                console.print(Panel(
                    Syntax(code, language, theme="monokai"),
                    title=f"Generated {language.title()} Code",
                    border_style="green"
                ))
                
            elif command == "fix_code":
                code = Prompt.ask("Enter the problematic code")
                error = Prompt.ask("Describe the error or issue")
                
                console.print("[cyan]🔧 Fixing code...[/cyan]")
                fixed_code = self.automation.fix_code_issues(code, error)
                
                console.print(Panel(
                    Markdown(fixed_code),
                    title="Fixed Code with Explanation",
                    border_style="green"
                ))
                
            elif command == "optimize_code":
                code = Prompt.ask("Enter the code to optimize")
                focus = Prompt.ask("Optimization focus", default="performance", 
                                 choices=["performance", "readability", "memory", "security"])
                
                console.print("[cyan]🔧 Optimizing code...[/cyan]")
                optimized = self.automation.optimize_code(code, focus)
                
                console.print(Panel(
                    Markdown(optimized),
                    title=f"Optimized Code ({focus.title()})",
                    border_style="green"
                ))
                
        except Exception as e:
            console.print(f"[red]❌ Automation error: {e}[/red]")
    
    def display_help(self):
        """Display comprehensive help"""
        help_text = """
[bold cyan]🎯 DevO Unified Chat Commands[/bold cyan]

[bold yellow]🤖 AI Provider Management:[/bold yellow]
• [cyan]switch provider[/cyan] - Change between Gemini/Local LLM
• [cyan]setup model[/cyan] - Configure local LLM models
• [cyan]model status[/cyan] - Show current model status

[bold yellow]💾 Memory Management:[/bold yellow]
• [cyan]memory status[/cyan] - Show memory and GPU usage
• [cyan]cleanup memory[/cyan] - Force memory cleanup
• [cyan]memory config[/cyan] - Adjust memory settings

[bold yellow]🔍 Repository Analysis:[/bold yellow]
• [cyan]analyze repo[/cyan] - Full repository analysis
• [cyan]check deps[/cyan] - Analyze dependencies
• [cyan]security scan[/cyan] - Check for security issues
• [cyan]suggest improvements[/cyan] - Code improvement suggestions

[bold yellow]🛠️ Automation & Code:[/bold yellow]
• [cyan]generate code[/cyan] - Create automation scripts
• [cyan]fix code[/cyan] - Fix code issues
• [cyan]optimize code[/cyan] - Optimize existing code
• [cyan]create dockerfile[/cyan] - Generate Docker configuration

[bold yellow]🚀 Auto Setup:[/bold yellow]
• [cyan]setup <repo_url>[/cyan] - Auto setup repository
• [cyan]containerize[/cyan] - Auto containerization
• [cyan]deploy prep[/cyan] - Prepare for deployment

[bold yellow]💬 General:[/bold yellow]
• [cyan]help[/cyan] - Show this help
• [cyan]clear[/cyan] - Clear chat history
• [cyan]save session[/cyan] - Save current session
• [cyan]exit[/cyan] - Quit assistant

[dim]You can also ask questions naturally in conversation![/dim]
"""
        console.print(Panel(help_text, title="Help & Commands", border_style="blue"))
    
    def save_session(self):
        """Save current chat session"""
        try:
            session_data = {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'repo_path': str(self.repo_path),
                'provider': self.current_provider.value,
                'chat_history': self.chat_history,
                'repo_context': self.repo_context
            }
            
            sessions_dir = Path("chat_sessions")
            sessions_dir.mkdir(exist_ok=True)
            
            session_file = sessions_dir / f"session_{self.session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            console.print(f"[green]💾 Session saved to {session_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Failed to save session: {e}[/red]")
    
    def run_interactive_chat(self):
        """Main interactive chat loop"""
        console.print("\n[green]🚀 Chat started! Type 'help' for commands or ask questions naturally.[/green]\n")
        
        try:
            while True:
                try:
                    # Get user input
                    user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle exit commands
                    if user_input.lower() in ['exit', 'quit', 'bye']:
                        if Confirm.ask("Save session before exiting?"):
                            self.save_session()
                        console.print("[green]👋 Goodbye![/green]")
                        break
                    
                    # Handle special commands
                    if user_input.lower() == 'help':
                        self.display_help()
                        continue
                    
                    if user_input.lower() == 'clear':
                        console.clear()
                        self._display_welcome()
                        self.chat_history = []
                        continue
                    
                    if user_input.lower() == 'memory status':
                        self.memory_manager.display_memory_status()
                        continue
                    
                    if user_input.lower() == 'cleanup memory':
                        self.memory_manager.cleanup_memory()
                        continue
                    
                    if user_input.lower() == 'switch provider':
                        self.switch_provider()
                        continue
                    
                    if user_input.lower() == 'setup model':
                        self.setup_local_model()
                        continue
                    
                    if user_input.lower() == 'model status':
                        if self.local_llm:
                            status = self.local_llm.get_status()
                            console.print(Panel(
                                json.dumps(status, indent=2),
                                title="Local LLM Status",
                                border_style="blue"
                            ))
                        else:
                            console.print("[yellow]Local LLM not available[/yellow]")
                        continue
                    
                    if user_input.lower() == 'save session':
                        self.save_session()
                        continue
                    
                    # Handle automation commands
                    if user_input.lower() in ['generate code', 'fix code', 'optimize code']:
                        self.handle_automation_command(user_input.lower().replace(' ', '_'))
                        continue
                    
                    # Add to chat history
                    self.chat_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'user': user_input,
                        'provider': self.current_provider.value
                    })
                    
                    # Show thinking indicator
                    with console.status(f"[cyan]🤖 {self.current_provider.value.title()} is thinking...[/cyan]", spinner="dots"):
                        response = self.generate_response(user_input)
                    
                    # Display response
                    console.print(f"\n[bold green]🤖 {self.current_provider.value.title()}[/bold green]")
                    console.print(Panel(Markdown(response), border_style="green"))
                    
                    # Add response to history
                    self.chat_history[-1]['response'] = response
                    
                    # Memory cleanup if needed
                    if self.memory_config.auto_cleanup:
                        memory_usage = self.memory_manager.get_memory_usage()
                        if memory_usage['percent'] > 85:
                            console.print("[dim]🧹 Auto-cleaning memory due to high usage...[/dim]")
                            self.memory_manager.cleanup_memory()
                
                except KeyboardInterrupt:
                    console.print("\n[yellow]⚠️ Interrupted by user[/yellow]")
                    if Confirm.ask("Exit chat?"):
                        break
                    continue
                
                except Exception as e:
                    console.print(f"[red]❌ Unexpected error: {e}[/red]")
                    console.print("[dim]Chat continues...[/dim]")
                    continue
        
        except Exception as e:
            console.print(f"[red]💥 Fatal error: {e}[/red]")
            console.print(f"[dim]{traceback.format_exc()}[/dim]")

@click.command()
@click.option('--api-key', envvar='GEMINI_API_KEY', help='Gemini API key')
@click.option('--repo-path', default='.', help='Repository path to analyze')
@click.option('--provider', type=click.Choice(['gemini', 'local', 'auto']), default='auto', help='AI provider to use')
@click.option('--max-memory', default=8.0, help='Maximum RAM usage in GB')
@click.option('--enable-gpu/--disable-gpu', default=True, help='Enable/disable GPU usage')
def main(api_key, repo_path, provider, max_memory, enable_gpu):
    """DevO Unified Chat - AI-powered development assistant with local LLM support"""
    
    try:
        # Configure memory management
        memory_config = MemoryConfig(
            max_ram_usage_gb=max_memory,
            enable_gpu=enable_gpu,
            auto_cleanup=True
        )
        
        # Initialize chat session
        chat = UnifiedChatSession(api_key=api_key, repo_path=repo_path)
        chat.memory_config = memory_config
        chat.memory_manager = MemoryManager(memory_config)
        
        # Set provider if specified
        if provider != 'auto':
            chat.switch_provider(provider)
        
        # Start interactive chat
        chat.run_interactive_chat()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]💥 Fatal error: {e}[/red]")
        console.print(f"[dim]{traceback.format_exc()}[/dim]")

if __name__ == "__main__":
    main()
