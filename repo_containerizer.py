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

if __name__ == "__main__":
    cli()
