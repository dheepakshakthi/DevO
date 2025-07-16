#!/usr/bin/env python3
"""
RepoContainerizer - LLM-powered GitHub Repository Containerization Tool

A sophisticated CLI tool that automates the process of understanding and 
containerizing GitHub repositories using AI analysis.
"""

import os
import sys
import json
import yaml
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import base64
from datetime import datetime
import re

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
import git
import google.generativeai as genai
from google.generativeai import types

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, continue without it
    pass

# Import utility functions
from utils import (
    detect_language_from_files, detect_framework_from_files, detect_package_manager,
    detect_database_requirements, detect_port_from_files, detect_environment_variables,
    detect_build_tools, generate_health_check_command, generate_run_commands,
    extract_dependencies
)
from templates import get_dockerfile_template, get_docker_compose_template

# Initialize Rich console
console = Console()

@dataclass
class RepositoryAnalysis:
    """Data class to store repository analysis results"""
    primary_language: str
    framework: str
    package_manager: str
    database: str
    external_services: List[str]
    dependencies: List[str]
    build_tools: List[str]
    port: int
    environment_vars: Dict[str, str]
    commands: Dict[str, str]
    dockerfile_content: str
    docker_compose_content: str
    health_check: str

@dataclass
class ContainerConfig:
    """Data class for container configuration"""
    image_name: str
    ports: List[str]
    environment_variables: Dict[str, str]
    volumes: List[str]
    commands: Dict[str, str]
    health_check: Dict[str, str]

class RepoContainerizer:
    """Main class for repository containerization"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
        self.model = "gemini-2.0-flash-exp"
        self.temp_dir = None
        
    def clone_repository(self, repo_url: str) -> str:
        """Clone a GitHub repository to a temporary directory"""
        try:
            self.temp_dir = tempfile.mkdtemp()
            console.print(f"🔄 Cloning repository: {repo_url}")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Cloning repository...", total=None)
                git.Repo.clone_from(repo_url, self.temp_dir)
                progress.update(task, completed=True)
            
            console.print(f"✅ Repository cloned to: {self.temp_dir}")
            return self.temp_dir
            
        except Exception as e:
            console.print(f"❌ Error cloning repository: {str(e)}")
            raise
    
    def analyze_repository_structure(self, repo_path: str) -> Dict:
        """Analyze the repository structure and files"""
        structure = {
            "files": [],
            "directories": [],
            "config_files": [],
            "dependencies": [],
            "languages": {}
        }
        
        # Known configuration files
        config_files = {
            "package.json": "Node.js",
            "requirements.txt": "Python",
            "Pipfile": "Python",
            "pyproject.toml": "Python",
            "Cargo.toml": "Rust",
            "go.mod": "Go",
            "pom.xml": "Java",
            "build.gradle": "Java",
            "composer.json": "PHP",
            "Gemfile": "Ruby",
            "Dockerfile": "Docker",
            "docker-compose.yml": "Docker Compose",
            "docker-compose.yaml": "Docker Compose",
            ".env": "Environment",
            "README.md": "Documentation",
            "README.rst": "Documentation"
        }
        
        # Walk through repository
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common build directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'target', 'build', 'dist']]
            
            rel_root = os.path.relpath(root, repo_path)
            if rel_root != ".":
                structure["directories"].append(rel_root)
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                rel_path = os.path.join(rel_root, file) if rel_root != "." else file
                structure["files"].append(rel_path)
                
                # Check for configuration files
                if file in config_files:
                    structure["config_files"].append({
                        "file": rel_path,
                        "type": config_files[file]
                    })
                
                # Analyze file extensions for language detection
                ext = os.path.splitext(file)[1].lower()
                if ext:
                    structure["languages"][ext] = structure["languages"].get(ext, 0) + 1
        
        return structure
    
    def read_important_files(self, repo_path: str, structure: Dict) -> Dict[str, str]:
        """Read content of important files for analysis"""
        important_files = {}
        
        # Files to read for analysis
        files_to_read = [
            "package.json", "requirements.txt", "Pipfile", "pyproject.toml",
            "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "composer.json",
            "Gemfile", "README.md", "README.rst", ".env.example", "Dockerfile",
            "docker-compose.yml", "docker-compose.yaml"
        ]
        
        for config_file in structure["config_files"]:
            file_path = os.path.join(repo_path, config_file["file"])
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        important_files[config_file["file"]] = f.read()
                except Exception as e:
                    console.print(f"⚠️  Warning: Could not read {config_file['file']}: {str(e)}")
        
        # Also read main application files
        main_files = []
        for file in structure["files"]:
            if any(file.endswith(ext) for ext in ['.py', '.js', '.ts', '.go', '.rs', '.java', '.php', '.rb']):
                if any(name in file.lower() for name in ['main', 'app', 'server', 'index']):
                    main_files.append(file)
        
        # Read up to 3 main files
        for main_file in main_files[:3]:
            file_path = os.path.join(repo_path, main_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Truncate if too long
                    if len(content) > 10000:
                        content = content[:10000] + "\n... (truncated)"
                    important_files[main_file] = content
            except Exception as e:
                console.print(f"⚠️  Warning: Could not read {main_file}: {str(e)}")
        
        return important_files
    
    def analyze_with_llm(self, repo_url: str, structure: Dict, file_contents: Dict[str, str]) -> RepositoryAnalysis:
        """Use LLM to analyze repository and generate containerization info"""
        console.print("🤖 Analyzing repository with AI...")
        
        # Pre-analyze with utility functions
        language_counts = detect_language_from_files(structure['files'])
        primary_language = max(language_counts, key=language_counts.get) if language_counts else "unknown"
        
        framework = detect_framework_from_files(structure['files'], file_contents)
        package_manager = detect_package_manager(structure['files'])
        databases = detect_database_requirements(file_contents)
        port = detect_port_from_files(file_contents)
        env_vars = detect_environment_variables(file_contents)
        build_tools = detect_build_tools(structure['files'], file_contents)
        dependencies = extract_dependencies(file_contents)
        
        # Generate base templates
        dockerfile_template = get_dockerfile_template(primary_language, framework)
        if not dockerfile_template:
            dockerfile_template = get_dockerfile_template(primary_language, "generic")
        
        # Determine docker-compose template
        if databases:
            if 'postgresql' in databases:
                compose_template = get_docker_compose_template("python_postgresql")
            elif 'redis' in databases:
                compose_template = get_docker_compose_template("node_redis")
            else:
                compose_template = get_docker_compose_template("generic")
        else:
            compose_template = get_docker_compose_template("generic")
        
        # Generate commands
        commands = generate_run_commands(primary_language, framework, package_manager)
        health_check = generate_health_check_command(primary_language, framework, port)
        
        # Prepare analysis prompt for LLM refinement
        analysis_prompt = f"""
        Analyze this GitHub repository and refine the containerization details:

        Repository URL: {repo_url}
        
        Pre-Analysis Results:
        - Primary Language: {primary_language}
        - Framework: {framework}
        - Package Manager: {package_manager}
        - Databases: {databases}
        - Port: {port}
        - Build Tools: {build_tools}
        - Dependencies: {dependencies[:10]}  # Show first 10 dependencies
        
        Repository Structure:
        - Files: {len(structure['files'])} files
        - Directories: {structure['directories']}
        - Languages detected: {language_counts}
        - Config files: {[cf['file'] for cf in structure['config_files']]}
        
        Important File Contents:
        {json.dumps(file_contents, indent=2)}
        
        Based on this analysis, provide a JSON response with refined containerization details:
        {{
            "primary_language": "{primary_language}",
            "framework": "{framework}",
            "package_manager": "{package_manager}",
            "database": "{databases[0] if databases else 'none'}",
            "external_services": {json.dumps(databases[1:] if len(databases) > 1 else [])},
            "dependencies": {json.dumps(dependencies)},
            "build_tools": {json.dumps(build_tools)},
            "port": {port},
            "environment_vars": {json.dumps(env_vars)},
            "commands": {json.dumps(commands)},
            "dockerfile_content": "complete optimized Dockerfile content",
            "docker_compose_content": "complete docker-compose.yml content",
            "health_check": "{health_check}"
        }}
        
        Please refine and optimize the Dockerfile and docker-compose.yml content based on:
        1. Security best practices (non-root user, minimal base image)
        2. Multi-stage builds where appropriate
        3. Proper layer caching optimization
        4. Framework-specific optimizations
        5. Database integration if needed
        6. Health check configuration
        7. Environment variable handling
        
        Base Dockerfile template to refine:
        {dockerfile_template}
        
        Base docker-compose template to refine:
        {compose_template}
        """
        
        try:
            # Generate content using the current API
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction="""You are an expert DevOps engineer specializing in containerization. 
                Refine and optimize Docker configurations with security best practices, performance optimizations, 
                and framework-specific improvements. Always generate production-ready configurations.
                
                IMPORTANT: You must respond with valid JSON only. Do not include any markdown formatting, 
                code blocks, or explanatory text. Just return the raw JSON object."""
            )
            
            response = model.generate_content(analysis_prompt)
            
            # Clean up the response text (remove markdown formatting if present)
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove ```
            response_text = response_text.strip()
            
            # Try to parse JSON
            try:
                analysis_data = json.loads(response_text)
                return RepositoryAnalysis(**analysis_data)
            except json.JSONDecodeError as json_error:
                console.print(f"⚠️  Invalid JSON response from LLM: {str(json_error)}")
                console.print(f"📝 Response was: {response_text[:200]}...")
                raise json_error
                
        except Exception as e:
            console.print(f"⚠️  LLM analysis failed, using fallback analysis: {str(e)}")
            # Fallback to utility-based analysis
            return RepositoryAnalysis(
                primary_language=primary_language,
                framework=framework,
                package_manager=package_manager,
                database=databases[0] if databases else "none",
                external_services=databases[1:] if len(databases) > 1 else [],
                dependencies=dependencies,
                build_tools=build_tools,
                port=port,
                environment_vars=env_vars,
                commands=commands,
                dockerfile_content=dockerfile_template or self._generate_fallback_dockerfile(primary_language, framework),
                docker_compose_content=compose_template,
                health_check=health_check
            )
    
    def generate_config_file(self, analysis: RepositoryAnalysis, format: str = "yaml") -> str:
        """Generate unified configuration file"""
        config = {
            "containerization": {
                "image_name": f"{analysis.primary_language.lower()}-app",
                "ports": [f"{analysis.port}:8080"],
                "environment_variables": analysis.environment_vars,
                "commands": analysis.commands,
                "health_check": {
                    "test": analysis.health_check,
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                }
            },
            "analysis": {
                "primary_language": analysis.primary_language,
                "framework": analysis.framework,
                "package_manager": analysis.package_manager,
                "database": analysis.database,
                "external_services": analysis.external_services,
                "dependencies": analysis.dependencies,
                "build_tools": analysis.build_tools
            }
        }
        
        if format == "yaml":
            return yaml.dump(config, default_flow_style=False, indent=2)
        else:
            return json.dumps(config, indent=2)
    
    def create_output_files(self, analysis: RepositoryAnalysis, output_dir: str, config_format: str = "yaml"):
        """Create all output files in the specified directory"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create Dockerfile
        dockerfile_path = output_path / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(analysis.dockerfile_content)
        
        # Create docker-compose.yml
        compose_path = output_path / "docker-compose.yml"
        with open(compose_path, 'w') as f:
            f.write(analysis.docker_compose_content)
        
        # Create config file
        config_content = self.generate_config_file(analysis, config_format)
        config_ext = "yml" if config_format == "yaml" else "json"
        config_path = output_path / f"container-config.{config_ext}"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        # Create .env.example
        env_path = output_path / ".env.example"
        with open(env_path, 'w') as f:
            f.write("# Environment variables for containerization\n")
            for key, description in analysis.environment_vars.items():
                f.write(f"{key}=  # {description}\n")
        
        # Create README with instructions
        readme_path = output_path / "CONTAINERIZATION_README.md"
        with open(readme_path, 'w') as f:
            f.write(self.generate_readme(analysis))
        
        console.print(f"✅ Output files created in: {output_dir}")
        return [dockerfile_path, compose_path, config_path, env_path, readme_path]
    
    def generate_readme(self, analysis: RepositoryAnalysis) -> str:
        """Generate README with containerization instructions"""
        return f"""# Containerization Guide

## Repository Analysis
- **Primary Language**: {analysis.primary_language}
- **Framework**: {analysis.framework}
- **Package Manager**: {analysis.package_manager}
- **Database**: {analysis.database}
- **External Services**: {', '.join(analysis.external_services)}

## Quick Start

### Using Docker
```bash
# Build the image
docker build -t {analysis.primary_language.lower()}-app .

# Run the container
docker run -p {analysis.port}:8080 {analysis.primary_language.lower()}-app
```

### Using Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Environment Variables
{chr(10).join(f"- `{key}`: {desc}" for key, desc in analysis.environment_vars.items())}

## Commands
- **Install**: `{analysis.commands.get('install', 'N/A')}`
- **Build**: `{analysis.commands.get('build', 'N/A')}`
- **Start**: `{analysis.commands.get('start', 'N/A')}`
- **Test**: `{analysis.commands.get('test', 'N/A')}`

## Health Check
The container includes a health check: `{analysis.health_check}`

## Dependencies
{chr(10).join(f"- {dep}" for dep in analysis.dependencies)}

## Build Tools
{chr(10).join(f"- {tool}" for tool in analysis.build_tools)}

---
*Generated by RepoContainerizer*
"""
    
    def validate_container(self, dockerfile_path: str) -> bool:
        """Validate the generated Dockerfile by building it"""
        try:
            console.print("🔍 Validating container build...")
            
            # Check if Docker is available
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                console.print("⚠️  Docker not found. Skipping validation.")
                return False
            
            # Build the Docker image
            build_result = subprocess.run(
                ["docker", "build", "-t", "repo-containerizer-test", "-f", dockerfile_path, "."],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=os.path.dirname(dockerfile_path)
            )
            
            if build_result.returncode == 0:
                console.print("✅ Container build successful!")
                
                # Clean up test image
                subprocess.run(
                    ["docker", "rmi", "repo-containerizer-test"],
                    capture_output=True,
                    text=True
                )
                
                return True
            else:
                console.print(f"❌ Container build failed:\n{build_result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            console.print("❌ Container build timed out")
            return False
        except Exception as e:
            console.print(f"❌ Error validating container: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up temporary files with Windows-compatible error handling"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                # Try normal cleanup first
                shutil.rmtree(self.temp_dir)
                console.print("🧹 Cleaned up temporary files")
            except PermissionError:
                # Windows-specific cleanup for locked Git files
                try:
                    self._force_remove_directory(self.temp_dir)
                    console.print("🧹 Cleaned up temporary files (forced)")
                except Exception as e:
                    console.print(f"⚠️  Warning: Could not fully clean up temporary files: {str(e)}")
                    console.print(f"📁 Temporary directory: {self.temp_dir}")
            except Exception as e:
                console.print(f"⚠️  Warning: Could not clean up temporary files: {str(e)}")
                console.print(f"📁 Temporary directory: {self.temp_dir}")
    
    def _force_remove_directory(self, path: str):
        """Force remove directory on Windows by handling file permissions"""
        import stat
        
        def handle_remove_readonly(func, path, exc):
            """Handle removal of readonly files on Windows"""
            if os.path.exists(path):
                # Make the file writable and try again
                os.chmod(path, stat.S_IWRITE)
                func(path)
        
        # Use onerror parameter to handle permission issues
        shutil.rmtree(path, onerror=handle_remove_readonly)
    
    def _generate_fallback_dockerfile(self, language: str, framework: str) -> str:
        """Generate a basic Dockerfile as fallback"""
        if language.lower() == "python":
            return '''FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]
'''
        elif language.lower() == "javascript":
            return '''FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1000 appuser && adduser -u 1000 -G appuser -s /bin/sh -D appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Run the application
CMD ["node", "index.js"]
'''
        else:
            return '''FROM alpine:latest

WORKDIR /app

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Run the application
CMD ["echo", "Please configure the application start command"]
'''

# CLI Implementation
@click.group()
@click.version_option(version="1.0.0")
def cli():
    """🚀 RepoContainerizer - AI-Powered GitHub Repository Containerization Tool
    
    Automatically analyze and containerize GitHub repositories using AI.
    """
    pass

@cli.command()
@click.argument('repo_url')
@click.option('--output', '-o', default='./output', help='Output directory for generated files')
@click.option('--format', '-f', type=click.Choice(['yaml', 'json']), default='yaml', help='Config file format')
@click.option('--validate', is_flag=True, help='Validate container by building it')
@click.option('--api-key', envvar='GEMINI_API_KEY', help='Gemini API key (or set GEMINI_API_KEY env var)')
def containerize(repo_url, output, format, validate, api_key):
    """Containerize a GitHub repository"""
    
    if not api_key:
        console.print("❌ API key required. Set GEMINI_API_KEY environment variable or use --api-key option.")
        sys.exit(1)
    
    # Display banner
    console.print(Panel.fit(
        "[bold blue]🚀 RepoContainerizer[/bold blue]\n"
        "[dim]AI-Powered GitHub Repository Containerization[/dim]",
        border_style="blue"
    ))
    
    containerizer = RepoContainerizer(api_key)
    
    try:
        # Step 1: Clone repository
        repo_path = containerizer.clone_repository(repo_url)
        
        # Step 2: Analyze repository structure
        console.print("📊 Analyzing repository structure...")
        structure = containerizer.analyze_repository_structure(repo_path)
        
        # Step 3: Read important files
        console.print("📖 Reading important files...")
        file_contents = containerizer.read_important_files(repo_path, structure)
        
        # Step 4: Analyze with LLM
        analysis = containerizer.analyze_with_llm(repo_url, structure, file_contents)
        
        # Step 5: Generate output files
        console.print("📝 Generating containerization files...")
        output_files = containerizer.create_output_files(analysis, output, format)
        
        # Step 6: Validate container (optional)
        if validate:
            containerizer.validate_container(str(output_files[0]))  # Dockerfile path
        
        # Display results
        console.print("\n" + "="*60)
        console.print("[bold green]✅ Containerization Complete![/bold green]")
        console.print("="*60)
        
        # Create results table
        table = Table(title="Analysis Results")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Primary Language", analysis.primary_language)
        table.add_row("Framework", analysis.framework)
        table.add_row("Package Manager", analysis.package_manager)
        table.add_row("Database", analysis.database)
        table.add_row("Port", str(analysis.port))
        
        console.print(table)
        
        # Show generated files
        console.print("\n[bold]Generated Files:[/bold]")
        for file_path in output_files:
            console.print(f"  📄 {file_path}")
        
        console.print(f"\n[bold]Next Steps:[/bold]")
        console.print(f"1. Navigate to the output directory: [cyan]cd {output}[/cyan]")
        console.print(f"2. Build the container: [cyan]docker build -t my-app .[/cyan]")
        console.print(f"3. Run the container: [cyan]docker run -p {analysis.port}:{analysis.port} my-app[/cyan]")
        
    except Exception as e:
        console.print(f"❌ Error: {str(e)}")
        sys.exit(1)
    finally:
        containerizer.cleanup()

@cli.command()
@click.argument('dockerfile_path')
def validate(dockerfile_path):
    """Validate a generated Dockerfile"""
    console.print(f"🔍 Validating Dockerfile: {dockerfile_path}")
    
    containerizer = RepoContainerizer("")  # No API key needed for validation
    success = containerizer.validate_container(dockerfile_path)
    
    if success:
        console.print("✅ Dockerfile validation successful!")
    else:
        console.print("❌ Dockerfile validation failed!")
        sys.exit(1)

@cli.command()
def setup():
    """Set up environment and dependencies"""
    console.print("🔧 Setting up RepoContainerizer...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        console.print("❌ Python 3.8+ required")
        sys.exit(1)
    
    # Check for required tools
    tools = ["git", "docker"]
    missing_tools = []
    
    for tool in tools:
        try:
            result = subprocess.run([tool, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                console.print(f"✅ {tool} is installed")
            else:
                missing_tools.append(tool)
        except FileNotFoundError:
            missing_tools.append(tool)
    
    if missing_tools:
        console.print(f"❌ Missing tools: {', '.join(missing_tools)}")
        console.print("Please install the missing tools and run setup again.")
        sys.exit(1)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        console.print("⚠️  GEMINI_API_KEY environment variable not set")
        console.print("Please set your Gemini API key:")
        console.print("  export GEMINI_API_KEY=your_api_key_here")
    else:
        console.print("✅ GEMINI_API_KEY is configured")
    
    console.print("\n🎉 Setup complete! Ready to containerize repositories.")

@cli.command()
@click.argument('repo_path')
@click.option('--api-key', envvar='GEMINI_API_KEY', help='Gemini API key (or set GEMINI_API_KEY env var)')
@click.option('--output', '-o', default='./suggestions', help='Output directory for suggestions')
@click.option('--language', '-l', help='Programming language filter')
@click.option('--focus', '-f', type=click.Choice(['security', 'performance', 'maintainability', 'all']), 
              default='all', help='Focus area for suggestions')
def suggest(repo_path, api_key, output, language, focus):
    """Get AI-powered code suggestions for a repository"""
    
    if not api_key:
        console.print("❌ API key required. Set GEMINI_API_KEY environment variable or use --api-key option.")
        sys.exit(1)
    
    console.print(Panel.fit(
        "[bold blue]🤖 AI Code Suggestions[/bold blue]\n"
        "[dim]Analyzing code and providing improvement suggestions[/dim]",
        border_style="blue"
    ))
    
    try:
        suggester = CodeSuggester(api_key)
        suggestions = suggester.analyze_and_suggest(repo_path, language, focus)
        
        # Create output directory
        os.makedirs(output, exist_ok=True)
        
        # Save suggestions to file
        suggestions_file = os.path.join(output, 'code_suggestions.md')
        with open(suggestions_file, 'w', encoding='utf-8') as f:
            f.write(suggestions)
        
        console.print(f"✅ Code suggestions saved to: {suggestions_file}")
        
        # Display summary
        console.print("\n[bold]Suggestion Summary:[/bold]")
        console.print(f"📁 Repository: {repo_path}")
        console.print(f"🎯 Focus: {focus}")
        console.print(f"💾 Output: {suggestions_file}")
        
    except Exception as e:
        console.print(f"❌ Error generating suggestions: {str(e)}")
        sys.exit(1)

@cli.command()
@click.argument('repo_path')
@click.option('--api-key', envvar='GEMINI_API_KEY', help='Gemini API key (or set GEMINI_API_KEY env var)')
@click.option('--output', '-o', default='./dependency_report', help='Output directory for reports')
@click.option('--fix', '-f', is_flag=True, help='Automatically fix detected issues')
@click.option('--format', type=click.Choice(['markdown', 'json', 'yaml']), default='markdown', 
              help='Report format')
def check_deps(repo_path, api_key, output, fix, format):
    """Check and report missing dependencies"""
    
    if not api_key:
        console.print("❌ API key required. Set GEMINI_API_KEY environment variable or use --api-key option.")
        sys.exit(1)
    
    console.print(Panel.fit(
        "[bold blue]🔍 Dependency Analysis[/bold blue]\n"
        "[dim]Checking for missing dependencies and compatibility issues[/dim]",
        border_style="blue"
    ))
    
    try:
        checker = DependencyChecker(api_key)
        report = checker.analyze_dependencies(repo_path)
        
        # Create output directory
        os.makedirs(output, exist_ok=True)
        
        # Save report
        if format == 'markdown':
            report_file = os.path.join(output, 'dependency_report.md')
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report['markdown'])
        elif format == 'json':
            report_file = os.path.join(output, 'dependency_report.json')
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report['data'], f, indent=2)
        else:  # yaml
            report_file = os.path.join(output, 'dependency_report.yaml')
            with open(report_file, 'w', encoding='utf-8') as f:
                yaml.dump(report['data'], f, default_flow_style=False)
        
        console.print(f"✅ Dependency report saved to: {report_file}")
        
        # Display summary
        missing_count = len(report['data'].get('missing_dependencies', []))
        outdated_count = len(report['data'].get('outdated_dependencies', []))
        conflicts_count = len(report['data'].get('conflicts', []))
        
        table = Table(title="Dependency Analysis Summary")
        table.add_column("Issue Type", style="cyan")
        table.add_column("Count", style="magenta")
        table.add_column("Status", style="green")
        
        table.add_row("Missing Dependencies", str(missing_count), 
                     "🔴 Critical" if missing_count > 0 else "✅ OK")
        table.add_row("Outdated Dependencies", str(outdated_count), 
                     "🟡 Warning" if outdated_count > 0 else "✅ OK")
        table.add_row("Conflicts", str(conflicts_count), 
                     "🔴 Critical" if conflicts_count > 0 else "✅ OK")
        
        console.print(table)
        
        # Auto-fix if requested
        if fix and (missing_count > 0 or outdated_count > 0):
            console.print("\n🔧 Auto-fixing detected issues...")
            fixer = DependencyFixer(api_key)
            fix_result = fixer.fix_dependencies(repo_path, report['data'])
            
            if fix_result['success']:
                console.print("✅ Dependencies fixed successfully!")
                console.print(f"📝 Fix summary: {fix_result['summary']}")
            else:
                console.print(f"❌ Failed to fix dependencies: {fix_result['error']}")
        
    except Exception as e:
        console.print(f"❌ Error checking dependencies: {str(e)}")
        sys.exit(1)

@cli.command()
@click.argument('repo_path')
@click.option('--api-key', envvar='GEMINI_API_KEY', help='Gemini API key (or set GEMINI_API_KEY env var)')
@click.option('--output', '-o', default='./fix_report', help='Output directory for fix reports')
@click.option('--dry-run', is_flag=True, help='Show what would be fixed without making changes')
@click.option('--backup', is_flag=True, default=True, help='Create backup before fixing')
def fix_code(repo_path, api_key, output, dry_run, backup):
    """Automatically fix common code issues using AI"""
    
    if not api_key:
        console.print("❌ API key required. Set GEMINI_API_KEY environment variable or use --api-key option.")
        sys.exit(1)
    
    console.print(Panel.fit(
        "[bold blue]🔧 AI Code Fixer[/bold blue]\n"
        "[dim]Automatically fixing common code issues[/dim]",
        border_style="blue"
    ))
    
    try:
        fixer = CodeFixer(api_key)
        
        if dry_run:
            console.print("🔍 Dry run mode - no changes will be made")
            issues = fixer.scan_issues(repo_path)
            
            console.print(f"\n[bold]Issues found:[/bold]")
            for issue in issues:
                console.print(f"  🔴 {issue['file']}: {issue['description']}")
                console.print(f"     💡 Suggested fix: {issue['fix']}")
        else:
            # Create backup if requested
            if backup:
                backup_path = f"{repo_path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copytree(repo_path, backup_path)
                console.print(f"📦 Backup created: {backup_path}")
            
            # Fix issues
            fix_result = fixer.fix_issues(repo_path)
            
            # Create output directory and save report
            os.makedirs(output, exist_ok=True)
            report_file = os.path.join(output, 'fix_report.md')
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(fix_result['report'])
            
            console.print(f"✅ Fix report saved to: {report_file}")
            console.print(f"🔧 Fixed {fix_result['fixed_count']} issues")
            
            if fix_result['failed_fixes']:
                console.print(f"⚠️  {len(fix_result['failed_fixes'])} issues could not be fixed automatically")
        
    except Exception as e:
        console.print(f"❌ Error fixing code: {str(e)}")
        sys.exit(1)

@cli.command()
@click.argument('repo_path')
@click.option('--api-key', envvar='GEMINI_API_KEY', help='Gemini API key (or set GEMINI_API_KEY env var)')
@click.option('--output', '-o', default='./analysis_report', help='Output directory for analysis report')
@click.option('--include-suggestions', is_flag=True, help='Include code suggestions in report')
@click.option('--include-dependencies', is_flag=True, help='Include dependency analysis in report')
@click.option('--include-security', is_flag=True, help='Include security analysis in report')
def analyze(repo_path, api_key, output, include_suggestions, include_dependencies, include_security):
    """Comprehensive AI-powered repository analysis"""
    
    if not api_key:
        console.print("❌ API key required. Set GEMINI_API_KEY environment variable or use --api-key option.")
        sys.exit(1)
    
    console.print(Panel.fit(
        "[bold blue]🔬 Comprehensive Analysis[/bold blue]\n"
        "[dim]AI-powered repository analysis with suggestions and fixes[/dim]",
        border_style="blue"
    ))
    
    try:
        analyzer = ComprehensiveAnalyzer(api_key)
        
        with Progress() as progress:
            task = progress.add_task("Analyzing repository...", total=100)
            
            # Basic analysis
            progress.update(task, advance=20)
            basic_analysis = analyzer.basic_analysis(repo_path)
            
            # Code suggestions
            if include_suggestions:
                progress.update(task, advance=20)
                suggestions = analyzer.get_suggestions(repo_path)
            else:
                suggestions = None
            
            # Dependency analysis
            if include_dependencies:
                progress.update(task, advance=20)
                dependencies = analyzer.check_dependencies(repo_path)
            else:
                dependencies = None
            
            # Security analysis
            if include_security:
                progress.update(task, advance=20)
                security = analyzer.security_analysis(repo_path)
            else:
                security = None
            
            # Generate comprehensive report
            progress.update(task, advance=20)
            report = analyzer.generate_report(
                basic_analysis, suggestions, dependencies, security
            )
        
        # Create output directory and save report
        os.makedirs(output, exist_ok=True)
        report_file = os.path.join(output, 'comprehensive_analysis.md')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        console.print(f"✅ Comprehensive analysis saved to: {report_file}")
        
        # Display summary
        console.print("\n[bold]Analysis Summary:[/bold]")
        console.print(f"📁 Repository: {repo_path}")
        console.print(f"📊 Basic Analysis: ✅ Complete")
        console.print(f"💡 Code Suggestions: {'✅ Included' if include_suggestions else '❌ Skipped'}")
        console.print(f"📦 Dependencies: {'✅ Included' if include_dependencies else '❌ Skipped'}")
        console.print(f"🔒 Security: {'✅ Included' if include_security else '❌ Skipped'}")
        console.print(f"📄 Report: {report_file}")
        
    except Exception as e:
        console.print(f"❌ Error during analysis: {str(e)}")
        sys.exit(1)

class CodeSuggester:
    """AI-powered code suggestion generator"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
        self.model = "gemini-2.0-flash-exp"
    
    def analyze_and_suggest(self, repo_path: str, language: str = None, focus: str = "all") -> str:
        """Analyze code and generate suggestions"""
        try:
            # Scan repository for code files
            code_files = self._scan_code_files(repo_path, language)
            
            # Analyze each file and generate suggestions
            suggestions = []
            
            for file_path in code_files[:10]:  # Limit to first 10 files
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    file_suggestions = self._analyze_file(file_path, content, focus)
                    if file_suggestions:
                        suggestions.append(file_suggestions)
                        
                except Exception as e:
                    console.print(f"⚠️  Could not analyze {file_path}: {str(e)}")
            
            # Generate comprehensive report
            return self._generate_suggestions_report(suggestions, repo_path, focus)
            
        except Exception as e:
            console.print(f"❌ Error analyzing code: {str(e)}")
            return f"# Code Analysis Error\n\nFailed to analyze repository: {str(e)}"
    
    def _scan_code_files(self, repo_path: str, language: str = None) -> List[str]:
        """Scan repository for code files"""
        extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'go': ['.go'],
            'rust': ['.rs'],
            'cpp': ['.cpp', '.cc', '.cxx', '.c++'],
            'c': ['.c', '.h'],
            'csharp': ['.cs'],
            'php': ['.php'],
            'ruby': ['.rb'],
            'swift': ['.swift'],
            'kotlin': ['.kt'],
            'scala': ['.scala']
        }
        
        if language:
            target_extensions = extensions.get(language.lower(), [])
        else:
            target_extensions = [ext for exts in extensions.values() for ext in exts]
        
        code_files = []
        for root, dirs, files in os.walk(repo_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
            
            for file in files:
                if any(file.endswith(ext) for ext in target_extensions):
                    code_files.append(os.path.join(root, file))
        
        return code_files
    
    def _analyze_file(self, file_path: str, content: str, focus: str) -> Dict:
        """Analyze a single file and generate suggestions"""
        try:
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=f"""You are an expert code reviewer. Analyze the provided code and give specific, actionable suggestions.

Focus areas: {focus}

For each suggestion, provide:
1. Issue description
2. Severity (low, medium, high, critical)
3. Specific code location
4. Recommended fix with code example
5. Explanation of why this improves the code

Be concise but thorough. Focus on practical improvements."""
            )
            
            prompt = f"""
Analyze this code file and provide improvement suggestions:

File: {file_path}

```
{content[:5000]}  # Limit content to avoid token limits
```

Please provide structured suggestions focusing on {focus} improvements.
"""
            
            response = model.generate_content(prompt)
            
            return {
                'file': file_path,
                'content': content[:200] + '...' if len(content) > 200 else content,
                'suggestions': response.text
            }
            
        except Exception as e:
            console.print(f"⚠️  Could not analyze {file_path}: {str(e)}")
            return None
    
    def _generate_suggestions_report(self, suggestions: List[Dict], repo_path: str, focus: str) -> str:
        """Generate a comprehensive suggestions report"""
        report = f"""# Code Suggestions Report

**Repository:** {repo_path}
**Focus:** {focus}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

Analyzed {len(suggestions)} files and generated improvement suggestions.

## File Analysis

"""
        
        for suggestion in suggestions:
            report += f"""
### {suggestion['file']}

{suggestion['suggestions']}

---

"""
        
        report += """
## Recommendations

1. **Review all critical and high severity issues first**
2. **Test changes in a development environment**
3. **Consider implementing automated linting/formatting**
4. **Regular code reviews can prevent many of these issues**

## Next Steps

1. Prioritize fixes based on severity
2. Create feature branches for each fix
3. Test thoroughly before merging
4. Update documentation as needed

---
*Generated by DevO AI Code Suggestions*
"""
        
        return report

@cli.command()
@click.option('--repo-path', '-r', help='Path to repository for analysis')
@click.option('--api-key', envvar='GEMINI_API_KEY', help='Gemini API key (or set GEMINI_API_KEY env var)')
@click.option('--save-session', is_flag=True, help='Save chat session to file')
def chat(repo_path, api_key, save_session):
    """Start interactive chat with DevO AI assistant"""
    
    if not api_key:
        console.print("❌ API key required. Set GEMINI_API_KEY environment variable or use --api-key option.")
        sys.exit(1)
    
    from chat import DevOChatSession
    
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
        import traceback
        traceback.print_exc()
    finally:
        # Save session if requested
        if save_session:
            session.save_session()


if __name__ == "__main__":
    cli()