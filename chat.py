#!/usr/bin/env python3
"""
DevO Chat - Interactive AI Assistant for Repository Analysis
A conversational interface for code analysis, suggestions, and dependency management
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import traceback

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

console = Console()

class DevOChatSession:
    """Main chat session handler"""
    
    def __init__(self, api_key: str, repo_path: str = None):
        self.api_key = api_key
        self.repo_path = repo_path
        self.chat_history = []
        self.context = {}
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize Gemini
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                system_instruction=self._get_system_instruction()
            )
        else:
            self.model = None
            
        # Initialize repository context if provided
        if repo_path:
            self._analyze_repository_context()
    
    def _get_system_instruction(self) -> str:
        """Get system instruction for the AI assistant"""
        return """You are DevO, an expert AI assistant specializing in:
1. Code analysis and review
2. Dependency management and security analysis
3. Docker containerization
4. DevOps best practices
5. Repository optimization

You help developers by:
- Analyzing code for issues and improvements
- Suggesting fixes for missing dependencies
- Providing security recommendations
- Helping with containerization
- Explaining complex technical concepts clearly

Always provide:
- Clear, actionable suggestions
- Code examples when relevant
- Security considerations
- Best practice recommendations
- Step-by-step instructions when needed

Be conversational but professional, and ask clarifying questions when needed."""

    def _analyze_repository_context(self):
        """Analyze the repository to provide context"""
        if not self.repo_path or not os.path.exists(self.repo_path):
            return
            
        try:
            # Get basic repository information
            repo_files = []
            for root, dirs, files in os.walk(self.repo_path):
                # Skip hidden directories and common build directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'build', 'dist']]
                
                for file in files:
                    if not file.startswith('.') and any(file.endswith(ext) for ext in ['.py', '.js', '.ts', '.json', '.yml', '.yaml', '.md', '.txt', '.dockerfile']):
                        repo_files.append(os.path.join(root, file))
            
            # Detect language and framework
            language = detect_language_from_files(repo_files)
            
            # Read key files for context
            key_files = {}
            for file_path in repo_files:
                filename = os.path.basename(file_path)
                if filename in ['README.md', 'requirements.txt', 'package.json', 'Dockerfile', 'docker-compose.yml', 'pyproject.toml']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            key_files[filename] = f.read()[:2000]  # Limit content
                    except:
                        pass
            
            framework = detect_framework_from_files(repo_files, key_files)
            
            
            # Read key files for context
            key_files = {}
            for file_path in repo_files:
                filename = os.path.basename(file_path)
                if filename in ['README.md', 'requirements.txt', 'package.json', 'Dockerfile', 'docker-compose.yml', 'pyproject.toml']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            key_files[filename] = f.read()[:2000]  # Limit content
                    except:
                        pass
            
            self.context = {
                'repo_path': self.repo_path,
                'language': language,
                'framework': framework,
                'files_count': len(repo_files),
                'key_files': key_files,
                'file_types': list(set(os.path.splitext(f)[1] for f in repo_files if os.path.splitext(f)[1]))
            }
            
        except Exception as e:
            console.print(f"⚠️  Warning: Could not analyze repository context: {e}")
    
    def display_banner(self):
        """Display the chat application banner"""
        banner = """
╭─────────────────────────────────────────────────────────────────╮
│                          🤖 DevO Chat                          │
│                AI-Powered Development Assistant                 │
│                                                                 │
│  Chat with AI about code analysis, dependencies, and DevOps    │
│  Type 'help' for commands or 'exit' to quit                    │
╰─────────────────────────────────────────────────────────────────╯
        """
        console.print(Panel(banner, border_style="blue"))
        
        # Show context information
        if self.context:
            info_table = Table(show_header=False, box=None, padding=(0, 1))
            info_table.add_column("Key", style="cyan")
            info_table.add_column("Value", style="white")
            
            info_table.add_row("📁 Repository", self.context.get('repo_path', 'Not loaded'))
            info_table.add_row("🔤 Language", self.context.get('language', 'Unknown'))
            info_table.add_row("🚀 Framework", self.context.get('framework', 'Unknown'))
            info_table.add_row("📄 Files", str(self.context.get('files_count', 0)))
            
            console.print(Panel(info_table, title="Repository Context", border_style="green"))
    
    def show_help(self):
        """Display help information"""
        help_content = """
**Available Commands:**
• `analyze` - Analyze current repository for issues
• `deps` - Check and suggest dependency fixes
• `security` - Security analysis and recommendations
• `containerize` - Help with Docker containerization
• `suggest <topic>` - Get suggestions on specific topics
• `explain <concept>` - Explain technical concepts
• `fix <issue>` - Get help fixing specific issues
• `optimize` - Repository optimization suggestions
• `help` - Show this help message
• `context` - Show current repository context
• `clear` - Clear chat history
• `exit` - Exit the chat

**Examples:**
• "analyze my Python code for issues"
• "deps check missing dependencies"
• "security audit my requirements.txt"
• "containerize this Flask app"
• "suggest improvements for performance"
• "explain docker best practices"
• "fix import errors in my code"
        """
        console.print(Panel(Markdown(help_content), title="DevO Chat Help", border_style="yellow"))
    
    def show_context(self):
        """Display current repository context"""
        if not self.context:
            console.print("No repository context loaded. Use 'load <path>' to load a repository.")
            return
            
        context_table = Table(title="Repository Context", show_header=True)
        context_table.add_column("Property", style="cyan")
        context_table.add_column("Value", style="white")
        
        for key, value in self.context.items():
            if key == 'key_files':
                context_table.add_row("Key Files", ", ".join(value.keys()))
            elif key == 'file_types':
                context_table.add_row("File Types", ", ".join(value))
            else:
                context_table.add_row(key.replace('_', ' ').title(), str(value))
        
        console.print(context_table)
    
    def process_command(self, user_input: str) -> bool:
        """Process user commands and return False if should exit"""
        user_input = user_input.strip()
        
        # Handle special commands
        if user_input.lower() in ['exit', 'quit', 'bye']:
            console.print("👋 Thanks for using DevO Chat! Happy coding!")
            return False
            
        elif user_input.lower() == 'help':
            self.show_help()
            return True
            
        elif user_input.lower() == 'context':
            self.show_context()
            return True
            
        elif user_input.lower() == 'clear':
            self.chat_history = []
            console.clear()
            self.display_banner()
            console.print("✅ Chat history cleared!")
            return True
            
        elif user_input.lower().startswith('load '):
            path = user_input[5:].strip()
            if os.path.exists(path):
                self.repo_path = path
                self._analyze_repository_context()
                console.print(f"✅ Repository loaded: {path}")
                self.show_context()
            else:
                console.print(f"❌ Path not found: {path}")
            return True
        
        # Handle AI conversation
        return self._handle_ai_conversation(user_input)
    
    def _handle_ai_conversation(self, user_input: str) -> bool:
        """Handle AI conversation with context"""
        if not self.model:
            console.print("❌ AI model not available. Please check your API key.")
            return True
        
        try:
            # Show thinking spinner
            with console.status("🤔 DevO is thinking...", spinner="dots"):
                # Prepare context for AI
                context_prompt = self._prepare_context_prompt(user_input)
                
                # Get AI response
                response = self.model.generate_content(context_prompt)
                
                # Store in history
                self.chat_history.append({
                    'user': user_input,
                    'ai': response.text,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Display AI response
            console.print(Panel(
                Markdown(response.text),
                title="🤖 DevO Assistant",
                border_style="blue"
            ))
            
        except Exception as e:
            console.print(f"❌ Error: {e}")
            console.print("Please try again or check your API key.")
        
        return True
    
    def _prepare_context_prompt(self, user_input: str) -> str:
        """Prepare context-aware prompt for the AI"""
        prompt_parts = [user_input]
        
        # Add repository context if available
        if self.context:
            context_info = f"""
Repository Context:
- Path: {self.context.get('repo_path', 'Unknown')}
- Language: {self.context.get('language', 'Unknown')}
- Framework: {self.context.get('framework', 'Unknown')}
- Files: {self.context.get('files_count', 0)}
- File Types: {', '.join(self.context.get('file_types', []))}
"""
            
            # Add key file contents if relevant
            if self.context.get('key_files'):
                context_info += "\nKey Files:\n"
                for filename, content in self.context['key_files'].items():
                    context_info += f"\n{filename}:\n```\n{content[:1000]}...\n```\n"
            
            prompt_parts.append(context_info)
        
        # Add recent chat history for context
        if self.chat_history:
            recent_history = self.chat_history[-3:]  # Last 3 exchanges
            history_text = "\nRecent conversation:\n"
            for exchange in recent_history:
                history_text += f"User: {exchange['user']}\n"
                history_text += f"AI: {exchange['ai'][:200]}...\n\n"
            prompt_parts.append(history_text)
        
        return "\n".join(prompt_parts)
    
    def save_session(self):
        """Save chat session to file"""
        if not self.chat_history:
            return
            
        session_file = f"chat_session_{self.session_id}.json"
        try:
            with open(session_file, 'w') as f:
                json.dump({
                    'session_id': self.session_id,
                    'context': self.context,
                    'chat_history': self.chat_history,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
            console.print(f"💾 Session saved to {session_file}")
        except Exception as e:
            console.print(f"⚠️  Could not save session: {e}")

@click.command()
@click.option('--repo-path', '-r', help='Path to repository for analysis')
@click.option('--api-key', envvar='GEMINI_API_KEY', help='Gemini API key')
@click.option('--save-session', is_flag=True, help='Save chat session to file')
def chat(repo_path, api_key, save_session):
    """Start interactive chat with DevO AI assistant"""
    
    if not api_key:
        console.print("❌ API key required. Set GEMINI_API_KEY environment variable or use --api-key option.")
        sys.exit(1)
    
    # Initialize chat session
    session = DevOChatSession(api_key, repo_path)
    session.display_banner()
    
    try:
        while True:
            # Get user input
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]", default="")
            
            if not user_input.strip():
                continue
            
            # Process command
            should_continue = session.process_command(user_input)
            if not should_continue:
                break
                
    except KeyboardInterrupt:
        console.print("\n\n👋 Chat interrupted. Goodbye!")
    except Exception as e:
        console.print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
    finally:
        # Save session if requested
        if save_session:
            session.save_session()

if __name__ == "__main__":
    chat()
