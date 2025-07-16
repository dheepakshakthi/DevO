#!/usr/bin/env python3
"""
DevO Chat - Unified Interactive AI Assistant
A comprehensive conversational interface for repository analysis, code suggestions, 
dependency management, containerization, and all development tasks in one place.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import traceback
import subprocess
import shutil
import tempfile

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.columns import Columns
from rich.layout import Layout
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
import google.generativeai as genai

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

console = Console()

class DevOChatSession:
    """Unified chat session handler with built-in repository analysis and AI assistance"""
    
    def __init__(self, api_key: str, repo_path: str = None):
        self.api_key = api_key
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.chat_history = []
        self.repo_context = None
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        # Initialize auto setup manager
        self.auto_setup = AutoSetupManager(api_key)
        
        # Auto-analyze repository on startup
        self._initialize_repository_context()
        
        console.print(Panel.fit(
            f"🚀 [bold green]DevO Chat Assistant Initialized[/bold green]\n"
            f"📁 Repository: {self.repo_path.name}\n"
            f"🤖 AI Model: Gemini 2.0 Flash\n"
            f"💬 Ready for all your development needs!\n\n"
            f"[dim]Type your questions naturally or use commands like:[/dim]\n"
            f"[cyan]• analyze my code[/cyan]\n"
            f"[cyan]• check dependencies[/cyan]\n"
            f"[cyan]• help with containerization[/cyan]\n"
            f"[cyan]• suggest improvements[/cyan]\n"
            f"[cyan]• fix security issues[/cyan]\n"
            f"[cyan]• setup <repo_url> - Auto setup repository[/cyan]\n"
            f"[cyan]• help or exit[/cyan]",
            title="DevO Chat Assistant",
            border_style="green"
        ))
        
        if self.repo_context:
            self._display_repository_overview()
    
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
            return
            
        # Create overview table
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Language", self.repo_context.get('language', 'Unknown'))
        table.add_row("Framework", self.repo_context.get('framework', 'None detected'))
        table.add_row("Package Manager", self.repo_context.get('package_manager', 'None'))
        table.add_row("Total Files", str(len(self.repo_context.get('files', []))))
        
        if self.repo_context.get('dependencies'):
            deps = len(self.repo_context['dependencies'])
            table.add_row("Dependencies", str(deps))
        
        console.print(Panel(table, title="📊 Repository Overview", border_style="blue"))
    
    def _analyze_repository_context(self):
        """Analyze repository structure and context"""
        if not self.repo_path or not self.repo_path.exists():
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
            
            # Detect language and framework
            context['language'] = detect_language_from_files(self.repo_path)
            context['framework'] = detect_framework_from_files(self.repo_path)
            context['package_manager'] = detect_package_manager(self.repo_path)
            
            # Extract dependencies
            try:
                context['dependencies'] = extract_dependencies(self.repo_path)
            except Exception as e:
                context['dependencies'] = []
                
            # Read key configuration files
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
            
            return context
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not analyze repository context: {e}[/yellow]")
            return context
    
    def run(self):
        """Main chat loop - unified experience with built-in analysis"""
        console.print("\n" + "="*70)
        console.print("💬 [bold green]DevO Chat Assistant[/bold green] - Your AI Development Partner")
        console.print("="*70)
        
        # Show quick tips
        console.print("\n[dim]💡 Quick Tips:[/dim]")
        console.print("[dim]• Ask anything about your code: 'What issues do you see?'[/dim]")
        console.print("[dim]• Get help with specific tasks: 'Help me containerize this app'[/dim]")
        console.print("[dim]• Natural conversation: 'How can I improve performance?'[/dim]")
        console.print("[dim]• Type 'help' for commands or 'exit' to quit[/dim]\n")
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]", default="")
                
                if not user_input.strip():
                    continue
                
                # Handle exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                    console.print("\n👋 [green]Thanks for using DevO Chat! Happy coding![/green]")
                    break
                
                # Handle help
                if user_input.lower() in ['help', 'h', '?']:
                    self._show_unified_help()
                    continue
                
                # Handle context display
                if user_input.lower() in ['context', 'info', 'repo']:
                    self._display_repository_overview()
                    continue
                
                # Handle clear history
                if user_input.lower() in ['clear', 'reset']:
                    self.chat_history = []
                    console.print("[green]✅ Chat history cleared![/green]")
                    continue
                
                # Process with AI - this is where the magic happens
                self._handle_unified_conversation(user_input)
                
            except KeyboardInterrupt:
                console.print("\n\n👋 [green]Thanks for using DevO Chat! Happy coding![/green]")
                break
            except EOFError:
                console.print("\n\n👋 [green]Thanks for using DevO Chat! Happy coding![/green]")
                break
            except Exception as e:
                console.print(f"[red]❌ Error: {e}[/red]")
                console.print("[yellow]Please try again or type 'help' for assistance.[/yellow]")
    
    def _show_unified_help(self):
        """Show comprehensive help for the unified chat experience"""
        help_text = """
🤖 **DevO Chat Assistant - Your AI Development Partner**

**How to Use:**
Just chat naturally! Ask questions about your code, request help with development tasks, 
or get suggestions for improvements. The AI has full context of your repository.

**Example Conversations:**
• "What issues do you see in my code?"
• "How can I improve the performance of this app?"
• "Help me containerize this Python application"
• "What dependencies am I missing?"
• "Are there any security vulnerabilities?"
• "How do I optimize this for production?"
• "Explain how Docker works for this project"
• "What's the best way to deploy this?"

**Quick Commands:**
• `help` - Show this help
• `context` - Show repository information  
• `clear` - Clear chat history
• `setup <repo_url>` - Auto setup repository with dependency correction
• `exit` - Exit the chat

**🚀 Auto Setup Feature:**
Use `setup <repository_url>` to automatically:
- Clone the repository
- Detect language and framework
- Install dependencies with AI-powered error correction
- Fix common issues automatically
- Validate the setup
- Generate comprehensive report

**Features:**
✅ **Automatic Analysis** - Repository analyzed on startup
✅ **Natural Conversation** - Chat like you would with a developer
✅ **Context Aware** - AI knows your codebase and tech stack
✅ **Code Suggestions** - Get specific code improvements
✅ **Security Analysis** - Identify vulnerabilities and fixes
✅ **Containerization** - Docker and deployment help
✅ **Dependency Management** - Missing packages and updates
✅ **Auto Setup** - Automatic repository setup with error fixing
✅ **Best Practices** - Industry-standard recommendations
        """
        console.print(Panel(Markdown(help_text), title="DevO Chat Help", border_style="blue"))
    
    def _handle_unified_conversation(self, user_input: str):
        """Handle natural conversation with built-in analysis capabilities"""
        try:
            # Check for auto setup command
            if user_input.lower().startswith('setup '):
                repo_url = user_input[6:].strip()
                self._handle_auto_setup(repo_url)
                return
            
            # Add user input to history
            self.chat_history.append({"role": "user", "content": user_input})
            
            # Show thinking indicator
            with console.status("[bold green]🤖 DevO is thinking...", spinner="dots"):
                # Build context-aware prompt
                enhanced_prompt = self._build_context_aware_prompt(user_input)
                
                # Get AI response
                response = self.model.generate_content(enhanced_prompt)
                ai_response = response.text
            
            # Add AI response to history
            self.chat_history.append({"role": "assistant", "content": ai_response})
            
            # Display response with nice formatting
            console.print(f"\n[bold green]🤖 DevO:[/bold green]")
            console.print(Panel(Markdown(ai_response), border_style="green", padding=(1, 2)))
            
        except Exception as e:
            console.print(f"[red]❌ Error getting AI response: {e}[/red]")
            console.print("[yellow]Please try rephrasing your question or check your API key.[/yellow]")
    
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
💡 **Suggestions**: Architecture improvements and modern practices

INSTRUCTIONS:
- Always provide specific, actionable advice
- Include code examples when relevant
- Consider the project's tech stack and context
- Explain complex concepts clearly
- Ask clarifying questions when needed
- Focus on practical solutions

Respond conversationally but professionally. Use emojis sparingly and appropriately."""
        
        full_prompt = f"""{system_prompt}

{context_info}

{history_context}

USER QUESTION: {user_input}

Please provide a helpful, contextual response based on the repository information and conversation history."""
        
        return full_prompt
    
    def _handle_auto_setup(self, repo_url: str):
        """Handle automatic repository setup"""
        try:
            console.print(f"[cyan]🚀 Starting auto setup for: {repo_url}[/cyan]")
            
            # Validate URL
            if not repo_url.startswith(('http://', 'https://', 'git@')):
                console.print("[red]❌ Invalid repository URL. Please provide a valid git URL.[/red]")
                return
            
            # Run auto setup
            success = self.auto_setup.setup_repository(repo_url)
            
            if success:
                console.print("\n[green]🎉 Repository setup completed successfully![/green]")
                console.print("[cyan]You can now navigate to the cloned repository and start development.[/cyan]")
                
                # Ask if user wants to switch to the new repository
                from rich.prompt import Confirm
                if Confirm.ask("Would you like to switch to the newly setup repository?"):
                    # Extract repo name from URL
                    repo_name = Path(repo_url).stem
                    new_repo_path = Path.cwd() / repo_name
                    
                    if new_repo_path.exists():
                        self.repo_path = new_repo_path
                        self.repo_context = self._analyze_repository_context()
                        console.print(f"[green]✅ Switched to repository: {new_repo_path}[/green]")
                        self._display_repository_overview()
                    else:
                        console.print("[yellow]⚠️  Repository directory not found for switching.[/yellow]")
                        
            else:
                console.print("[red]❌ Repository setup failed. Please check the URL and try again.[/red]")
                
        except Exception as e:
            console.print(f"[red]❌ Auto setup error: {e}[/red]")
            console.print("[yellow]Please check the repository URL and your internet connection.[/yellow]")


# Session management and CLI interface
def save_session(chat_session: DevOChatSession, filepath: str):
    """Save chat session to file"""
    try:
        session_data = {
            'session_id': chat_session.session_id,
            'repo_path': str(chat_session.repo_path),
            'chat_history': chat_session.chat_history,
            'repo_context': chat_session.repo_context,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2)
        
        console.print(f"[green]✅ Session saved to {filepath}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]❌ Error saving session: {e}[/red]")
        return False


def load_session(filepath: str) -> Optional[Dict]:
    """Load chat session from file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        console.print(f"[green]✅ Session loaded from {filepath}[/green]")
        return session_data
    except Exception as e:
        console.print(f"[red]❌ Error loading session: {e}[/red]")
        return None


@click.command()
@click.option('--repo-path', '-r', default='.', help='Path to repository to analyze')
@click.option('--api-key', '-k', help='Gemini API key (can also use GEMINI_API_KEY env var)')
@click.option('--save-session', '-s', help='Save session to file')
@click.option('--load-session', '-l', help='Load session from file')
def main(repo_path, api_key, save_session, load_session):
    """DevO Chat - Unified AI Development Assistant
    
    A comprehensive conversational interface for repository analysis, code suggestions,
    dependency management, containerization, and all development tasks in one place.
    """
    
    # Get API key from parameter, environment, or .env file
    if not api_key:
        api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        console.print("[red]❌ No API key provided![/red]")
        console.print("[yellow]Please set GEMINI_API_KEY environment variable or use --api-key parameter[/yellow]")
        console.print("[dim]Example: export GEMINI_API_KEY=your_api_key_here[/dim]")
        return
    
    try:
        # Initialize chat session
        repo_path = Path(repo_path).resolve()
        chat_session = DevOChatSession(api_key, repo_path)
        
        # Load session if requested
        if load_session:
            session_data = load_session(load_session)
            if session_data:
                chat_session.chat_history = session_data.get('chat_history', [])
                console.print("[green]✅ Previous session loaded![/green]")
        
        # Run chat
        chat_session.run()
        
        # Save session if requested
        if save_session:
            save_session(chat_session, save_session)
            
    except KeyboardInterrupt:
        console.print("\n\n👋 [green]Thanks for using DevO Chat! Happy coding![/green]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        console.print("[yellow]Please check your API key and try again.[/yellow]")


if __name__ == '__main__':
    main()
