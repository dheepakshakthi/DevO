#!/usr/bin/env python3
"""
RepoContainerizer - Standalone CLI Application
A self-contained, Warp-inspired command-line tool for AI-powered repository containerization.
"""

import os
import sys
import json
import tempfile
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
import re
import urllib.request
import urllib.parse
import zipfile
import platform
from datetime import datetime

# Optional imports with fallbacks
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Rich imports for beautiful CLI (with fallback)
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.syntax import Syntax
    from rich.prompt import Prompt, Confirm
    from rich.layout import Layout
    from rich.align import Align
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback console for systems without rich
    class Console:
        def print(self, *args, **kwargs):
            print(*args)
    
    class Panel:
        def __init__(self, content, **kwargs):
            self.content = content
        
        def __str__(self):
            return str(self.content)
    
    class Table:
        def __init__(self, **kwargs):
            self.rows = []
        
        def add_column(self, *args, **kwargs):
            pass
        
        def add_row(self, *args, **kwargs):
            self.rows.append(args)

# Initialize console
console = Console()

# Version and metadata
__version__ = "1.0.0"
__author__ = "RepoContainerizer Team"
__description__ = "AI-powered GitHub repository containerization tool"

class Config:
    """Application configuration"""
    
    def __init__(self):
        self.home_dir = Path.home() / ".repocontainerizer"
        self.config_file = self.home_dir / "config.json"
        self.cache_dir = self.home_dir / "cache"
        self.templates_dir = self.home_dir / "templates"
        self.logs_dir = self.home_dir / "logs"
        
        # Create directories
        for dir_path in [self.home_dir, self.cache_dir, self.templates_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.data = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default configuration
        return {
            "api_key": "",
            "default_output_dir": "./output",
            "default_format": "yaml",
            "validate_by_default": False,
            "theme": "auto",
            "last_updated": datetime.now().isoformat()
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            console.print(f"Warning: Could not save config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.data[key] = value
        self.save_config()

class Logger:
    """Simple logging system"""
    
    def __init__(self, config: Config):
        self.log_file = config.logs_dir / f"repocontainerizer_{datetime.now().strftime('%Y%m%d')}.log"
        self.verbose = False
    
    def log(self, level: str, message: str):
        """Log message to file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception:
            pass
        
        if self.verbose:
            console.print(f"[{level}] {message}")
    
    def info(self, message: str):
        self.log("INFO", message)
    
    def error(self, message: str):
        self.log("ERROR", message)
    
    def warning(self, message: str):
        self.log("WARNING", message)

class GitHubAPI:
    """Simple GitHub API client"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.base_url = "https://api.github.com"
    
    def get_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information"""
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
                return {
                    "name": data.get("name", ""),
                    "description": data.get("description", ""),
                    "language": data.get("language", ""),
                    "size": data.get("size", 0),
                    "stars": data.get("stargazers_count", 0),
                    "forks": data.get("forks_count", 0),
                    "topics": data.get("topics", [])
                }
        except Exception as e:
            self.logger.error(f"Failed to get repo info: {e}")
            return {}
    
    def download_repo(self, owner: str, repo: str, target_dir: str) -> bool:
        """Download repository as ZIP"""
        try:
            url = f"https://github.com/{owner}/{repo}/archive/main.zip"
            zip_path = Path(target_dir) / "repo.zip"
            
            # Download ZIP file
            urllib.request.urlretrieve(url, zip_path)
            
            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
            
            # Find extracted directory
            for item in Path(target_dir).iterdir():
                if item.is_dir() and item.name.startswith(f"{repo}-"):
                    # Move contents to target directory
                    for file in item.iterdir():
                        shutil.move(str(file), target_dir)
                    item.rmdir()
                    break
            
            # Clean up ZIP file
            zip_path.unlink()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download repo: {e}")
            return False

class RepositoryAnalyzer:
    """Analyze repository structure and generate containerization info"""
    
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.github = GitHubAPI(logger)
    
    def analyze_repo_url(self, repo_url: str) -> tuple[str, str]:
        """Extract owner and repo from GitHub URL"""
        # Handle different URL formats
        patterns = [
            r'github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
            r'github\.com/([^/]+)/([^/]+)/.*',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, repo_url)
            if match:
                return match.group(1), match.group(2)
        
        raise ValueError(f"Invalid GitHub URL: {repo_url}")
    
    def detect_language(self, repo_path: Path) -> str:
        """Detect primary programming language"""
        language_files = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'go': ['.go'],
            'php': ['.php'],
            'ruby': ['.rb'],
            'rust': ['.rs'],
            'cpp': ['.cpp', '.cc', '.cxx'],
            'c': ['.c'],
            'csharp': ['.cs']
        }
        
        file_counts = {}
        
        for file_path in repo_path.rglob("*"):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                suffix = file_path.suffix.lower()
                for lang, extensions in language_files.items():
                    if suffix in extensions:
                        file_counts[lang] = file_counts.get(lang, 0) + 1
        
        if not file_counts:
            return "unknown"
        
        return max(file_counts, key=file_counts.get)
    
    def detect_framework(self, repo_path: Path, language: str) -> str:
        """Detect framework based on files"""
        framework_indicators = {
            'python': {
                'django': ['manage.py', 'settings.py'],
                'flask': ['app.py', 'run.py'],
                'fastapi': ['main.py'],
            },
            'javascript': {
                'react': ['src/App.js', 'src/App.jsx', 'public/index.html'],
                'next': ['next.config.js', 'pages/'],
                'express': ['app.js', 'server.js'],
                'vue': ['vue.config.js', 'src/main.js'],
            },
            'java': {
                'spring': ['src/main/java/', 'pom.xml'],
                'maven': ['pom.xml'],
                'gradle': ['build.gradle'],
            },
            'go': {
                'gin': ['main.go'],
                'echo': ['main.go'],
            }
        }
        
        if language not in framework_indicators:
            return 'generic'
        
        for framework, indicators in framework_indicators[language].items():
            for indicator in indicators:
                if (repo_path / indicator).exists():
                    return framework
        
        return 'generic'
    
    def detect_dependencies(self, repo_path: Path) -> List[str]:
        """Detect dependencies from package files"""
        dependencies = []
        
        # Python dependencies
        requirements_file = repo_path / "requirements.txt"
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            dep = re.split(r'[>=<~!]', line)[0].strip()
                            dependencies.append(dep)
            except Exception:
                pass
        
        # Node.js dependencies
        package_json = repo_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    dev_deps = data.get('devDependencies', {})
                    dependencies.extend(list(deps.keys()))
                    dependencies.extend(list(dev_deps.keys()))
            except Exception:
                pass
        
        return dependencies
    
    def generate_dockerfile(self, language: str, framework: str, dependencies: List[str]) -> str:
        """Generate Dockerfile based on detected stack"""
        
        dockerfiles = {
            'python': {
                'django': '''FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
''',
                'flask': '''FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["python", "app.py"]
''',
                'generic': '''FROM python:3.9-slim

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
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
'''
            },
            'javascript': {
                'react': '''FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app
COPY --from=build /app/build /usr/share/nginx/html

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
''',
                'express': '''FROM node:18-alpine

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
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:3000/health || exit 1

# Run the application
CMD ["node", "server.js"]
''',
                'generic': '''FROM node:18-alpine

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
EXPOSE 3000

# Run the application
CMD ["node", "index.js"]
'''
            }
        }
        
        if language in dockerfiles and framework in dockerfiles[language]:
            return dockerfiles[language][framework]
        elif language in dockerfiles:
            return dockerfiles[language]['generic']
        else:
            return '''FROM alpine:latest

WORKDIR /app

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Run the application
CMD ["echo", "Please configure your application"]
'''
    
    def generate_docker_compose(self, language: str, framework: str) -> str:
        """Generate docker-compose.yml"""
        
        base_compose = '''version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
'''
        
        if language == 'python' and framework == 'django':
            return '''version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/mydb
      - DEBUG=False
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
'''
        
        return base_compose

class RepoContainerizer:
    """Main application class"""
    
    def __init__(self):
        self.config = Config()
        self.logger = Logger(self.config)
        self.analyzer = RepositoryAnalyzer(self.config, self.logger)
        
        # Setup API key
        self.api_key = self.config.get("api_key") or os.getenv("GEMINI_API_KEY")
    
    def display_banner(self):
        """Display application banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🚀 RepoContainerizer                      ║
║              AI-Powered Repository Containerization          ║
║                                                              ║
║  Transform any GitHub repository into a containerized       ║
║  application with zero configuration overhead.              ║
╚══════════════════════════════════════════════════════════════╝
"""
        
        if RICH_AVAILABLE:
            console.print(Panel(banner, border_style="blue", padding=(1, 2)))
        else:
            print(banner)
    
    def display_help(self):
        """Display help information"""
        help_text = f"""
USAGE:
    repocontainerizer <command> [options]

COMMANDS:
    containerize <repo_url>     Containerize a GitHub repository
    config                      Manage configuration
    validate <dockerfile>       Validate a Dockerfile
    setup                       Setup and configure the tool
    version                     Show version information
    help                        Show this help message

OPTIONS:
    --output, -o <dir>         Output directory (default: ./output)
    --format, -f <fmt>         Config format: yaml|json (default: yaml)
    --validate                 Validate container after generation
    --verbose, -v              Verbose output
    --api-key <key>            Gemini API key (overrides config)

EXAMPLES:
    repocontainerizer containerize https://github.com/owner/repo
    repocontainerizer containerize https://github.com/owner/repo -o ./containers --validate
    repocontainerizer config set api_key your_api_key_here
    repocontainerizer setup

DEPENDENCIES:
    Core: Python 3.8+ (built-in modules only)
    Enhanced: pip install pyyaml rich requests
    Optional: Docker (for validation)

STATUS:
    YAML support: {"✅ Available" if YAML_AVAILABLE else "❌ Not available (will use JSON)"}
    Rich output: {"✅ Available" if RICH_AVAILABLE else "❌ Not available (basic output)"}
    Requests: {"✅ Available" if REQUESTS_AVAILABLE else "❌ Not available (using urllib)"}

For more information, visit: https://github.com/your-username/repocontainerizer
"""
        console.print(help_text)
    
    def setup_interactive(self):
        """Interactive setup process"""
        self.display_banner()
        console.print("\n🔧 Welcome to RepoContainerizer Setup!\n")
        
        # API Key setup
        current_key = self.config.get("api_key", "")
        if current_key:
            console.print(f"✅ API key is already configured (ends with: ...{current_key[-4:]})")
            if RICH_AVAILABLE:
                update_key = Confirm.ask("Would you like to update it?")
            else:
                update_key = input("Would you like to update it? (y/N): ").lower().startswith('y')
        else:
            update_key = True
        
        if update_key:
            if RICH_AVAILABLE:
                api_key = Prompt.ask("Enter your Gemini API key", password=True)
            else:
                api_key = input("Enter your Gemini API key: ")
            
            if api_key:
                self.config.set("api_key", api_key)
                console.print("✅ API key saved!")
        
        # Default settings
        console.print("\n⚙️  Configure default settings:")
        
        current_output = self.config.get("default_output_dir", "./output")
        if RICH_AVAILABLE:
            output_dir = Prompt.ask("Default output directory", default=current_output)
        else:
            output_dir = input(f"Default output directory [{current_output}]: ") or current_output
        
        self.config.set("default_output_dir", output_dir)
        
        current_format = self.config.get("default_format", "yaml")
        if RICH_AVAILABLE:
            format_choice = Prompt.ask("Default config format", choices=["yaml", "json"], default=current_format)
        else:
            format_choice = input(f"Default config format (yaml/json) [{current_format}]: ") or current_format
        
        self.config.set("default_format", format_choice)
        
        # Validation
        current_validate = self.config.get("validate_by_default", False)
        if RICH_AVAILABLE:
            validate_default = Confirm.ask("Validate containers by default?", default=current_validate)
        else:
            validate_default = input(f"Validate containers by default? (y/N) [{current_validate}]: ").lower().startswith('y')
        
        self.config.set("validate_by_default", validate_default)
        
        console.print("\n✅ Setup complete!")
        console.print(f"📁 Configuration saved to: {self.config.config_file}")
        console.print(f"📝 Logs will be saved to: {self.logger.log_file}")
        
        console.print("\n🎯 You're ready to containerize repositories!")
        console.print("Try: repocontainerizer containerize https://github.com/owner/repo")
    
    def containerize_repo(self, repo_url: str, output_dir: str = None, format_type: str = None, validate: bool = False):
        """Containerize a GitHub repository"""
        try:
            # Setup
            output_dir = output_dir or self.config.get("default_output_dir", "./output")
            format_type = format_type or self.config.get("default_format", "yaml")
            validate = validate or self.config.get("validate_by_default", False)
            
            self.logger.info(f"Starting containerization of {repo_url}")
            
            # Parse repository URL
            owner, repo_name = self.analyzer.analyze_repo_url(repo_url)
            console.print(f"📦 Repository: {owner}/{repo_name}")
            
            # Get repository info
            repo_info = self.analyzer.github.get_repo_info(owner, repo_name)
            if repo_info:
                console.print(f"📋 Description: {repo_info.get('description', 'No description')}")
                console.print(f"⭐ Stars: {repo_info.get('stars', 0)}")
                console.print(f"🍴 Forks: {repo_info.get('forks', 0)}")
                if repo_info.get('language'):
                    console.print(f"💻 Primary Language: {repo_info['language']}")
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Download repository
                console.print("📥 Downloading repository...")
                if not self.analyzer.github.download_repo(owner, repo_name, temp_dir):
                    raise Exception("Failed to download repository")
                
                # Analyze repository
                console.print("🔍 Analyzing repository structure...")
                language = self.analyzer.detect_language(temp_path)
                framework = self.analyzer.detect_framework(temp_path, language)
                dependencies = self.analyzer.detect_dependencies(temp_path)
                
                console.print(f"🎯 Detected language: {language}")
                console.print(f"🛠️  Detected framework: {framework}")
                console.print(f"📦 Dependencies found: {len(dependencies)}")
                
                # Generate containerization files
                console.print("🐳 Generating containerization files...")
                
                # Create output directory
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                
                # Generate Dockerfile
                dockerfile_content = self.analyzer.generate_dockerfile(language, framework, dependencies)
                dockerfile_path = output_path / "Dockerfile"
                with open(dockerfile_path, 'w') as f:
                    f.write(dockerfile_content)
                
                # Generate docker-compose.yml
                compose_content = self.analyzer.generate_docker_compose(language, framework)
                compose_path = output_path / "docker-compose.yml"
                with open(compose_path, 'w') as f:
                    f.write(compose_content)
                
                # Generate configuration file
                config_data = {
                    "repository": {
                        "url": repo_url,
                        "owner": owner,
                        "name": repo_name,
                        "info": repo_info
                    },
                    "analysis": {
                        "language": language,
                        "framework": framework,
                        "dependencies": dependencies[:20]  # Limit to first 20
                    },
                    "containerization": {
                        "image_name": f"{repo_name.lower()}-app",
                        "ports": ["8080:8080"],
                        "environment": {
                            "NODE_ENV": "production" if language == "javascript" else "PRODUCTION",
                            "PORT": "8080"
                        },
                        "volumes": ["./logs:/app/logs"],
                        "health_check": {
                            "test": "curl -f http://localhost:8080/health || exit 1",
                            "interval": "30s",
                            "timeout": "10s",
                            "retries": 3
                        }
                    },
                    "commands": {
                        "build": "docker build -t {image_name} .",
                        "run": "docker run -p 8080:8080 {image_name}",
                        "compose": "docker-compose up -d"
                    }
                }
                
                # Save configuration
                config_filename = f"container-config.{format_type}"
                config_path = output_path / config_filename
                
                if format_type == "json" or not YAML_AVAILABLE:
                    with open(config_path, 'w') as f:
                        json.dump(config_data, f, indent=2)
                    if format_type == "yaml" and not YAML_AVAILABLE:
                        console.print("⚠️  YAML not available, using JSON format instead")
                        config_filename = "container-config.json"
                        config_path = output_path / config_filename
                else:
                    with open(config_path, 'w') as f:
                        yaml.dump(config_data, f, default_flow_style=False, indent=2)
                
                # Generate README
                readme_content = f"""# {repo_name} - Containerization

## Quick Start

### Using Docker
```bash
# Build the image
docker build -t {repo_name.lower()}-app .

# Run the container
docker run -p 8080:8080 {repo_name.lower()}-app
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

## Repository Information
- **Repository**: {owner}/{repo_name}
- **Language**: {language}
- **Framework**: {framework}
- **Dependencies**: {len(dependencies)} packages

## Configuration
See `{config_filename}` for detailed configuration options.

## Health Check
The container includes a health check endpoint at `/health`.

---
*Generated by RepoContainerizer v{__version__}*
"""
                
                readme_path = output_path / "README.md"
                with open(readme_path, 'w') as f:
                    f.write(readme_content)
                
                # Validate container (optional)
                if validate:
                    console.print("🔍 Validating container...")
                    if self.validate_dockerfile(str(dockerfile_path)):
                        console.print("✅ Container validation successful!")
                    else:
                        console.print("⚠️  Container validation failed (check logs)")
                
                # Success message
                console.print("\n" + "="*60)
                console.print("🎉 Containerization Complete!")
                console.print("="*60)
                
                # Display results table
                if RICH_AVAILABLE:
                    table = Table(title="Analysis Results")
                    table.add_column("Property", style="cyan")
                    table.add_column("Value", style="magenta")
                    
                    table.add_row("Repository", f"{owner}/{repo_name}")
                    table.add_row("Language", language)
                    table.add_row("Framework", framework)
                    table.add_row("Dependencies", str(len(dependencies)))
                    table.add_row("Output Directory", str(output_path))
                    
                    console.print(table)
                else:
                    console.print(f"Repository: {owner}/{repo_name}")
                    console.print(f"Language: {language}")
                    console.print(f"Framework: {framework}")
                    console.print(f"Dependencies: {len(dependencies)}")
                    console.print(f"Output Directory: {output_path}")
                
                # Display generated files
                console.print("\n📁 Generated Files:")
                generated_files = [dockerfile_path, compose_path, config_path, readme_path]
                for file_path in generated_files:
                    console.print(f"  📄 {file_path}")
                
                # Next steps
                console.print(f"\n🎯 Next Steps:")
                console.print(f"1. Navigate to output directory: cd {output_path}")
                console.print(f"2. Build the container: docker build -t {repo_name.lower()}-app .")
                console.print(f"3. Run the container: docker run -p 8080:8080 {repo_name.lower()}-app")
                console.print(f"4. Or use docker-compose: docker-compose up -d")
                
                self.logger.info(f"Containerization completed successfully for {repo_url}")
                
        except Exception as e:
            error_msg = f"Error containerizing repository: {str(e)}"
            self.logger.error(error_msg)
            console.print(f"❌ {error_msg}")
            return False
        
        return True
    
    def validate_dockerfile(self, dockerfile_path: str) -> bool:
        """Validate Dockerfile by attempting to build it"""
        try:
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
                ["docker", "build", "-t", "repocontainerizer-test", "-f", dockerfile_path, "."],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=os.path.dirname(dockerfile_path)
            )
            
            if build_result.returncode == 0:
                # Clean up test image
                subprocess.run(
                    ["docker", "rmi", "repocontainerizer-test"],
                    capture_output=True,
                    text=True
                )
                return True
            else:
                self.logger.error(f"Docker build failed: {build_result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Docker build timed out")
            return False
        except Exception as e:
            self.logger.error(f"Error validating Dockerfile: {str(e)}")
            return False
    
    def manage_config(self, args: List[str]):
        """Manage configuration"""
        if not args:
            # Show current configuration
            console.print("📋 Current Configuration:")
            for key, value in self.config.data.items():
                if key == "api_key" and value:
                    console.print(f"  {key}: ...{value[-4:]}")
                else:
                    console.print(f"  {key}: {value}")
            return
        
        command = args[0]
        
        if command == "set" and len(args) >= 3:
            key, value = args[1], args[2]
            # Handle boolean values
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            self.config.set(key, value)
            console.print(f"✅ Configuration updated: {key} = {value}")
        
        elif command == "get" and len(args) >= 2:
            key = args[1]
            value = self.config.get(key)
            if key == "api_key" and value:
                console.print(f"{key}: ...{value[-4:]}")
            else:
                console.print(f"{key}: {value}")
        
        elif command == "reset":
            self.config.data = self.config.load_config()
            console.print("✅ Configuration reset to defaults")
        
        else:
            console.print("Usage: config [set <key> <value> | get <key> | reset]")
    
    def run(self, args: List[str]):
        """Main entry point"""
        if not args:
            self.display_help()
            return
        
        command = args[0]
        
        # Set verbose mode
        if "--verbose" in args or "-v" in args:
            self.logger.verbose = True
        
        # Parse API key override
        if "--api-key" in args:
            idx = args.index("--api-key")
            if idx + 1 < len(args):
                self.api_key = args[idx + 1]
        
        if command == "containerize":
            if len(args) < 2:
                console.print("❌ Repository URL required")
                console.print("Usage: containerize <repo_url> [options]")
                return
            
            repo_url = args[1]
            
            # Parse options
            output_dir = None
            format_type = None
            validate = False
            
            for i, arg in enumerate(args):
                if arg in ["--output", "-o"] and i + 1 < len(args):
                    output_dir = args[i + 1]
                elif arg in ["--format", "-f"] and i + 1 < len(args):
                    format_type = args[i + 1]
                elif arg == "--validate":
                    validate = True
            
            self.containerize_repo(repo_url, output_dir, format_type, validate)
        
        elif command == "config":
            self.manage_config(args[1:])
        
        elif command == "validate":
            if len(args) < 2:
                console.print("❌ Dockerfile path required")
                console.print("Usage: validate <dockerfile_path>")
                return
            
            dockerfile_path = args[1]
            if self.validate_dockerfile(dockerfile_path):
                console.print("✅ Dockerfile validation successful!")
            else:
                console.print("❌ Dockerfile validation failed!")
        
        elif command == "setup":
            self.setup_interactive()
        
        elif command == "version":
            console.print(f"RepoContainerizer v{__version__}")
            console.print(f"Author: {__author__}")
            console.print(f"Description: {__description__}")
        
        elif command == "help":
            self.display_help()
        
        else:
            console.print(f"❌ Unknown command: {command}")
            self.display_help()

def main():
    """Main entry point for the standalone application"""
    app = RepoContainerizer()
    
    # Handle no arguments
    if len(sys.argv) == 1:
        app.display_banner()
        app.display_help()
        return
    
    # Run the application
    app.run(sys.argv[1:])

if __name__ == "__main__":
    main()
