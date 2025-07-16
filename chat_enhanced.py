#!/usr/bin/env python3
"""
DevO Chat - Enhanced with Local LLM Support
Supports both Gemini API and local models (CodeLlama, Mistral, etc.)
Includes automati            f"[dim]Enhanced Commands:[/dim]\n"
            f"[cyan]• analyze my code[/cyan]\n"
            f"[cyan]• generate <task> - Auto-generate code[/cyan]\n"
            f"[cyan]• fix <e> - Fix code issues[/cyan]\n"
            f"[cyan]• optimize <focus> - Optimize code[/cyan]\n"
            f"[cyan]• demo - Interactive automation demo[/cyan]\n"
            f"[cyan]• switch ai - Switch between AI providers[/cyan]\n"
            f"[cyan]• models - List available models[/cyan]\n"
            f"[cyan]• setup <repo_url> - Auto setup repository[/cyan]\n"
            f"[cyan]• help or exit[/cyan]",es and timeout prevention
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import traceback
import subprocess
import shutil
import tempfile
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
from rich.progress import Progress, SpinnerColumn, TextColumn

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import from existing modules
from utils import (
    detect_language_from_files, detect_framework_from_files, 
    detect_package_manager, extract_dependencies
)
from templates import get_dockerfile_template
from auto_setup import AutoSetupManager

# Import local LLM support
try:
    from local_llm import LocalLLMManager, AutomationManager
    LOCAL_LLM_AVAILABLE = True
except ImportError:
    LOCAL_LLM_AVAILABLE = False
    print("Local LLM support not available. Install dependencies: pip install torch transformers")

# Import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Gemini API not available. Install: pip install google-genai")

console = Console()

class GeminiAutomationManager:
    """Automation manager using Gemini API for code generation, fixing, and optimization"""
    
    def __init__(self, gemini_model):
        self.model = gemini_model
    
    def generate_code(self, task: str, language: str = "python") -> str:
        """Generate code using Gemini API"""
        prompt = f"""
Generate {language} code for the following task: {task}

Requirements:
- Write clean, production-ready code
- Include proper error handling
- Add helpful comments
- Follow {language} best practices
- Make the code modular and reusable

Please provide only the code without additional explanation.
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating code: {e}"
    
    def fix_code_issues(self, code: str, error: str) -> str:
        """Fix code issues using Gemini API"""
        prompt = f"""
Fix the following code that has this error: {error}

Original Code:
```
{code}
```

Error: {error}

Please provide:
1. The corrected code
2. Explanation of what was wrong
3. Best practices to avoid similar issues

Format your response in markdown with code blocks.
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error fixing code: {e}"
    
    def optimize_code(self, code: str, focus: str = "performance") -> str:
        """Optimize code using Gemini API"""
        prompt = f"""
Optimize the following code with focus on: {focus}

Original Code:
```
{code}
```

Optimization Focus: {focus}

Please provide:
1. The optimized code
2. Explanation of improvements made
3. Performance or readability benefits
4. Any trade-offs to consider

Format your response in markdown with code blocks.
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error optimizing code: {e}"

class EnhancedDevOChatSession:
    """Enhanced chat session with local LLM and automation support"""
    
    def __init__(self, api_key: str = None, repo_path: str = None, use_local: bool = False, local_model: str = "codellama"):
        self.api_key = api_key
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.chat_history = []
        self.repo_context = None
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.use_local = use_local
        self.local_model = local_model
        
        # Initialize AI providers
        self.gemini_model = None
        self.local_llm = None
        self.automation = None
        
        self._initialize_ai_providers()
        
        # Initialize auto setup manager if Gemini available
        if self.gemini_model and api_key:
            self.auto_setup = AutoSetupManager(api_key)
        else:
            self.auto_setup = None
        
        # Auto-analyze repository on startup
        self._initialize_repository_context()
        
        # Show initialization message
        self._show_initialization_message()
        
        if self.repo_context:
            self._display_repository_overview()
    
    def _initialize_ai_providers(self):
        """Initialize available AI providers"""
        console.print("[cyan]🤖 Initializing AI providers...[/cyan]")
        
        # Initialize Gemini if available and requested
        if not self.use_local and GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash-exp")
                console.print("[green]✅ Gemini API initialized[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠️  Gemini initialization failed: {e}[/yellow]")
        
        # Initialize local LLM if available and requested
        if (self.use_local or not self.gemini_model) and LOCAL_LLM_AVAILABLE:
            try:
                console.print("[cyan]🚀 Setting up local LLM...[/cyan]")
                self.local_llm = LocalLLMManager()
                
                # Try to setup the model
                if self.local_llm.setup_model(self.local_model):
                    console.print(f"[green]✅ Local LLM ({self.local_model}) initialized[/green]")
                else:
                    console.print("[yellow]⚠️  Local LLM setup failed, trying fallback...[/yellow]")
                    # Try transformers as fallback
                    if self.local_llm.setup_model(self.local_model, "transformers"):
                        console.print(f"[green]✅ Local LLM ({self.local_model}) initialized via Transformers[/green]")
                    else:
                        self.local_llm = None
                        
            except Exception as e:
                console.print(f"[yellow]⚠️  Local LLM initialization failed: {e}[/yellow]")
                self.local_llm = None
        
        # Initialize automation with available AI providers
        if self.local_llm and LOCAL_LLM_AVAILABLE:
            # Use Local LLM for automation if available
            try:
                self.automation = AutomationManager(self.local_llm)
                console.print("[green]✅ Automation enabled with Local LLM[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠️  Local LLM automation failed: {e}[/yellow]")
        
        if not self.automation and self.gemini_model:
            # Use Gemini for automation if Local LLM not available
            try:
                self.automation = GeminiAutomationManager(self.gemini_model)
                console.print("[green]✅ Automation enabled with Gemini API[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠️  Gemini automation failed: {e}[/yellow]")
        
        # Check if we have any working AI
        if not self.gemini_model and not self.local_llm:
            console.print("[red]❌ No AI providers available![/red]")
            console.print("[yellow]Please either:[/yellow]")
            console.print("[yellow]1. Set GEMINI_API_KEY for cloud AI[/yellow]")
            console.print("[yellow]2. Install local LLM dependencies: pip install torch transformers[/yellow]")
            console.print("[yellow]3. Install and setup Ollama for better local performance[/yellow]")
    
    def _show_initialization_message(self):
        """Show enhanced initialization message"""
        ai_provider = "None"
        if self.gemini_model and self.local_llm:
            ai_provider = f"Gemini + Local LLM ({self.local_model})"
        elif self.gemini_model:
            ai_provider = "Gemini 2.0 Flash"
        elif self.local_llm:
            ai_provider = f"Local LLM ({self.local_model})"
        
        console.print(Panel.fit(
            f"🚀 [bold green]Enhanced DevO Chat Assistant[/bold green]\n"
            f"📁 Repository: {self.repo_path.name}\n"
            f"🤖 AI Provider: {ai_provider}\n"
            f"🔧 Automation: {'✅ Enabled' if self.automation else '❌ Disabled'}\n"
            f"💬 Ready for development tasks!\n\n"
            f"[dim]Enhanced Commands:[/dim]\n"
            f"[cyan]• analyze my code[/cyan]\n"
            f"[cyan]• generate <task> - Auto-generate code[/cyan]\n"
            f"[cyan]• fix <error> - Fix code issues[/cyan]\n"
            f"[cyan]• optimize <focus> - Optimize code[/cyan]\n"
            f"[cyan]• switch ai - Switch between AI providers[/cyan]\n"
            f"[cyan]• models - List available models[/cyan]\n"
            f"[cyan]• setup <repo_url> - Auto setup repository[/cyan]\n"
            f"[cyan]• help or exit[/cyan]",
            title="Enhanced DevO Chat",
            border_style="green"
        ))
    
    def _get_ai_response(self, prompt: str) -> str:
        """Get response from available AI provider"""
        try:
            # Try local LLM first if available
            if self.local_llm:
                with console.status("[bold green]🧠 Local AI thinking...", spinner="dots"):
                    return self.local_llm.generate(prompt, max_tokens=1024)
            
            # Fallback to Gemini
            elif self.gemini_model:
                with console.status("[bold green]☁️  Cloud AI thinking...", spinner="dots"):
                    response = self.gemini_model.generate_content(prompt)
                    return response.text
            
            else:
                raise Exception("No AI providers available")
                
        except Exception as e:
            console.print(f"[red]❌ AI Error: {e}[/red]")
            raise
    
    def _initialize_repository_context(self):
        """Automatically analyze repository context on startup"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("🔍 Analyzing repository...", total=1)
                self.repo_context = self._analyze_repository_context()
                progress.update(task, completed=1)
        except Exception as e:
            console.print(f"[yellow]⚠️  Could not analyze repository: {e}[/yellow]")
            self.repo_context = None
    
    def _display_repository_overview(self):
        """Display a quick overview of the repository"""
        if not self.repo_context:
            console.print("[yellow]⚠️  No repository context available[/yellow]")
            return
            
        # Create overview table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Language", self.repo_context.get('language', 'Unknown'))
        table.add_row("Framework", self.repo_context.get('framework', 'None detected'))
        table.add_row("Package Manager", self.repo_context.get('package_manager', 'None'))
        table.add_row("Total Files", str(self.repo_context.get('total_files', 0)))
        
        if self.repo_context.get('dependencies'):
            deps = len(self.repo_context['dependencies'])
            table.add_row("Dependencies", str(deps))
        
        # Show key configuration files
        config_files = self.repo_context.get('config_files', {})
        if config_files:
            table.add_row("Config Files", ", ".join(config_files.keys()))
        
        console.print(Panel(table, title="📊 Repository Overview", border_style="blue"))
    
    def _analyze_repository_context(self):
        """Analyze repository structure and context"""
        if not self.repo_path or not self.repo_path.exists():
            console.print(f"[yellow]⚠️  Repository path invalid or doesn't exist: {self.repo_path}[/yellow]")
            return None
            
        context = {
            'path': str(self.repo_path),
            'name': self.repo_path.name,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Get all files in the repository
            files = []
            for file_path in self.repo_path.rglob('*'):
                if file_path.is_file() and not any(ignore in str(file_path) for ignore in ['.git', '__pycache__', 'node_modules', '.env']):
                    files.append(str(file_path.relative_to(self.repo_path)))
            
            # Limit to first 10 files for performance
            context['files'] = files[:10] if len(files) > 10 else files
            context['total_files'] = len(files)
            
            # Read key configuration files first
            config_files = ['requirements.txt', 'package.json', 'pyproject.toml', 'Dockerfile', 'docker-compose.yml', 'README.md']
            context['config_files'] = {}
            
            for config_file in config_files:
                config_path = self.repo_path / config_file
                if config_path.exists():
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Truncate large files
                            if len(content) > 2000:
                                content = content[:2000] + "... [truncated]"
                            context['config_files'][config_file] = content
                    except Exception as e:
                        context['config_files'][config_file] = f"Error reading file: {e}"
            
            # Detect language and framework
            try:
                language_counts = detect_language_from_files(files)
                if language_counts:
                    # Get the most common language
                    context['language'] = max(language_counts, key=language_counts.get)
                else:
                    context['language'] = 'Unknown'
            except Exception as e:
                console.print(f"[yellow]⚠️  Language detection failed: {e}[/yellow]")
                context['language'] = 'Unknown'
            
            try:
                context['framework'] = detect_framework_from_files(files, context['config_files'])
            except Exception as e:
                console.print(f"[yellow]⚠️  Framework detection failed: {e}[/yellow]")
                context['framework'] = 'Unknown'
            
            try:
                context['package_manager'] = detect_package_manager(files)
            except Exception as e:
                console.print(f"[yellow]⚠️  Package manager detection failed: {e}[/yellow]")
                context['package_manager'] = 'Unknown'
            
            # Extract dependencies
            try:
                context['dependencies'] = extract_dependencies(context['config_files'])
            except Exception as e:
                console.print(f"[yellow]⚠️  Dependency extraction failed: {e}[/yellow]")
                context['dependencies'] = []
            
            console.print(f"[dim]Repository context created: {context['total_files']} files analyzed[/dim]")
            return context
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not analyze repository context: {e}[/yellow]")
            return context
    
    def run(self):
        """Enhanced main chat loop with automation features"""
        console.print("\n" + "="*70)
        console.print("💬 [bold green]Enhanced DevO Chat Assistant[/bold green] - AI Development Partner")
        console.print("="*70)
        
        # Show quick tips
        console.print("\n[dim]💡 Enhanced Features:[/dim]")
        console.print("[dim]• Natural conversation with AI about your code[/dim]")
        console.print("[dim]• Automation: 'generate a REST API for user management'[/dim]")
        console.print("[dim]• Code fixing: 'fix this error: ImportError...'[/dim]")
        console.print("[dim]• Code optimization: 'optimize for performance'[/dim]")
        console.print("[dim]• Switch AI providers on the fly[/dim]\n")
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]", default="")
                
                if not user_input.strip():
                    continue
                
                # Handle exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                    console.print("\n👋 [green]Thanks for using Enhanced DevO Chat! Happy coding![/green]")
                    break
                
                # Handle enhanced commands
                if self._handle_enhanced_commands(user_input):
                    continue
                
                # Process with AI - enhanced conversation
                self._handle_enhanced_conversation(user_input)
                
            except KeyboardInterrupt:
                console.print("\n\n👋 [green]Thanks for using Enhanced DevO Chat! Happy coding![/green]")
                break
            except EOFError:
                console.print("\n\n👋 [green]Thanks for using Enhanced DevO Chat! Happy coding![/green]")
                break
            except Exception as e:
                console.print(f"[red]❌ Error: {e}[/red]")
                console.print("[yellow]Please try again or type 'help' for assistance.[/yellow]")
    
    def _handle_enhanced_commands(self, user_input: str) -> bool:
        """Handle enhanced commands, return True if command was processed"""
        cmd = user_input.lower().strip()
        
        # Help command
        if cmd in ['help', 'h', '?']:
            self._show_enhanced_help()
            return True
        
        # Context display
        if cmd in ['context', 'info', 'repo']:
            self._display_repository_overview()
            return True
        
        # Clear history
        if cmd in ['clear', 'reset']:
            self.chat_history = []
            console.print("[green]✅ Chat history cleared![/green]")
            return True
        
        # Switch AI provider
        if cmd in ['switch ai', 'switch', 'toggle ai']:
            self._switch_ai_provider()
            return True
        
        # List models
        if cmd in ['models', 'list models']:
            self._list_available_models()
            return True
        
        # Automation commands
        if cmd.startswith('generate '):
            task = user_input[9:].strip()
            self._handle_automation_generate(task)
            return True
        
        if cmd.startswith('fix '):
            error = user_input[4:].strip()
            self._handle_automation_fix(error)
            return True
        
        if cmd.startswith('optimize'):
            focus = user_input[8:].strip() if len(user_input) > 8 else "performance"
            self._handle_automation_optimize(focus)
            return True
        
        # Auto setup
        if cmd.startswith('setup '):
            repo_url = user_input[6:].strip()
            self._handle_auto_setup(repo_url)
            return True
        
        # Automation demo
        if cmd in ['demo', 'automation demo', 'demo automation']:
            self._handle_automation_demo()
            return True
        
        return False
    
    def _switch_ai_provider(self):
        """Switch between available AI providers"""
        if not self.gemini_model and not self.local_llm:
            console.print("[red]❌ No AI providers available to switch between[/red]")
            return
        
        if self.gemini_model and self.local_llm:
            # Both available, let user choose
            console.print("[cyan]Available AI providers:[/cyan]")
            console.print("1. Gemini (Cloud AI)")
            console.print("2. Local LLM")
            
            choice = Prompt.ask("Choose provider", choices=["1", "2"], default="1")
            if choice == "1":
                self.use_local = False
                console.print("[green]✅ Switched to Gemini (Cloud AI)[/green]")
            else:
                self.use_local = True
                console.print(f"[green]✅ Switched to Local LLM ({self.local_model})[/green]")
        else:
            console.print("[yellow]⚠️  Only one AI provider available[/yellow]")
    
    def _list_available_models(self):
        """List all available models"""
        console.print("[cyan]🤖 Available AI Models:[/cyan]")
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Provider", style="cyan")
        table.add_column("Model", style="white")
        table.add_column("Status", style="green")
        
        if self.gemini_model:
            table.add_row("Gemini", "gemini-2.0-flash-exp", "✅ Ready")
        
        if self.local_llm:
            status = self.local_llm.get_status()
            table.add_row("Local LLM", status.get("current_model", "Unknown"), "✅ Ready")
            
            # Show available local models
            if LOCAL_LLM_AVAILABLE:
                available = self.local_llm.list_available_models()
                for provider, info in available.items():
                    if provider == "configured":
                        for model_name, model_info in info.items():
                            table.add_row(f"Local ({provider})", model_name, "📋 Configured")
        
        console.print(table)
    
    def _handle_automation_generate(self, task: str):
        """Handle code generation automation"""
        if not self.automation:
            console.print("[red]❌ Automation not available. Gemini API or Local LLM required.[/red]")
            console.print("[yellow]Please set GEMINI_API_KEY or install local LLM dependencies.[/yellow]")
            return
        
        try:
            console.print(f"[cyan]🔧 Generating code for: {task}[/cyan]")
            
            # Detect language from repository context
            language = self.repo_context.get('language', 'python') if self.repo_context else 'python'
            
            code = self.automation.generate_code(task, language)
            
            console.print(Panel(
                Syntax(code, language, theme="monokai", line_numbers=True),
                title=f"Generated {language.title()} Code",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(f"[red]❌ Code generation failed: {e}[/red]")
    
    def _handle_automation_fix(self, error: str):
        """Handle code fixing automation"""
        if not self.automation:
            console.print("[red]❌ Automation not available. Gemini API or Local LLM required.[/red]")
            console.print("[yellow]Please set GEMINI_API_KEY or install local LLM dependencies.[/yellow]")
            return
        
        # Ask for code to fix
        console.print("[yellow]Please paste the problematic code (press Enter twice to finish):[/yellow]")
        code_lines = []
        empty_line_count = 0
        
        while empty_line_count < 2:
            line = input()
            if line == "":
                empty_line_count += 1
            else:
                empty_line_count = 0
            code_lines.append(line)
        
        code = "\n".join(code_lines[:-2])  # Remove the last two empty lines
        
        if not code.strip():
            console.print("[red]❌ No code provided[/red]")
            return
        
        try:
            console.print(f"[cyan]🔧 Fixing code with error: {error}[/cyan]")
            
            fixed_code = self.automation.fix_code_issues(code, error)
            
            console.print(Panel(
                Markdown(fixed_code),
                title="Fixed Code with Explanation",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(f"[red]❌ Code fixing failed: {e}[/red]")
    
    def _handle_automation_optimize(self, focus: str):
        """Handle code optimization automation"""
        if not self.automation:
            console.print("[red]❌ Automation not available. Gemini API or Local LLM required.[/red]")
            console.print("[yellow]Please set GEMINI_API_KEY or install local LLM dependencies.[/yellow]")
            return
        
        # Ask for code to optimize
        console.print(f"[yellow]Please paste the code to optimize (focus: {focus}):[/yellow]")
        console.print("[dim]Press Enter twice to finish[/dim]")
        
        code_lines = []
        empty_line_count = 0
        
        while empty_line_count < 2:
            line = input()
            if line == "":
                empty_line_count += 1
            else:
                empty_line_count = 0
            code_lines.append(line)
        
        code = "\n".join(code_lines[:-2])  # Remove the last two empty lines
        
        if not code.strip():
            console.print("[red]❌ No code provided[/red]")
            return
        
        try:
            console.print(f"[cyan]🔧 Optimizing code for: {focus}[/cyan]")
            
            optimized_code = self.automation.optimize_code(code, focus)
            
            console.print(Panel(
                Markdown(optimized_code),
                title=f"Optimized Code ({focus})",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(f"[red]❌ Code optimization failed: {e}[/red]")
    
    def _handle_automation_demo(self):
        """Handle interactive automation demo"""
        if not self.automation:
            console.print("[red]❌ Automation demo not available. Gemini API or Local LLM required.[/red]")
            console.print("[yellow]Please set GEMINI_API_KEY or install local LLM dependencies.[/yellow]")
            return
        
        console.print(Panel.fit(
            "[bold green]🤖 DevO Chat Automation Demo[/bold green]\n"
            "This demo shows the automation capabilities of Enhanced DevO Chat.\n\n"
            "[cyan]Features demonstrated:[/cyan]\n"
            "• 🚀 Automated code generation\n"
            "• 🔧 Intelligent code fixing\n"
            "• ⚡ Code optimization\n"
            "• 🤖 AI processing (Gemini or Local LLM)\n\n"
            "[yellow]Note: Using your configured AI provider for demonstrations.[/yellow]",
            title="🤖 Automation Demo",
            border_style="green"
        ))
        
        if not Confirm.ask("Continue with automation demo?"):
            console.print("[yellow]Demo cancelled.[/yellow]")
            return
        
        while True:
            console.print("\n[bold cyan]🤖 DevO Automation Demo Menu[/bold cyan]")
            console.print("1. 🚀 Code Generation Demo")
            console.print("2. 🔧 Code Fixing Demo") 
            console.print("3. ⚡ Code Optimization Demo")
            console.print("4. ℹ️  Current AI Provider")
            console.print("5. 🚪 Return to Main Chat")
            
            choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"], default="1")
            
            try:
                if choice == "1":
                    task, language = self._demonstrate_code_generation()
                    console.print(f"\n[cyan]🚀 Generating {language} code for: {task}[/cyan]")
                    
                    result = self.automation.generate_code(task, language)
                    console.print(Panel(
                        Syntax(result, language, theme="monokai", line_numbers=True),
                        title=f"Generated {language.title()} Code",
                        border_style="green"
                    ))
                    
                elif choice == "2":
                    code, error = self._demonstrate_code_fixing()
                    console.print(f"\n[cyan]🔧 Fixing code with error: {error}[/cyan]")
                    
                    result = self.automation.fix_code_issues(code, error)
                    console.print(Panel(
                        Markdown(result),
                        title="Fixed Code with Explanation",
                        border_style="green"
                    ))
                    
                elif choice == "3":
                    code, focus = self._demonstrate_code_optimization()
                    console.print(f"\n[cyan]⚡ Optimizing code for: {focus}[/cyan]")
                    
                    result = self.automation.optimize_code(code, focus)
                    console.print(Panel(
                        Markdown(result),
                        title=f"Optimized Code ({focus})",
                        border_style="green"
                    ))
                    
                elif choice == "4":
                    self._show_current_ai_provider()
                    
                elif choice == "5":
                    console.print("[green]👋 Returning to main chat![/green]")
                    break
                    
            except Exception as e:
                console.print(f"[red]❌ Demo error: {e}[/red]")
                console.print("[yellow]Please try again or check your setup.[/yellow]")
    
    def _show_current_ai_provider(self):
        """Show current AI provider information"""
        console.print(Panel(
            f"🤖 **Current AI Provider Information**\n\n"
            f"**Gemini API**: {'✅ Available' if self.gemini_model else '❌ Not available'}\n"
            f"**Local LLM**: {'✅ Available' if self.local_llm else '❌ Not available'}\n"
            f"**Automation**: {'✅ Enabled' if self.automation else '❌ Disabled'}\n"
            f"**Provider Type**: {'Gemini-based' if isinstance(self.automation, GeminiAutomationManager) else 'Local LLM-based' if self.automation else 'None'}\n\n"
            f"**Usage Priority**: {'Local LLM first, then Gemini fallback' if self.local_llm and self.gemini_model else 'Gemini only' if self.gemini_model else 'Local LLM only' if self.local_llm else 'None available'}",
            title="AI Provider Status",
            border_style="blue"
        ))
    
    def _demonstrate_code_generation(self):
        """Demonstrate automated code generation"""
        console.print("\n[bold cyan]🚀 Code Generation Demo[/bold cyan]")
        
        tasks = [
            "Create a REST API endpoint for user authentication",
            "Write a function to validate email addresses",
            "Generate a class for handling database connections",
            "Create a decorator for logging function calls",
            "Write unit tests for a calculator function"
        ]
        
        # Let user choose or input custom task
        console.print("\n[yellow]Choose a task or enter your own:[/yellow]")
        for i, task in enumerate(tasks, 1):
            console.print(f"{i}. {task}")
        console.print("6. Custom task")
        
        choice = Prompt.ask("Select option", choices=[str(i) for i in range(1, 7)], default="1")
        
        if choice == "6":
            task = Prompt.ask("Enter your custom task")
        else:
            task = tasks[int(choice) - 1]
        
        language = Prompt.ask("Programming language", default="python")
        
        return task, language
    
    def _demonstrate_code_fixing(self):
        """Demonstrate automated code fixing"""
        console.print("\n[bold cyan]🔧 Code Fixing Demo[/bold cyan]")
        
        # Example buggy code
        buggy_examples = {
            "1": {
                "code": """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

# This will cause division by zero error
result = calculate_average([])
print(result)
""",
                "error": "ZeroDivisionError: division by zero"
            },
            "2": {
                "code": """
import requests

def fetch_data(url):
    response = requests.get(url)
    return response.json()

# This doesn't handle potential errors
data = fetch_data("https://invalid-url.com")
print(data)
""",
                "error": "ConnectionError: Failed to establish a new connection"
            },
            "3": {
                "code": """
def process_file(filename):
    file = open(filename, 'r')
    content = file.read()
    return content.upper()

# This doesn't close the file properly
result = process_file("test.txt")
print(result)
""",
                "error": "Resource leak: file not properly closed"
            }
        }
        
        console.print("\n[yellow]Choose buggy code to fix:[/yellow]")
        for key, example in buggy_examples.items():
            console.print(f"{key}. {example['error']}")
        console.print("4. Enter custom code")
        
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"], default="1")
        
        if choice == "4":
            console.print("[yellow]Enter your code (press Enter twice to finish):[/yellow]")
            code_lines = []
            empty_line_count = 0
            
            while empty_line_count < 2:
                line = input()
                if line == "":
                    empty_line_count += 1
                else:
                    empty_line_count = 0
                code_lines.append(line)
            
            code = "\n".join(code_lines[:-2])
            error = Prompt.ask("Describe the error")
        else:
            example = buggy_examples[choice]
            code = example["code"]
            error = example["error"]
        
        return code, error
    
    def _demonstrate_code_optimization(self):
        """Demonstrate code optimization"""
        console.print("\n[bold cyan]⚡ Code Optimization Demo[/bold cyan]")
        
        # Example code that can be optimized
        optimization_examples = {
            "1": """
def find_duplicates(list1, list2):
    duplicates = []
    for item1 in list1:
        for item2 in list2:
            if item1 == item2:
                duplicates.append(item1)
    return duplicates
""",
            "2": """
def calculate_sum(numbers):
    result = 0
    for i in range(len(numbers)):
        result = result + numbers[i]
    return result
""",
            "3": """
import time

def slow_fibonacci(n):
    if n <= 1:
        return n
    return slow_fibonacci(n-1) + slow_fibonacci(n-2)

# This is very slow for large numbers
result = slow_fibonacci(30)
print(result)
"""
        }
        
        console.print("\n[yellow]Choose code to optimize:[/yellow]")
        console.print("1. Nested loop optimization")
        console.print("2. List iteration optimization")
        console.print("3. Fibonacci performance optimization")
        console.print("4. Enter custom code")
        
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"], default="1")
        
        if choice == "4":
            console.print("[yellow]Enter your code (press Enter twice to finish):[/yellow]")
            code_lines = []
            empty_line_count = 0
            
            while empty_line_count < 2:
                line = input()
                if line == "":
                    empty_line_count += 1
                else:
                    empty_line_count = 0
                code_lines.append(line)
            
            code = "\n".join(code_lines[:-2])
        else:
            code = optimization_examples[choice]
        
        focus = Prompt.ask("Optimization focus", 
                          choices=["performance", "readability", "memory", "maintainability"], 
                          default="performance")
        
        return code, focus
    
    def _handle_enhanced_conversation(self, user_input: str):
        """Handle enhanced conversation with automation and local LLM support"""
        try:
            # Add user input to history
            self.chat_history.append({"role": "user", "content": user_input})
            
            # Build context-aware prompt
            enhanced_prompt = self._build_context_aware_prompt(user_input)
            
            # Get AI response using appropriate provider
            ai_response = self._get_ai_response(enhanced_prompt)
            
            # Add AI response to history
            self.chat_history.append({"role": "assistant", "content": ai_response})
            
            # Display response with nice formatting
            provider_emoji = "🧠" if self.use_local or not self.gemini_model else "☁️"
            console.print(f"\n[bold green]{provider_emoji} DevO:[/bold green]")
            console.print(Panel(Markdown(ai_response), border_style="green", padding=(1, 2)))
            
        except Exception as e:
            console.print(f"[red]❌ Error getting AI response: {e}[/red]")
            console.print("[yellow]Please try rephrasing your question or check your AI setup.[/yellow]")
    
    def _build_context_aware_prompt(self, user_input: str) -> str:
        """Build a comprehensive prompt with repository context"""
        context_info = ""
        
        if self.repo_context:
            context_info = f"""
REPOSITORY CONTEXT:
- Path: {self.repo_context.get('path', 'Unknown')}
- Language: {self.repo_context.get('language', 'Unknown')}
- Framework: {self.repo_context.get('framework', 'Unknown')}
- Package Manager: {self.repo_context.get('package_manager', 'Unknown')}
- Total Files: {self.repo_context.get('total_files', 0)}
- Key Files: {', '.join(self.repo_context.get('files', [])[:10])}

DEPENDENCIES:
{self.repo_context.get('dependencies', [])}

CONFIGURATION FILES:
"""
            for filename, content in self.repo_context.get('config_files', {}).items():
                context_info += f"\n{filename}:\n{content[:500]}...\n"
        
        # Build conversation history
        history_context = ""
        if self.chat_history:
            history_context = "\nCONVERSATION HISTORY:\n"
            for entry in self.chat_history[-6:]:  # Last 6 entries
                role = "User" if entry["role"] == "user" else "Assistant"
                history_context += f"{role}: {entry['content'][:200]}...\n"
        
        system_prompt = """You are DevO, an expert AI development assistant. You help developers with:

🔍 **Code Analysis**: Review code for bugs, performance issues, and improvements
🔒 **Security**: Identify vulnerabilities and suggest fixes  
📦 **Dependencies**: Manage packages, check for updates, resolve conflicts
🐳 **Containerization**: Docker setup, optimization, and deployment
🚀 **DevOps**: CI/CD, deployment strategies, and best practices
💡 **Automation**: Generate code, fix issues, optimize performance
🤖 **Local AI**: Support both cloud and local AI models

INSTRUCTIONS:
- Always provide specific, actionable advice
- Include code examples when relevant
- Consider the project's tech stack and context
- Explain complex concepts clearly
- Ask clarifying questions when needed
- Focus on practical solutions
- For code generation, write production-ready code
- For code fixes, explain what was wrong and how it's fixed

Respond conversationally but professionally. Use emojis sparingly and appropriately."""
        
        full_prompt = f"""{system_prompt}

{context_info}

{history_context}

USER QUESTION: {user_input}

Please provide a helpful, contextual response based on the repository information and conversation history."""
        
        return full_prompt
        

def main():
    """Enhanced DevO Chat - AI Development Assistant with Local LLM Support
    
    Supports both cloud AI (Gemini) and local models (CodeLlama, Mistral) with
    automation features for code generation, fixing, and optimization.
    """
    
    parser = argparse.ArgumentParser(
        description='Enhanced DevO Chat - AI Development Assistant with Local LLM Support'
    )
    parser.add_argument('--repo-path', '-r', default='.', 
                       help='Path to repository to analyze')
    parser.add_argument('--api-key', '-k', 
                       help='Gemini API key (can also use GEMINI_API_KEY env var)')
    parser.add_argument('--use-local', '-l', action='store_true', 
                       help='Use local LLM instead of cloud AI')
    parser.add_argument('--local-model', '-m', default='codellama', 
                       help='Local model to use (codellama, mistral, llama2)')
    parser.add_argument('--save-session', '-s', 
                       help='Save session to file')
    parser.add_argument('--load-session', 
                       help='Load session from file')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Interactive AI provider selection')
    
    args = parser.parse_args()
    
    # Get API key from parameter, environment, or .env file
    api_key = args.api_key
    if not api_key:
        api_key = os.getenv('GEMINI_API_KEY')
    
    # Interactive provider selection
    if args.interactive or (not args.use_local and not api_key and LOCAL_LLM_AVAILABLE):
        use_local, local_model, api_key = interactive_provider_selection(api_key)
    else:
        use_local = args.use_local
        local_model = args.local_model
    
    # Check if we have any AI available
    if not use_local and not api_key and not LOCAL_LLM_AVAILABLE:
        console.print("[red]❌ No AI providers available![/red]")
        console.print("[yellow]Please either:[/yellow]")
        console.print("[yellow]1. Set GEMINI_API_KEY environment variable for cloud AI[/yellow]")
        console.print("[yellow]2. Install local LLM: pip install torch transformers[/yellow]")
        console.print("[yellow]3. Use --use-local flag to force local AI[/yellow]")
        console.print("[yellow]4. Use --interactive flag for guided setup[/yellow]")
        return
    
    try:
        # Initialize enhanced chat session
        repo_path = Path(args.repo_path).resolve()
        chat_session = EnhancedDevOChatSession(
            api_key=api_key, 
            repo_path=repo_path, 
            use_local=use_local,
            local_model=local_model
        )
        
        # Load session if requested
        if args.load_session:
            try:
                with open(args.load_session, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    chat_session.chat_history = session_data.get('chat_history', [])
                    console.print("[green]✅ Previous session loaded![/green]")
            except Exception as e:
                console.print(f"[yellow]⚠️  Could not load session: {e}[/yellow]")
        
        # Run chat
        chat_session.run()
        
        # Save session if requested
        if args.save_session:
            try:
                session_data = {
                    'session_id': chat_session.session_id,
                    'repo_path': str(chat_session.repo_path),
                    'chat_history': chat_session.chat_history,
                    'repo_context': chat_session.repo_context,
                    'timestamp': datetime.now().isoformat()
                }
                
                with open(args.save_session, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, indent=2)
                
                console.print(f"[green]✅ Session saved to {args.save_session}[/green]")
            except Exception as e:
                console.print(f"[red]❌ Error saving session: {e}[/red]")
            
    except KeyboardInterrupt:
        console.print("\n\n👋 [green]Thanks for using Enhanced DevO Chat! Happy coding![/green]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        console.print("[yellow]Please check your setup and try again.[/yellow]")


if __name__ == '__main__':
    main()
