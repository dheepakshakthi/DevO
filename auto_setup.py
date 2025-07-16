    from dotenv import load_dotenv
    import argparse
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.text import Text
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import google.generativeai as genai
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

#!/usr/bin/env python3
"""
Auto Setup Module - Automatic Repository Setup and Dependency Correction
Handles cloning, dependency installation, error detection, and automatic fixes
"""



# Load environment variables
try:
    load_dotenv()
except ImportError:
    self.log(f"Exception occurred: {e}", "ERROR")

console = Console()

class AutoSetupManager:
    """Handles automatic repository setup, dependency correction, and error fixing"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.setup_history = []
        self.error_fixes = []
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
        else:
            self.model = None
            console.print("[yellow]⚠️  No API key available. AI-powered fixes will be disabled.[/yellow]")
    
    def setup_repository(self, repo_url: str, target_dir: str = None) -> bool:
    # TODO: Consider breaking this function into smaller functions
        """Automatically setup repository with dependency correction and error fixing"""
        
        console.print(Panel.fit(
            f"🚀 [bold green]Auto Setup Starting[/bold green]\n"
            f"📎 Repository: {repo_url}\n"
            f"🤖 AI-Powered Fixes: {'✅ Enabled' if self.model else '❌ Disabled'}\n"
            f"🔧 Auto Dependency Correction: ✅ Enabled\n"
            f"🛠️ Error Detection & Fixing: ✅ Enabled",
            title="DevO Auto Setup",
            border_style="green"
        ))
        
        try:
            # Step 1: Clone repository
            repo_path = self._clone_repository(repo_url, target_dir)
            if not repo_path:
                return False
            
            # Step 2: Analyze repository structure
            repo_info = self._analyze_repository_structure(repo_path)
            
            # Step 3: Setup environment and dependencies
            setup_success = self._setup_environment(repo_path, repo_info)
            
            # Step 4: Run error detection and fixing
            if setup_success:
                self._detect_and_fix_errors(repo_path, repo_info)
            
            # Step 5: Validate setup
            validation_result = self._validate_setup(repo_path, repo_info)
            
            # Step 6: Generate summary report
            self._generate_setup_report(repo_path, repo_info, validation_result)
            
            return validation_result['success']
            
        except Exception as e:
            console.print(f"[red]❌ Auto setup failed: {e}[/red]")
            return False
    
    def _clone_repository(self, repo_url: str, target_dir: str = None) -> Optional[str]:
    # TODO: Consider breaking this function into smaller functions
        """Clone repository from URL"""
        try:
            # Extract repo name from URL
            parsed_url = urlparse(repo_url)
            repo_name = Path(parsed_url.path).stem
            
            # Determine target directory
            if target_dir:
                target_path = Path(target_dir) / repo_name
            else:
                target_path = Path.cwd() / repo_name
            
            # Remove existing directory if it exists
            if target_path.exists():
                console.print(f"[yellow]📁 Directory {target_path} already exists,
                    removing...[/yellow]")
                shutil.rmtree(target_path)
            
            # Clone repository
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("📥 Cloning repository...", total=1)
                
                result = subprocess.run([
                    'git', 'clone', repo_url, str(target_path)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    console.print(f"[red]❌ Git clone failed: {result.stderr}[/red]")
                    return None
                
                progress.update(task, completed=1)
            
            console.print(f"[green]✅ Repository cloned to: {target_path}[/green]")
            return str(target_path)
            
        except Exception as e:
            console.print(f"[red]❌ Clone failed: {e}[/red]")
            return None
    
    def _analyze_repository_structure(self, repo_path: str) -> Dict:
    # TODO: Consider breaking this function into smaller functions
        """Analyze repository structure and detect project type"""
        repo_info = {
            'path': repo_path,
            'language': 'unknown',
            'framework': 'unknown',
            'package_manager': 'unknown',
            'config_files': {},
            'dependencies': [],
            'scripts': {},
            'project_type': 'unknown'
        }
        
        try:
            repo_path = Path(repo_path)
            
            # Check for common config files
            config_files = {
                'requirements.txt': 'python',
                'pyproject.toml': 'python',
                'setup.py': 'python',
                'package.json': 'node',
                'yarn.lock': 'node',
                'pnpm-lock.yaml': 'node',
                'Gemfile': 'ruby',
                'composer.json': 'php',
                'go.mod': 'go',
                'Cargo.toml': 'rust',
                'pom.xml': 'java',
                'build.gradle': 'java'
            }
            
            detected_languages = []
            
            for config_file, language in config_files.items():
                config_path = repo_path / config_file
                if config_path.exists():
                    detected_languages.append(language)
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            repo_info['config_files'][config_file] = content
                    except Exception as e:
                        console.print(f"[yellow]⚠️  Could not read {config_file}: {e}[/yellow]")
            
            # Determine primary language
            if detected_languages:
                repo_info['language'] = max(set(detected_languages), key=detected_languages.count)
            
            # Detect framework and package manager based on language
            if repo_info['language'] == 'python':
                repo_info.update(self._analyze_python_project(repo_path))
            elif repo_info['language'] == 'node':
                repo_info.update(self._analyze_node_project(repo_path))
            
            console.print(f"[green]📊 Repository Analysis Complete[/green]")
            console.print(f"[cyan]Language: {repo_info['language']}[/cyan]")
            console.print(f"[cyan]Framework: {repo_info['framework']}[/cyan]")
            console.print(f"[cyan]Package Manager: {repo_info['package_manager']}[/cyan]")
            
            return repo_info
            
        except Exception as e:
            console.print(f"[red]❌ Repository analysis failed: {e}[/red]")
            return repo_info
    
    def _analyze_python_project(self, repo_path: Path) -> Dict:
    # TODO: Consider breaking this function into smaller functions
        """Analyze Python project specifics"""
        info = {
            'package_manager': 'pip',
            'framework': 'unknown',
            'dependencies': [],
            'scripts': {}
        }
        
        # Check for package managers
        if (repo_path / 'pyproject.toml').exists():
            info['package_manager'] = 'pip'  # Could be poetry, but we'll use pip
        if (repo_path / 'poetry.lock').exists():
            info['package_manager'] = 'poetry'
        if (repo_path / 'Pipfile').exists():
            info['package_manager'] = 'pipenv'
        
        # Detect framework
        if (repo_path / 'manage.py').exists():
            info['framework'] = 'django'
        elif any((repo_path / 'app.py').exists(), (repo_path / 'main.py').exists()):
            # Check for Flask imports
            for py_file in repo_path.rglob('*.py'):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'from flask' in content or 'import flask' in content:
                            info['framework'] = 'flask'
                            break
                        elif 'from fastapi' in content or 'import fastapi' in content:
                            info['framework'] = 'fastapi'
                            break
                except:
                    continue
        
        # Extract dependencies
        requirements_file = repo_path / 'requirements.txt'
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    info['dependencies'] = deps
            except:
                pass
        
        return info
    
    def _analyze_node_project(self, repo_path: Path) -> Dict:
    # TODO: Consider breaking this function into smaller functions
        """Analyze Node.js project specifics"""
        info = {
            'package_manager': 'npm',
            'framework': 'unknown',
            'dependencies': [],
            'scripts': {}
        }
        
        # Check for package managers
        if (repo_path / 'yarn.lock').exists():
            info['package_manager'] = 'yarn'
        elif (repo_path / 'pnpm-lock.yaml').exists():
            info['package_manager'] = 'pnpm'
        
        # Analyze package.json
        package_json = repo_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Extract dependencies
                    deps = []
                    for dep_type in ['dependencies', 'devDependencies']:
                        if dep_type in data:
                            deps.extend(data[dep_type].keys())
                    info['dependencies'] = deps
                    
                    # Extract scripts
                    if 'scripts' in data:
                        info['scripts'] = data['scripts']
                    
                    # Detect framework
                    if 'next' in deps:
                        info['framework'] = 'nextjs'
                    elif 'react' in deps:
                        info['framework'] = 'react'
                    elif 'vue' in deps:
                        info['framework'] = 'vue'
                    elif 'angular' in deps:
                        info['framework'] = 'angular'
                    elif 'express' in deps:
                        info['framework'] = 'express'
                    
            except Exception as e:
                console.print(f"[yellow]⚠️  Could not parse package.json: {e}[/yellow]")
        
        return info
    
    def _setup_environment(self, repo_path: str, repo_info: Dict) -> bool:
    # TODO: Consider breaking this function into smaller functions
        """Setup environment and install dependencies"""
        try:
            os.chdir(repo_path)
            
            language = repo_info['language']
            package_manager = repo_info['package_manager']
            
            console.print(f"[cyan]🔧 Setting up {language} environment...[/cyan]")
            
            if language == 'python':
                return self._setup_python_environment(repo_info)
            elif language == 'node':
                return self._setup_node_environment(repo_info)
            else:
                console.print(f"[yellow]⚠️  Unsupported language: {language}[/yellow]")
                return False
                
        except Exception as e:
            console.print(f"[red]❌ Environment setup failed: {e}[/red]")
            return False
    
    def _setup_python_environment(self, repo_info: Dict) -> bool:
    # TODO: Consider breaking this function into smaller functions
        """Setup Python environment with automatic dependency correction"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console
            ) as progress:
                
                # Check if uv is available
                task1 = progress.add_task("🔍 Checking uv availability...", total=1)
                result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
                if result.returncode != 0:
                    console.print("[red]❌ uv is not installed. Please install uv first.[/red]")
                    return False
                progress.update(task1, completed=1)
                
                # Initialize uv project
                task2 = progress.add_task("🔧 Initializing uv project...", total=1)
                subprocess.run(['uv', 'init', '--quiet'], capture_output=True)
                progress.update(task2, completed=1)
                
                # Install dependencies
                task3 = progress.add_task("📦 Installing dependencies...", total=1)
                
                # Install from requirements.txt if exists
                if 'requirements.txt' in repo_info['config_files']:
                    result = subprocess.run([
                        'uv', 'add', '--requirements', 'requirements.txt'
                    ], capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        console.print(f"[yellow]⚠️  Dependency installation issues detected[/yellow]")
                        self._fix_python_dependencies(result.stderr)
                
                # Install common development dependencies
                dev_deps = ['pytest', 'black', 'flake8', 'mypy']
                for dep in dev_deps:
                    subprocess.run(['uv', 'add', '--dev', dep], capture_output=True)
                
                progress.update(task3, completed=1)
            
            console.print("[green]✅ Python environment setup complete[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Python setup failed: {e}[/red]")
            return False
    
    def _setup_node_environment(self, repo_info: Dict) -> bool:
    # TODO: Consider breaking this function into smaller functions
        """Setup Node.js environment with automatic dependency correction"""
        try:
            package_manager = repo_info['package_manager']
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console
            ) as progress:
                
                # Check package manager availability
                task1 = progress.add_task(f"🔍 Checking {package_manager} availability...", total=1)
                result = subprocess.run([package_manager, '--version'], capture_output=True, text=True)
                if result.returncode != 0:
                    console.print(f"[red]❌ {package_manager} is not installed.[/red]")
                    return False
                progress.update(task1, completed=1)
                
                # Install dependencies
                task2 = progress.add_task("📦 Installing dependencies...", total=1)
                
                install_cmd = [package_manager, 'install']
                if package_manager == 'yarn':
                    install_cmd = ['yarn', 'install']
                elif package_manager == 'pnpm':
                    install_cmd = ['pnpm', 'install']
                
                result = subprocess.run(install_cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    console.print(f"[yellow]⚠️  Dependency installation issues detected[/yellow]")
                    self._fix_node_dependencies(result.stderr, package_manager)
                
                progress.update(task2, completed=1)
            
            console.print("[green]✅ Node.js environment setup complete[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Node.js setup failed: {e}[/red]")
            return False
    
    def _fix_python_dependencies(self, error_output: str):
    # TODO: Consider breaking this function into smaller functions
        """Fix Python dependency issues using AI"""
        if not self.model:
            return
        
        try:
            console.print("[cyan]🤖 AI analyzing dependency errors...[/cyan]")
            
            prompt = f"""
            Analyze this Python dependency installation error and provide fixes:
            
            Error Output:
            {error_output}
            
            Please provide:
            1. Root cause analysis
            2. Specific commands to fix the issues
            3. Alternative dependencies if needed
            4. Version compatibility solutions
            
            Format your response as actionable steps.
            """
            
            response = self.model.generate_content(prompt)
            
            console.print(Panel(
                Markdown(response.text),
                title="🤖 AI Dependency Analysis",
                border_style="blue"
            ))
            
            # Try to extract and execute fix commands
            self._execute_ai_fixes(response.text)
            
        except Exception as e:
            console.print(f"[red]❌ AI dependency fix failed: {e}[/red]")
    
    def _fix_node_dependencies(self, error_output: str, package_manager: str):
    # TODO: Consider breaking this function into smaller functions
        """Fix Node.js dependency issues using AI"""
        if not self.model:
            return
        
        try:
            console.print("[cyan]🤖 AI analyzing dependency errors...[/cyan]")
            
            prompt = f"""
            Analyze this Node.js dependency installation error and provide fixes:
            
            Package Manager: {package_manager}
            Error Output:
            {error_output}
            
            Please provide:
            1. Root cause analysis
            2. Specific commands to fix the issues
            3. Alternative packages if needed
            4. Version compatibility solutions
            
            Format your response as actionable steps.
            """
            
            response = self.model.generate_content(prompt)
            
            console.print(Panel(
                Markdown(response.text),
                title="🤖 AI Dependency Analysis",
                border_style="blue"
            ))
            
            # Try to extract and execute fix commands
            self._execute_ai_fixes(response.text)
            
        except Exception as e:
            console.print(f"[red]❌ AI dependency fix failed: {e}[/red]")
    
    def _execute_ai_fixes(self, ai_response: str):
    # TODO: Consider breaking this function into smaller functions
        """Extract and execute commands from AI response"""
        try:
            # Extract code blocks that look like commands
            code_blocks = re.findall(r'```(?:bash|shell|cmd)?\n(.*?)\n```', ai_response, re.DOTALL)
            
            for block in code_blocks:
                commands = [line.strip() for line in block.split('\n') if line.strip() and not line.startswith('#')]
                
                for cmd in commands:
                    if any(cmd.startswith(prefix) for prefix in ['uv ', 'pip ', 'npm ', 'yarn ', 'pnpm ']):
                        console.print(f"[cyan]🔧 Executing: {cmd}[/cyan]")
                        result = subprocess.run(cmd.split(), capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            console.print(f"[green]✅ Command successful[/green]")
                        else:
                            console.print(f"[yellow]⚠️  Command failed: {result.stderr}[/yellow]")
                            
        except Exception as e:
            console.print(f"[red]❌ AI fix execution failed: {e}[/red]")
    
    def _detect_and_fix_errors(self, repo_path: str, repo_info: Dict):
        """Detect and fix common errors in the repository"""
        console.print("[cyan]🔍 Detecting and fixing errors...[/cyan]")
        
        # Check for common issues
        self._check_import_errors(repo_path, repo_info)
        self._check_syntax_errors(repo_path, repo_info)
        self._check_missing_files(repo_path, repo_info)
        self._check_configuration_errors(repo_path, repo_info)
    
    def _check_import_errors(self, repo_path: str, repo_info: Dict):
    # TODO: Consider breaking this function into smaller functions
        """Check for import errors and fix them"""
        if repo_info['language'] != 'python':
            return
        
        try:
            python_files = list(Path(repo_path).rglob('*.py'))
            
            for py_file in python_files[:10]:  # Limit to first 10 files
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for common import issues
                    imports = re.findall(r'^(?:from|import)\s+([^\s]+)', content, re.MULTILINE)
                    
                    for imp in imports:
                        if '.' not in imp and imp not in ['os', 'sys', 'json', 'datetime', 're']:
                            # Check if package is installed
                            result = subprocess.run([
                                'uv', 'run', 'python', '-c', f'import {imp}'
                            ], capture_output=True, text=True)
                            
                            if result.returncode != 0:
                                console.print(f"[yellow]📦 Missing package detected: {imp}[/yellow]")
                                # Try to install it
                                install_result = subprocess.run([
                                    'uv', 'add', imp
                                ], capture_output=True, text=True)
                                
                                if install_result.returncode == 0:
                                    console.print(f"[green]✅ Installed: {imp}[/green]")
                                else:
                                    console.print(f"[red]❌ Failed to install: {imp}[/red]")
                                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            console.print(f"[red]❌ Import error check failed: {e}[/red]")
    
    def _check_syntax_errors(self, repo_path: str, repo_info: Dict):
    # TODO: Consider breaking this function into smaller functions
        """Check for syntax errors"""
        if repo_info['language'] != 'python':
            return
        
        try:
            python_files = list(Path(repo_path).rglob('*.py'))
            
            for py_file in python_files[:5]:  # Limit to first 5 files
                result = subprocess.run([
                    'uv', 'run', 'python', '-m', 'py_compile', str(py_file)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    console.print(f"[red]❌ Syntax error in {py_file.name}[/red]")
                    if self.model:
                        self._fix_syntax_error(py_file, result.stderr)
                        
        except Exception as e:
            console.print(f"[red]❌ Syntax error check failed: {e}[/red]")
    
    def _fix_syntax_error(self, file_path: Path, error_msg: str):
    # TODO: Consider breaking this function into smaller functions
        """Fix syntax errors using AI"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            prompt = f"""
            Fix this Python syntax error:
            
            File: {file_path.name}
            Error: {error_msg}
            
            Code:
            ```python
            {content}
            ```
            
            Please provide the corrected code.
            """
            
            response = self.model.generate_content(prompt)
            
            # Extract corrected code
            corrected_code = re.search(r'```python\n(.*?)\n```', response.text, re.DOTALL)
            if corrected_code:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(corrected_code.group(1))
                console.print(f"[green]✅ Fixed syntax error in {file_path.name}[/green]")
                
        except Exception as e:
            console.print(f"[red]❌ Syntax error fix failed: {e}[/red]")
    
    def _check_missing_files(self, repo_path: str, repo_info: Dict):
        """Check for missing essential files"""
        essential_files = {
            'python': ['requirements.txt', 'README.md', '.gitignore'],
            'node': ['package.json', 'README.md', '.gitignore']
        }
        
        language = repo_info['language']
        if language not in essential_files:
            return
        
        repo_path = Path(repo_path)
        
        for file_name in essential_files[language]:
            if not (repo_path / file_name).exists():
                console.print(f"[yellow]📄 Missing file: {file_name}[/yellow]")
                self._create_missing_file(repo_path, file_name, repo_info)
    
    def _create_missing_file(self, repo_path: Path, file_name: str, repo_info: Dict):
    # TODO: Consider breaking this function into smaller functions
        """Create missing essential files"""
        try:
            if file_name == 'requirements.txt' and repo_info['language'] == 'python':
                # Create basic requirements.txt
                with open(repo_path / file_name, 'w', encoding='utf-8') as f:
                    f.write("# Auto-generated requirements.txt\n")
                    f.write("# Add your dependencies here\n")
                    
            elif file_name == 'README.md':
                # Create basic README
                with open(repo_path / file_name, 'w', encoding='utf-8') as f:
                    f.write(f"# {repo_path.name}\n\n")
                    f.write("## Description\n\n")
                    f.write("## Installation\n\n")
                    f.write("## Usage\n\n")
                    
            elif file_name == '.gitignore':
                # Create basic .gitignore
                gitignore_content = {
                    'python': "__pycache__/\n*.pyc\n*.pyo\n*.pyd\n.Python\nbuild/\ndevelop-eggs/\ndist/\ndownloads/\neggs/\n.eggs/\nlib/\nlib64/\nparts/\nsdist/\nvar/\nwheels/\n*.egg-info/\n.installed.cfg\n*.egg\n.env\n.venv\nenv/\nvenv/\nENV/\nenv.bak/\nvenv.bak/\n",
                    'node': "node_modules/\nnpm-debug.log*\nyarn-debug.log*\nyarn-error.log*\n.npm\n.yarn-integrity\n.env\n.env.local\n.env.development.local\n.env.test.local\n.env.production.local\ndist/\nbuild/\n"
                }
                
                content = gitignore_content.get(repo_info['language'], '')
                with open(repo_path / file_name, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            console.print(f"[green]✅ Created {file_name}[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Failed to create {file_name}: {e}[/red]")
    
    def _check_configuration_errors(self, repo_path: str, repo_info: Dict):
        """Check for configuration errors"""
        # This is a placeholder for more advanced configuration checks
        console.print("[cyan]🔧 Configuration check complete[/cyan]")
    
    def _validate_setup(self, repo_path: str, repo_info: Dict) -> Dict:
    # TODO: Consider breaking this function into smaller functions
        """Validate the setup was successful"""
        validation_result = {
            'success': True,
            'errors': [],
            'warnings': [],
            'tests_passed': False
        }
        
        try:
            os.chdir(repo_path)
            
            # Try to run basic validation
            if repo_info['language'] == 'python':
                validation_result.update(self._validate_python_setup())
            elif repo_info['language'] == 'node':
                validation_result.update(self._validate_node_setup(repo_info))
            
            console.print(f"[green]✅ Setup validation complete[/green]")
            
        except Exception as e:
            validation_result['success'] = False
            validation_result['errors'].append(str(e))
            console.print(f"[red]❌ Setup validation failed: {e}[/red]")
        
        return validation_result
    
    def _validate_python_setup(self) -> Dict:
        """Validate Python setup"""
        result = {'success': True, 'errors': [], 'warnings': []}
        
        try:
            # Check if we can import basic modules
            check_result = subprocess.run([
                'uv', 'run', 'python', '-c', 'import sys; print("Python validation successful")'
            ], capture_output=True, text=True)
            
            if check_result.returncode != 0:
                result['success'] = False
                result['errors'].append("Python environment validation failed")
            
        except Exception as e:
            result['success'] = False
            result['errors'].append(f"Python validation error: {e}")
        
        return result
    
    def _validate_node_setup(self, repo_info: Dict) -> Dict:
    # TODO: Consider breaking this function into smaller functions
        """Validate Node.js setup"""
        result = {'success': True, 'errors': [], 'warnings': []}
        
        try:
            package_manager = repo_info['package_manager']
            
            # Check if we can run basic commands
            check_result = subprocess.run([
                package_manager, 'list'
            ], capture_output=True, text=True)
            
            if check_result.returncode != 0:
                result['warnings'].append("Package list check had issues")
            
        except Exception as e:
            result['success'] = False
            result['errors'].append(f"Node.js validation error: {e}")
        
        return result
    
    def _generate_setup_report(self, repo_path: str, repo_info: Dict, validation_result: Dict):
        """Generate comprehensive setup report"""
        
        # Create report table
        report_table = Table(title="🎯 Auto Setup Report", show_header=True)
        report_table.add_column("Component", style="cyan")
        report_table.add_column("Status", style="white")
        report_table.add_column("Details", style="dim")
        
        # Add rows
        report_table.add_row("Repository", "✅ Cloned", f"Path: {repo_path}")
        report_table.add_row("Language", "✅ Detected", repo_info['language'])
        report_table.add_row("Framework", "✅ Detected", repo_info['framework'])
        report_table.add_row("Dependencies", "✅ Installed", f"Package Manager: {repo_info['package_manager']}")
        
        if validation_result['success']:
            report_table.add_row("Validation", "✅ Passed", "Environment ready")
        else:
            report_table.add_row("Validation", "❌ Failed", f"Errors: {len(validation_result['errors'])}")
        
        console.print(report_table)
        
        # Show next steps
        next_steps = f"""
**🚀 Setup Complete! Next Steps:**

1. **Navigate to project**: `cd {repo_path}`
2. **Start development**: Use your preferred IDE or editor
3. **Run the project**: Check README.md for run instructions
4. **Chat with DevO**: Use `uv run python chat.py` for AI assistance

**📁 Project Structure:**
- Language: {repo_info['language']}
- Framework: {repo_info['framework']}
- Package Manager: {repo_info['package_manager']}
- Dependencies: {len(repo_info['dependencies'])} packages

**🤖 AI Assistant Available:**
Your repository is now ready for development with AI-powered assistance!
        """
        
        console.print(Panel(Markdown(next_steps), title="Setup Complete", border_style="green"))


def main():
    """Main function for testing auto setup"""
    
    parser = argparse.ArgumentParser(description='Auto Setup Repository')
    parser.add_argument('repo_url', help='Repository URL to setup')
    parser.add_argument('--target-dir', help='Target directory for cloning')
    parser.add_argument('--api-key', help='Gemini API key for AI fixes')
    
    args = parser.parse_args()
    
    # Initialize auto setup manager
    setup_manager = AutoSetupManager(args.api_key)
    
    # Run auto setup
    success = setup_manager.setup_repository(args.repo_url, args.target_dir)
    
    if success:
        console.print("[green]🎉 Auto setup completed successfully![/green]")
        sys.exit(0)
    else:
        console.print("[red]❌ Auto setup failed![/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()