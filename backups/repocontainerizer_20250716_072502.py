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

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, continue without it
    pass

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
    
    def detect_build_commands(self, repo_path: Path, language: str, framework: str) -> Dict[str, List[str]]:
        """Detect build and setup commands for the repository"""
        commands = {
            "setup": [],
            "build": [],
            "run": [],
            "test": [],
            "install": []
        }
        
        # Python projects
        if language == "python":
            # Check for uv package manager first
            has_uv_lock = (repo_path / "uv.lock").exists()
            has_pyproject = (repo_path / "pyproject.toml").exists()
            has_requirements = (repo_path / "requirements.txt").exists()
            
            # Prioritize uv if lock file exists or pyproject.toml is present
            if has_uv_lock or (has_pyproject and not has_requirements):
                commands["install"].append("uv sync")
                commands["setup"].append("uv venv")  # Create virtual environment
                if has_pyproject:
                    commands["install"].append("uv pip install -e .")
            elif has_requirements:
                # Check if we should use uv with requirements.txt
                commands["install"].append("uv pip install -r requirements.txt")
            elif has_pyproject:
                commands["install"].append("uv pip install .")
            elif (repo_path / "setup.py").exists():
                commands["install"].append("uv pip install -e .")
            else:
                # Fallback to pip if no package manager is detected
                if has_requirements:
                    commands["install"].append("pip install -r requirements.txt")
                elif has_pyproject:
                    commands["install"].append("pip install .")
                elif (repo_path / "setup.py").exists():
                    commands["install"].append("pip install -e .")
            
            # Framework-specific commands
            if framework == "django":
                commands["setup"].extend([
                    "python manage.py migrate",
                    "python manage.py collectstatic --noinput"
                ])
                commands["run"].append("python manage.py runserver 0.0.0.0:8000")
                commands["test"].append("python manage.py test")
            elif framework == "flask":
                commands["run"].append("python app.py")
                commands["test"].append("python -m pytest")
            elif framework == "fastapi":
                commands["run"].append("uvicorn main:app --host 0.0.0.0 --port 8000")
                commands["test"].append("python -m pytest")
            else:
                # Generic Python
                main_files = ["main.py", "app.py", "run.py", "server.py"]
                for main_file in main_files:
                    if (repo_path / main_file).exists():
                        commands["run"].append(f"python {main_file}")
                        break
                commands["test"].append("python -m pytest")
        
        # JavaScript/Node.js projects
        elif language == "javascript":
            # Check for package.json
            package_json = repo_path / "package.json"
            if package_json.exists():
                commands["install"].append("npm install")
                
                try:
                    with open(package_json, 'r') as f:
                        package_data = json.load(f)
                        scripts = package_data.get('scripts', {})
                        
                        # Common script mappings
                        if 'start' in scripts:
                            commands["run"].append("npm start")
                        if 'dev' in scripts:
                            commands["run"].append("npm run dev")
                        if 'build' in scripts:
                            commands["build"].append("npm run build")
                        if 'test' in scripts:
                            commands["test"].append("npm test")
                        
                        # Framework-specific
                        if framework == "react":
                            if 'build' not in scripts:
                                commands["build"].append("npm run build")
                            if 'start' not in scripts:
                                commands["run"].append("npm start")
                        elif framework == "next":
                            commands["build"].append("npm run build")
                            commands["run"].append("npm run start")
                        elif framework == "express":
                            if 'start' not in scripts:
                                commands["run"].append("node server.js")
                        
                except Exception:
                    # Fallback commands
                    commands["build"].append("npm run build")
                    commands["run"].append("npm start")
                    commands["test"].append("npm test")
        
        # Java projects
        elif language == "java":
            if (repo_path / "pom.xml").exists():
                commands["install"].append("mvn clean install")
                commands["build"].append("mvn package")
                commands["run"].append("mvn spring-boot:run")
                commands["test"].append("mvn test")
            elif (repo_path / "build.gradle").exists():
                commands["install"].append("./gradlew build")
                commands["build"].append("./gradlew assemble")
                commands["run"].append("./gradlew bootRun")
                commands["test"].append("./gradlew test")
        
        # Go projects
        elif language == "go":
            if (repo_path / "go.mod").exists():
                commands["install"].append("go mod download")
                commands["build"].append("go build -o app .")
                commands["run"].append("./app")
                commands["test"].append("go test ./...")
            else:
                commands["install"].append("go get ./...")
                commands["build"].append("go build -o app .")
                commands["run"].append("./app")
                commands["test"].append("go test ./...")
        
        # Rust projects
        elif language == "rust":
            if (repo_path / "Cargo.toml").exists():
                commands["build"].append("cargo build --release")
                commands["run"].append("cargo run")
                commands["test"].append("cargo test")
        
        # PHP projects
        elif language == "php":
            if (repo_path / "composer.json").exists():
                commands["install"].append("composer install")
                commands["test"].append("./vendor/bin/phpunit")
            commands["run"].append("php -S localhost:8000")
        
        # Ruby projects
        elif language == "ruby":
            if (repo_path / "Gemfile").exists():
                commands["install"].append("bundle install")
                commands["run"].append("bundle exec rails server")
                commands["test"].append("bundle exec rspec")
        
        # C/C++ projects
        elif language in ["c", "cpp"]:
            if (repo_path / "CMakeLists.txt").exists():
                commands["setup"].extend([
                    "mkdir -p build",
                    "cd build"
                ])
                commands["build"].extend([
                    "cmake ..",
                    "make"
                ])
                commands["run"].append("./main")
            elif (repo_path / "Makefile").exists():
                commands["build"].append("make")
                commands["run"].append("./main")
        
        # Remove empty commands
        return {k: v for k, v in commands.items() if v}
    
    def generate_dockerfile(self, language: str, framework: str, dependencies: List[str]) -> str:
        """Generate Dockerfile based on detected stack"""
        
        # Check if we should use uv (this will be called from containerize_repo with repo context)
        use_uv = hasattr(self, '_use_uv') and self._use_uv
        
        if language == 'python':
            if framework == 'django':
                if use_uv:
                    return '''FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock* requirements.txt* ./

# Install dependencies
RUN if [ -f "uv.lock" ]; then uv sync --frozen; elif [ -f "pyproject.toml" ]; then uv pip install .; elif [ -f "requirements.txt" ]; then uv pip install -r requirements.txt; fi

# Copy application code
COPY . .

# Collect static files
RUN uv run python manage.py collectstatic --noinput

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
'''
                else:
                    return '''FROM python:3.9-slim

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
'''
            
            elif framework == 'flask':
                if use_uv:
                    return '''FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock* requirements.txt* ./

# Install dependencies
RUN if [ -f "uv.lock" ]; then uv sync --frozen; elif [ -f "pyproject.toml" ]; then uv pip install .; elif [ -f "requirements.txt" ]; then uv pip install -r requirements.txt; fi

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
CMD ["uv", "run", "python", "app.py"]
'''
                else:
                    return '''FROM python:3.9-slim

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
'''
            
            elif framework == 'fastapi':
                if use_uv:
                    return '''FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock* requirements.txt* ./

# Install dependencies
RUN if [ -f "uv.lock" ]; then uv sync --frozen; elif [ -f "pyproject.toml" ]; then uv pip install .; elif [ -f "requirements.txt" ]; then uv pip install -r requirements.txt; fi

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
                else:
                    return '''FROM python:3.9-slim

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
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
            
            else:  # generic python
                if use_uv:
                    return '''FROM python:3.9-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock* requirements.txt* ./

# Install dependencies
RUN if [ -f "uv.lock" ]; then uv sync --frozen; elif [ -f "pyproject.toml" ]; then uv pip install .; elif [ -f "requirements.txt" ]; then uv pip install -r requirements.txt; fi

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "python", "main.py"]
'''
                else:
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
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
'''
        
        elif language == 'javascript':
            if framework == 'react':
                return '''FROM node:18-alpine AS build

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
'''
            elif framework == 'express':
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
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:3000/health || exit 1

# Run the application
CMD ["node", "server.js"]
'''
            else:  # generic javascript
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
EXPOSE 3000

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


def print_colored_text(text: str, color: str):
    """Print colored text to console. Fallback for systems without rich/colorama."""
    # Color codes for terminal output
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    
    if color in colors:
        print(f"{colors[color]}{text}{colors['reset']}")
    else:
        print(text)


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
    auto-setup <repo_url>       Automatically analyze and setup a repository
    config                      Manage configuration
    validate <dockerfile>       Validate a Dockerfile
    setup                       Setup and configure the tool
    version                     Show version information
    help                        Show this help message

OPTIONS:
    --output, -o <dir>         Output directory (default: ./output)
    --format, -f <fmt>         Config format: yaml|json (default: yaml)
    --validate                 Validate container after generation
    --execute, -e              Execute generated setup script (auto-setup only)
    --verbose, -v              Verbose output
    --api-key <key>            Gemini API key (overrides config)

EXAMPLES:
    repocontainerizer containerize https://github.com/owner/repo
    repocontainerizer containerize https://github.com/owner/repo -o ./containers --validate
    repocontainerizer auto-setup https://github.com/owner/repo
    repocontainerizer auto-setup https://github.com/owner/repo --execute
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
                
                # Check if uv should be used
                use_uv = (temp_path / "uv.lock").exists() or (
                    language == "python" and 
                    (temp_path / "pyproject.toml").exists() and 
                    not (temp_path / "requirements.txt").exists()
                )
                self.analyzer._use_uv = use_uv
                
                if use_uv:
                    console.print("📦 Detected uv package manager - using uv for Python dependencies")
                
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
        
        elif command == "auto-setup":
            if len(args) < 2:
                console.print("❌ Repository URL required")
                console.print("Usage: auto-setup <repo_url> [options]")
                return
            
            repo_url = args[1]
            
            # Parse options
            output_dir = None
            execute = False
            
            for i, arg in enumerate(args):
                if arg in ["--output", "-o"] and i + 1 < len(args):
                    output_dir = args[i + 1]
                elif arg in ["--execute", "-e"]:
                    execute = True
            
            self.auto_setup_repo(repo_url, output_dir, execute)
        
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
    
    def auto_setup_repo(self, repo_url: str, output_dir: str = None, execute: bool = False):
        """Automatically analyze and setup a repository with appropriate commands"""
        try:
            # Setup
            output_dir = output_dir or self.config.get("default_output_dir", "./output")
            
            self.logger.info(f"Starting auto-setup for {repo_url}")
            
            # Parse repository URL
            owner, repo_name = self.analyzer.analyze_repo_url(repo_url)
            console.print(f"🔍 Analyzing repository: {owner}/{repo_name}")
            
            # Get repository info
            repo_info = self.analyzer.github.get_repo_info(owner, repo_name)
            if repo_info:
                console.print(f"📋 Description: {repo_info.get('description', 'No description available')}")
                console.print(f"⭐ Stars: {repo_info.get('stars', 0)}")
                if repo_info.get('language'):
                    console.print(f"💻 GitHub detected language: {repo_info['language']}")
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Download repository
                console.print("📥 Downloading repository...")
                if not self.analyzer.github.download_repo(owner, repo_name, temp_dir):
                    raise Exception("Failed to download repository")
                
                # Analyze repository structure
                console.print("🔍 Analyzing repository structure...")
                language = self.analyzer.detect_language(temp_path)
                framework = self.analyzer.detect_framework(temp_path, language)
                dependencies = self.analyzer.detect_dependencies(temp_path)
                
                # Check if uv should be used
                use_uv = (temp_path / "uv.lock").exists() or (
                    language == "python" and 
                    (temp_path / "pyproject.toml").exists() and 
                    not (temp_path / "requirements.txt").exists()
                )
                self.analyzer._use_uv = use_uv
                
                # Detect build commands
                console.print("🛠️  Detecting build and setup commands...")
                commands = self.analyzer.detect_build_commands(temp_path, language, framework)
                
                if use_uv:
                    console.print("📦 Detected uv package manager - using uv for Python dependencies")
                
                # Display analysis results
                console.print("\n" + "="*60)
                console.print("📊 REPOSITORY ANALYSIS RESULTS")
                console.print("="*60)
                
                if RICH_AVAILABLE:
                    # Create analysis table
                    table = Table(title="Repository Analysis")
                    table.add_column("Property", style="cyan", width=20)
                    table.add_column("Value", style="magenta")
                    
                    table.add_row("Repository", f"{owner}/{repo_name}")
                    table.add_row("Language", language.title())
                    table.add_row("Framework", framework.title())
                    table.add_row("Dependencies", str(len(dependencies)))
                    table.add_row("Commands Found", str(len([cmd for cmds in commands.values() for cmd in cmds])))
                    
                    console.print(table)
                    
                    # Commands table
                    if commands:
                        cmd_table = Table(title="Detected Commands")
                        cmd_table.add_column("Phase", style="green", width=15)
                        cmd_table.add_column("Commands", style="yellow")
                        
                        for phase, cmds in commands.items():
                            if cmds:
                                cmd_table.add_row(phase.title(), "\n".join(cmds))
                        
                        console.print(cmd_table)
                else:
                    console.print(f"Repository: {owner}/{repo_name}")
                    console.print(f"Language: {language.title()}")
                    console.print(f"Framework: {framework.title()}")
                    console.print(f"Dependencies: {len(dependencies)}")
                    console.print(f"Commands Found: {len([cmd for cmds in commands.values() for cmd in cmds])}")
                    
                    # Show commands
                    if commands:
                        console.print("\n🛠️  Detected Commands:")
                        for phase, cmds in commands.items():
                            if cmds:
                                console.print(f"\n{phase.title()}:")
                                for cmd in cmds:
                                    console.print(f"  • {cmd}")
                
                # Create output directory
                output_path = Path(output_dir) / f"{repo_name}-setup"
                output_path.mkdir(parents=True, exist_ok=True)
                
                # Generate setup script
                console.print(f"\n📝 Generating setup script...")
                script_content = self.generate_setup_script(temp_path, language, framework, commands, use_uv)
                
                # Determine script filename
                is_windows = platform.system() == "Windows"
                script_filename = f"setup{'.bat' if is_windows else '.sh'}"
                script_path = output_path / script_filename
                
                with open(script_path, 'w') as f:
                    f.write(script_content)
                
                # Make script executable on Unix systems
                if not is_windows:
                    os.chmod(script_path, 0o755)
                
                # Generate detailed analysis report
                analysis_report = {
                    "repository": {
                        "url": repo_url,
                        "owner": owner,
                        "name": repo_name,
                        "info": repo_info,
                        "analysis_date": datetime.now().isoformat()
                    },
                    "detected_stack": {
                        "language": language,
                        "framework": framework,
                        "dependencies": dependencies[:50]  # Limit to first 50
                    },
                    "setup_commands": commands,
                    "recommendations": self.generate_recommendations(language, framework, commands, temp_path),
                    "containerization": {
                        "dockerfile_available": (temp_path / "Dockerfile").exists(),
                        "docker_compose_available": (temp_path / "docker-compose.yml").exists(),
                        "recommended_ports": self.get_recommended_ports(language, framework),
                        "environment_variables": self.get_recommended_env_vars(language, framework)
                    }
                }
                
                # Save analysis report
                report_path = output_path / "analysis-report.json"
                with open(report_path, 'w') as f:
                    json.dump(analysis_report, f, indent=2)
                
                # Generate README with setup instructions
                readme_content = self.generate_setup_readme(repo_name, owner, language, framework, commands, dependencies)
                readme_path = output_path / "SETUP_README.md"
                with open(readme_path, 'w') as f:
                    f.write(readme_content)
                
                # Execute setup script if requested
                if execute:
                    console.print(f"\n🚀 Executing setup script...")
                    if self.execute_setup_script(script_path, temp_path):
                        console.print("✅ Setup script executed successfully!")
                    else:
                        console.print("⚠️  Setup script execution completed with warnings (check logs)")
                
                # Display results
                console.print("\n" + "="*60)
                console.print("✅ AUTO-SETUP COMPLETED")
                console.print("="*60)
                
                console.print(f"\n📁 Generated Files:")
                console.print(f"  📄 Setup Script: {script_path}")
                console.print(f"  📄 Analysis Report: {report_path}")
                console.print(f"  📄 Setup README: {readme_path}")
                
                console.print(f"\n🎯 Next Steps:")
                console.print(f"1. Navigate to: cd {output_path}")
                console.print(f"2. Run setup script: ./{script_filename}")
                console.print(f"3. Follow instructions in SETUP_README.md")
                console.print(f"4. Containerize: python repocontainerizer.py containerize {repo_url}")
                
                self.logger.info(f"Auto-setup completed successfully for {repo_url}")
                
        except Exception as e:
            error_msg = f"Error in auto-setup: {str(e)}"
            self.logger.error(error_msg)
            console.print(f"❌ {error_msg}")
            return False
    
    def generate_recommendations(self, language: str, framework: str, commands: Dict[str, List[str]], repo_path: Path) -> List[str]:
        """Generate recommendations for the repository"""
        recommendations = []
        
        # Check for missing files
        if language == "python":
            if not (repo_path / "requirements.txt").exists() and not (repo_path / "pyproject.toml").exists():
                recommendations.append("Consider adding requirements.txt or pyproject.toml for dependency management")
            
            if not (repo_path / "README.md").exists():
                recommendations.append("Add a README.md file with project description and setup instructions")
            
            if framework == "django" and not (repo_path / "manage.py").exists():
                recommendations.append("This appears to be a Django project but manage.py is missing")
        
        elif language == "javascript":
            if not (repo_path / "package.json").exists():
                recommendations.append("Consider adding package.json for dependency management")
            
            if framework == "react" and not (repo_path / "public").exists():
                recommendations.append("React projects typically need a public directory")
        
        # Security recommendations
        if (repo_path / ".env").exists():
            recommendations.append("Found .env file - ensure it's in .gitignore and not committed to version control")
        
        # Docker recommendations
        if not (repo_path / "Dockerfile").exists():
            recommendations.append("Consider adding a Dockerfile for containerization")
        
        # Testing recommendations
        if "test" not in commands:
            recommendations.append("No test commands detected - consider adding automated tests")
        
        return recommendations
    
    def get_recommended_ports(self, language: str, framework: str) -> List[str]:
        """Get recommended ports for containerization"""
        port_map = {
            "python": {
                "django": ["8000"],
                "flask": ["5000"],
                "fastapi": ["8000"]
            },
            "javascript": {
                "react": ["3000", "80"],
                "express": ["3000"],
                "next": ["3000"]
            },
            "java": {
                "spring": ["8080"]
            }
        }
        
        if language in port_map and framework in port_map[language]:
            return port_map[language][framework]
        
        return ["8080"]  # Default port
    
    def get_recommended_env_vars(self, language: str, framework: str) -> Dict[str, str]:
        """Get recommended environment variables"""
        env_vars = {"NODE_ENV": "production"}
        
        if language == "python":
            env_vars["PYTHONUNBUFFERED"] = "1"
            if framework == "django":
                env_vars["DJANGO_SETTINGS_MODULE"] = "myproject.settings"
        elif language == "javascript":
            if framework == "next":
                env_vars["NEXT_TELEMETRY_DISABLED"] = "1"
        
        return env_vars
    
    def generate_setup_readme(self, repo_name: str, owner: str, language: str, framework: str, commands: Dict[str, List[str]], dependencies: List[str]) -> str:
        """Generate a comprehensive setup README"""
        return f"""# {repo_name} - Auto-Setup Guide

## 🔍 Repository Analysis

- **Repository**: {owner}/{repo_name}
- **Language**: {language.title()}
- **Framework**: {framework.title()}
- **Dependencies**: {len(dependencies)} packages detected

## 🚀 Quick Setup

### Automatic Setup
Run the generated setup script:
```bash
{"./setup.bat" if platform.system() == "Windows" else "./setup.sh"}
```

### Manual Setup

{self._generate_manual_setup_section(commands)}

## 📦 Dependencies

{self._generate_dependencies_section(dependencies[:20])}

## 🐳 Containerization

To containerize this repository:
```bash
python repocontainerizer.py containerize https://github.com/{owner}/{repo_name}
```

## 📝 Generated Files

- `setup.{"bat" if platform.system() == "Windows" else "sh"}` - Automated setup script
- `analysis-report.json` - Detailed analysis results
- `SETUP_README.md` - This file

## 🎯 Next Steps

1. Run the setup script
2. Test the application locally
3. Containerize for deployment
4. Add tests if not present
5. Add documentation

---
*Generated by RepoContainerizer v{__version__} on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    
    def _generate_manual_setup_section(self, commands: Dict[str, List[str]]) -> str:
        """Generate manual setup section for README"""
        content = ""
        
        if "install" in commands:
            content += "#### 1. Install Dependencies\n```bash\n"
            for cmd in commands["install"]:
                content += f"{cmd}\n"
            content += "```\n\n"
        
        if "setup" in commands:
            content += "#### 2. Setup Project\n```bash\n"
            for cmd in commands["setup"]:
                content += f"{cmd}\n"
            content += "```\n\n"
        
        if "build" in commands:
            content += "#### 3. Build Project\n```bash\n"
            for cmd in commands["build"]:
                content += f"{cmd}\n"
            content += "```\n\n"
        
        if "run" in commands:
            content += "#### 4. Run Application\n```bash\n"
            for cmd in commands["run"]:
                content += f"{cmd}\n"
            content += "```\n\n"
        
        if "test" in commands:
            content += "#### 5. Run Tests\n```bash\n"
            for cmd in commands["test"]:
                content += f"{cmd}\n"
            content += "```\n\n"
        
        return content or "No specific setup commands detected.\n\n"
    
    def _generate_dependencies_section(self, dependencies: List[str]) -> str:
        """Generate dependencies section for README"""
        if not dependencies:
            return "No dependencies detected.\n\n"
        
        content = f"Found {len(dependencies)} dependencies:\n\n"
        for dep in dependencies:
            content += f"- {dep}\n"
        
        return content + "\n"
    
    def execute_setup_script(self, script_path: Path, repo_path: Path) -> bool:
        """Execute the generated setup script"""
        try:
            console.print(f"🔧 Executing setup script: {script_path}")
            
            # Change to repository directory
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            
            # Execute script
            if platform.system() == "Windows":
                result = subprocess.run(
                    [str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minutes timeout
                    shell=True
                )
            else:
                result = subprocess.run(
                    [str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minutes timeout
                    executable="/bin/bash"
                )
            
            # Log output
            if result.stdout:
                self.logger.info(f"Setup script output: {result.stdout}")
            if result.stderr:
                self.logger.warning(f"Setup script stderr: {result.stderr}")
            
            # Restore original directory
            os.chdir(original_cwd)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            self.logger.error("Setup script execution timed out")
            return False
        except Exception as e:
            self.logger.error(f"Error executing setup script: {str(e)}")
            return False
        finally:
            # Ensure we restore the original directory
            try:
                os.chdir(original_cwd)
            except:
                pass
    
    def generate_setup_script(self, repo_path: Path, language: str, framework: str, commands: Dict[str, List[str]], use_uv: bool = False) -> str:
        """Generate a setup script for the repository"""
        
        # Determine script type based on OS
        is_windows = platform.system() == "Windows"
        script_ext = ".bat" if is_windows else ".sh"
        
        package_manager = "uv" if use_uv else ("pip" if language == "python" else "npm")
        
        if is_windows:
            script_content = f"""@echo off
REM Auto-generated setup script for {repo_path.name}
REM Generated by RepoContainerizer v{__version__}
REM Language: {language}, Framework: {framework}
REM Package Manager: {package_manager}

echo ==========================================
echo Setting up {repo_path.name}
echo ==========================================

REM Check if required tools are installed
echo Checking prerequisites...
{"where uv >nul 2>&1" if use_uv else "where python >nul 2>&1"}
if %errorlevel% neq 0 (
    echo Error: {"uv" if use_uv else "Python"} is not installed or not in PATH
    {"echo Please install uv: https://docs.astral.sh/uv/getting-started/installation/" if use_uv else "echo Please install Python: https://python.org/downloads/"}
    exit /b 1
)

"""
            
            # Add setup commands
            if "setup" in commands:
                script_content += "echo Setting up project environment...\n"
                for cmd in commands["setup"]:
                    script_content += f"{cmd}\n"
                script_content += "\n"
            
            # Add install commands
            if "install" in commands:
                script_content += "echo Installing dependencies...\n"
                for cmd in commands["install"]:
                    script_content += f"{cmd}\n"
                    script_content += "if %errorlevel% neq 0 (echo Error: Installation failed & exit /b 1)\n"
                script_content += "\n"
            
            # Add build commands
            if "build" in commands:
                script_content += "echo Building project...\n"
                for cmd in commands["build"]:
                    script_content += f"{cmd}\n"
                    script_content += "if %errorlevel% neq 0 (echo Error: Build failed & exit /b 1)\n"
                script_content += "\n"
            
            script_content += """echo ==========================================
echo Setup completed successfully!
echo ==========================================

echo.
echo Next steps:
"""
            
            # Add run commands
            if "run" in commands:
                script_content += f"echo To run the application: {commands['run'][0]}\n"
            
            if "test" in commands:
                script_content += f"echo To run tests: {commands['test'][0]}\n"
            
            script_content += """echo To containerize: python repocontainerizer.py containerize <repo_url>
echo.
pause
"""
        
        else:
            script_content = f"""#!/bin/bash
# Auto-generated setup script for {repo_path.name}
# Generated by RepoContainerizer v{__version__}
# Language: {language}, Framework: {framework}
# Package Manager: {package_manager}

set -e  # Exit on error

echo "=========================================="
echo "Setting up {repo_path.name}"
echo "=========================================="

# Check if required tools are installed
echo "Checking prerequisites..."
if ! command -v {"uv" if use_uv else "python"} &> /dev/null; then
    echo "Error: {"uv" if use_uv else "Python"} is not installed or not in PATH"
    {"echo 'Please install uv: https://docs.astral.sh/uv/getting-started/installation/'" if use_uv else "echo 'Please install Python: https://python.org/downloads/'"}
    exit 1
fi

"""
            
            # Add setup commands
            if "setup" in commands:
                script_content += "echo \"Setting up project environment...\"\n"
                for cmd in commands["setup"]:
                    script_content += f"{cmd}\n"
                script_content += "\n"
            
            # Add install commands
            if "install" in commands:
                script_content += "echo \"Installing dependencies...\"\n"
                for cmd in commands["install"]:
                    script_content += f"{cmd}\n"
                script_content += "\n"
            
            # Add build commands
            if "build" in commands:
                script_content += "echo \"Building project...\"\n"
                for cmd in commands["build"]:
                    script_content += f"{cmd}\n"
                script_content += "\n"
            
            script_content += """echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="

echo ""
echo "Next steps:"
"""
            
            # Add run commands
            if "run" in commands:
                script_content += f"echo \"To run the application: {commands['run'][0]}\"\n"
            
            if "test" in commands:
                script_content += f"echo \"To run tests: {commands['test'][0]}\"\n"
            
            script_content += """echo "To containerize: python repocontainerizer.py containerize <repo_url>"
echo ""
"""
        
        return script_content


def main():
    """Main function to run the RepoContainerizer CLI"""
    try:
        import argparse
        
        parser = argparse.ArgumentParser(
            description="RepoContainerizer - AI-powered repository containerization tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python repocontainerizer.py analyze https://github.com/user/repo
  python repocontainerizer.py containerize https://github.com/user/repo
  python repocontainerizer.py setup-repo /path/to/repo
            """
        )
        
        parser.add_argument("command", choices=["analyze", "containerize", "setup-repo"], 
                          help="Command to execute")
        parser.add_argument("target", help="Repository URL or local path")
        parser.add_argument("--output", "-o", default="./output", 
                          help="Output directory for generated files")
        parser.add_argument("--validate", action="store_true", 
                          help="Validate generated Docker configuration")
        parser.add_argument("--api-key", help="Gemini API key")
        parser.add_argument("--config", help="Path to configuration file")
        parser.add_argument("--format", choices=["yaml", "json"], default="yaml",
                          help="Output format for configuration files")
        
        args = parser.parse_args()
        
        # Set API key if provided
        if args.api_key:
            os.environ["GEMINI_API_KEY"] = args.api_key
        
        # Initialize containerizer
        containerizer = RepoContainerizer()
        
        # Execute command
        if args.command == "analyze":
            result = containerizer.analyze_repository(args.target)
            if result:
                print_colored_text("✅ Repository analysis completed successfully!", "green")
                print_colored_text(f"📊 Analysis results saved to: {args.output}", "blue")
            else:
                print_colored_text("❌ Repository analysis failed!", "red")
                sys.exit(1)
                
        elif args.command == "containerize":
            result = containerizer.containerize_repo(args.target, args.output, args.format, args.validate)
            if result:
                print_colored_text("✅ Repository containerization completed successfully!", "green")
                print_colored_text(f"🐳 Docker files saved to: {args.output}", "blue")
            else:
                print_colored_text("❌ Repository containerization failed!", "red")
                sys.exit(1)
                
        elif args.command == "setup-repo":
            result = containerizer.setup_repository(args.target)
            if result:
                print_colored_text("✅ Repository setup completed successfully!", "green")
                print_colored_text(f"📁 Setup files saved to: {args.output}", "blue")
            else:
                print_colored_text("❌ Repository setup failed!", "red")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print_colored_text("\n👋 Operation cancelled by user", "yellow")
        sys.exit(0)
    except Exception as e:
        print_colored_text(f"💥 Unexpected error: {str(e)}", "red")
        sys.exit(1)


if __name__ == "__main__":
    main()
