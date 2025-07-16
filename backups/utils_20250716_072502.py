#!/usr/bin/env python3
"""
Utility functions for repository analysis and containerization
"""

import os
import re
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path

def detect_language_from_files(files: List[str]) -> Dict[str, int]:
    """Detect programming languages from file extensions"""
    language_extensions = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'JavaScript',
        '.tsx': 'TypeScript',
        '.java': 'Java',
        '.kt': 'Kotlin',
        '.go': 'Go',
        '.rs': 'Rust',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.php': 'PHP',
        '.rb': 'Ruby',
        '.swift': 'Swift',
        '.dart': 'Dart',
        '.scala': 'Scala',
        '.clj': 'Clojure',
        '.r': 'R',
        '.sh': 'Shell',
        '.yml': 'YAML',
        '.yaml': 'YAML',
        '.json': 'JSON',
        '.xml': 'XML',
        '.html': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.sass': 'SASS',
        '.less': 'LESS',
        '.sql': 'SQL',
        '.dockerfile': 'Dockerfile',
    }
    
    language_counts = {}
    
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext in language_extensions:
            lang = language_extensions[ext]
            language_counts[lang] = language_counts.get(lang, 0) + 1
    
    return language_counts

def detect_framework_from_files(files: List[str], file_contents: Dict[str, str]) -> str:
    """Detect framework from files and their contents"""
    
    # Check for specific framework files
    framework_indicators = {
        'package.json': ['react', 'next', 'express', 'vue', 'angular', 'gatsby', 'nuxt'],
        'requirements.txt': ['django', 'flask', 'fastapi', 'tornado', 'bottle'],
        'Pipfile': ['django', 'flask', 'fastapi', 'tornado', 'bottle'],
        'pyproject.toml': ['django', 'flask', 'fastapi', 'tornado', 'bottle'],
        'pom.xml': ['spring', 'struts', 'wicket'],
        'build.gradle': ['spring', 'struts', 'wicket'],
        'Cargo.toml': ['actix', 'rocket', 'warp'],
        'go.mod': ['gin', 'echo', 'fiber', 'gorilla'],
        'composer.json': ['laravel', 'symfony', 'codeigniter'],
        'Gemfile': ['rails', 'sinatra', 'hanami']
    }
    
    detected_frameworks = []
    
    for file, content in file_contents.items():
        if file in framework_indicators:
            content_lower = content.lower()
            for framework in framework_indicators[file]:
                if framework in content_lower:
                    detected_frameworks.append(framework)
    
    # Check for framework-specific files
    framework_files = {
        'manage.py': 'django',
        'app.py': 'flask',
        'main.py': 'fastapi',
        'server.js': 'express',
        'index.js': 'express',
        'next.config.js': 'next',
        'gatsby-config.js': 'gatsby',
        'nuxt.config.js': 'nuxt',
        'angular.json': 'angular',
        'vue.config.js': 'vue',
        'Application.java': 'spring',
        'main.go': 'gin',
        'artisan': 'laravel',
        'config/application.rb': 'rails'
    }
    
    for file in files:
        if file in framework_files:
            detected_frameworks.append(framework_files[file])
    
    # Return the most likely framework
    if detected_frameworks:
        return max(set(detected_frameworks), key=detected_frameworks.count)
    
    return 'generic'

def detect_package_manager(files: List[str]) -> str:
    """Detect package manager from files"""
    package_managers = {
        'package.json': 'npm',
        'package-lock.json': 'npm',
        'yarn.lock': 'yarn',
        'pnpm-lock.yaml': 'pnpm',
        'requirements.txt': 'pip',
        'Pipfile': 'pipenv',
        'pyproject.toml': 'pip',
        'poetry.lock': 'poetry',
        'pom.xml': 'maven',
        'build.gradle': 'gradle',
        'Cargo.toml': 'cargo',
        'go.mod': 'go',
        'composer.json': 'composer',
        'Gemfile': 'bundle'
    }
    
    for file in files:
        if file in package_managers:
            return package_managers[file]
    
    return 'unknown'

def detect_database_requirements(file_contents: Dict[str, str]) -> List[str]:
    """Detect database requirements from file contents"""
    databases = []
    
    database_indicators = {
        'postgresql': ['postgresql', 'postgres', 'psycopg2', 'pg_', 'postgresql://'],
        'mysql': ['mysql', 'pymysql', 'mysql2', 'mysql://'],
        'sqlite': ['sqlite', 'sqlite3', 'sqlite://'],
        'mongodb': ['mongodb', 'pymongo', 'mongoose', 'mongodb://'],
        'redis': ['redis', 'redis-py', 'ioredis', 'redis://'],
        'elasticsearch': ['elasticsearch', 'elastic', 'elasticsearch://'],
        'cassandra': ['cassandra', 'datastax', 'cassandra://']
    }
    
    for content in file_contents.values():
        content_lower = content.lower()
        for db, indicators in database_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                if db not in databases:
                    databases.append(db)
    
    return databases

def detect_port_from_files(file_contents: Dict[str, str]) -> int:
    """Detect the port number from file contents"""
    default_ports = {
        'django': 8000,
        'flask': 5000,
        'fastapi': 8000,
        'express': 3000,
        'next': 3000,
        'react': 3000,
        'vue': 8080,
        'angular': 4200,
        'spring': 8080,
        'gin': 8080,
        'laravel': 8000,
        'rails': 3000
    }
    
    # Look for port configurations in files
    port_patterns = [
        r'port[:\s]*[=]?\s*(\d+)',
        r'PORT[:\s]*[=]?\s*(\d+)',
        r'listen[:\s]*[=]?\s*(\d+)',
        r'server\.port[:\s]*[=]?\s*(\d+)',
        r'app\.listen\s*\(\s*(\d+)',
        r'\.run\s*\(\s*port\s*=\s*(\d+)',
        r'server_port[:\s]*[=]?\s*(\d+)'
    ]
    
    for content in file_contents.values():
        for pattern in port_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                try:
                    port = int(matches[0])
                    if 1000 <= port <= 65535:  # Valid port range
                        return port
                except ValueError:
                    continue
    
    return 8080  # Default port

def detect_environment_variables(file_contents: Dict[str, str]) -> Dict[str, str]:
    """Detect environment variables from file contents"""
    env_vars = {}
    
    # Common environment variable patterns
    env_patterns = [
        r'os\.environ\.get\([\'"]([A-Z_]+)[\'"]',
        r'process\.env\.([A-Z_]+)',
        r'System\.getenv\([\'"]([A-Z_]+)[\'"]',
        r'std::env::var\([\'"]([A-Z_]+)[\'"]',
        r'\$\{([A-Z_]+)\}',
        r'\$([A-Z_]+)',
        r'env\([\'"]([A-Z_]+)[\'"]'
    ]
    
    # Common environment variable descriptions
    env_descriptions = {
        'DATABASE_URL': 'Database connection URL',
        'DB_HOST': 'Database host',
        'DB_PORT': 'Database port',
        'DB_NAME': 'Database name',
        'DB_USER': 'Database username',
        'DB_PASSWORD': 'Database password',
        'REDIS_URL': 'Redis connection URL',
        'SECRET_KEY': 'Secret key for encryption',
        'JWT_SECRET': 'JWT token secret',
        'API_KEY': 'API key for external services',
        'PORT': 'Application port',
        'HOST': 'Application host',
        'NODE_ENV': 'Node.js environment',
        'FLASK_ENV': 'Flask environment',
        'DJANGO_SETTINGS_MODULE': 'Django settings module',
        'DEBUG': 'Debug mode flag',
        'LOG_LEVEL': 'Logging level',
        'CORS_ORIGIN': 'CORS allowed origins',
        'MAIL_SERVER': 'Email server',
        'MAIL_PORT': 'Email server port',
        'MAIL_USERNAME': 'Email username',
        'MAIL_PASSWORD': 'Email password',
        'AWS_ACCESS_KEY_ID': 'AWS access key',
        'AWS_SECRET_ACCESS_KEY': 'AWS secret key',
        'AWS_REGION': 'AWS region',
        'GOOGLE_APPLICATION_CREDENTIALS': 'Google Cloud credentials',
        'MONGODB_URI': 'MongoDB connection URI',
        'ELASTICSEARCH_URL': 'Elasticsearch URL'
    }
    
    detected_vars = set()
    
    for content in file_contents.values():
        for pattern in env_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                detected_vars.add(match.upper())
    
    # Add descriptions for detected variables
    for var in detected_vars:
        env_vars[var] = env_descriptions.get(var, f"Environment variable: {var}")
    
    # Add common default variables if not detected
    if not any(var.startswith('DB_') or 'DATABASE' in var for var in detected_vars):
        env_vars['DATABASE_URL'] = 'Database connection URL'
    
    if 'PORT' not in detected_vars:
        env_vars['PORT'] = 'Application port'
    
    return env_vars

def detect_build_tools(files: List[str], file_contents: Dict[str, str]) -> List[str]:
    """Detect build tools from files and contents"""
    build_tools = []
    
    # Build tool indicators
    build_indicators = {
        'webpack.config.js': 'webpack',
        'rollup.config.js': 'rollup',
        'vite.config.js': 'vite',
        'gulpfile.js': 'gulp',
        'Gruntfile.js': 'grunt',
        'tsconfig.json': 'typescript',
        'babel.config.js': 'babel',
        '.babelrc': 'babel',
        'Makefile': 'make',
        'CMakeLists.txt': 'cmake',
        'build.gradle': 'gradle',
        'pom.xml': 'maven',
        'Cargo.toml': 'cargo',
        'go.mod': 'go',
        'setup.py': 'python setuptools',
        'pyproject.toml': 'python build',
        'tox.ini': 'tox',
        'Dockerfile': 'docker',
        'docker-compose.yml': 'docker-compose',
        'docker-compose.yaml': 'docker-compose',
        '.github/workflows': 'github-actions',
        'Jenkinsfile': 'jenkins',
        '.travis.yml': 'travis-ci',
        '.circleci/config.yml': 'circleci'
    }
    
    for file in files:
        if file in build_indicators:
            build_tools.append(build_indicators[file])
    
    # Check package.json for build scripts
    if 'package.json' in file_contents:
        try:
            package_data = json.loads(file_contents['package.json'])
            scripts = package_data.get('scripts', {})
            
            if 'build' in scripts:
                build_tools.append('npm build')
            if 'test' in scripts:
                build_tools.append('npm test')
            if 'start' in scripts:
                build_tools.append('npm start')
                
        except json.JSONDecodeError:
            pass
    
    return list(set(build_tools))

def generate_health_check_command(language: str, framework: str, port: int) -> str:
    """Generate appropriate health check command"""
    
    health_checks = {
        'python': {
            'django': f'python manage.py check --deploy',
            'flask': f'curl -f http://localhost:{port}/health || exit 1',
            'fastapi': f'curl -f http://localhost:{port}/health || exit 1',
            'generic': f'curl -f http://localhost:{port} || exit 1'
        },
        'javascript': {
            'express': f'curl -f http://localhost:{port}/health || exit 1',
            'next': f'curl -f http://localhost:{port}/api/health || exit 1',
            'react': f'curl -f http://localhost:{port} || exit 1',
            'generic': f'curl -f http://localhost:{port} || exit 1'
        },
        'java': {
            'spring': f'curl -f http://localhost:{port}/actuator/health || exit 1',
            'generic': f'curl -f http://localhost:{port}/health || exit 1'
        },
        'go': {
            'gin': f'wget --no-verbose --tries=1 --spider http://localhost:{port}/health || exit 1',
            'generic': f'wget --no-verbose --tries=1 --spider http://localhost:{port} || exit 1'
        }
    }
    
    if language.lower() in health_checks:
        framework_checks = health_checks[language.lower()]
        return framework_checks.get(framework.lower(), framework_checks.get('generic', f'curl -f http://localhost:{port} || exit 1'))
    
    return f'curl -f http://localhost:{port} || exit 1'

def generate_run_commands(language: str, framework: str, package_manager: str) -> Dict[str, str]:
    """Generate run commands for different languages and frameworks"""
    
    commands = {
        'python': {
            'install': 'pip install -r requirements.txt',
            'build': 'python setup.py build',
            'start': 'python main.py',
            'test': 'python -m pytest'
        },
        'javascript': {
            'install': f'{package_manager} install',
            'build': f'{package_manager} run build',
            'start': f'{package_manager} start',
            'test': f'{package_manager} test'
        },
        'java': {
            'install': 'mvn install' if package_manager == 'maven' else 'gradle build',
            'build': 'mvn package' if package_manager == 'maven' else 'gradle build',
            'start': 'java -jar target/*.jar',
            'test': 'mvn test' if package_manager == 'maven' else 'gradle test'
        },
        'go': {
            'install': 'go mod download',
            'build': 'go build -o main .',
            'start': './main',
            'test': 'go test ./...'
        }
    }
    
    # Framework-specific overrides
    framework_overrides = {
        'django': {
            'start': 'python manage.py runserver 0.0.0.0:8000',
            'test': 'python manage.py test'
        },
        'flask': {
            'start': 'python app.py',
            'test': 'python -m pytest'
        },
        'fastapi': {
            'start': 'uvicorn main:app --host 0.0.0.0 --port 8000',
            'test': 'python -m pytest'
        },
        'express': {
            'start': 'node index.js',
            'test': 'npm test'
        },
        'next': {
            'start': 'npm run start',
            'build': 'npm run build'
        },
        'react': {
            'start': 'npm start',
            'build': 'npm run build'
        },
        'spring': {
            'start': 'java -jar target/*.jar',
            'test': 'mvn test'
        },
        'gin': {
            'start': './main',
            'test': 'go test ./...'
        }
    }
    
    base_commands = commands.get(language.lower(), {
        'install': 'echo "No install command available"',
        'build': 'echo "No build command available"',
        'start': 'echo "No start command available"',
        'test': 'echo "No test command available"'
    })
    
    # Apply framework-specific overrides
    if framework.lower() in framework_overrides:
        base_commands.update(framework_overrides[framework.lower()])
    
    return base_commands

def extract_dependencies(file_contents: Dict[str, str]) -> List[str]:
    """Extract dependencies from various package files"""
    dependencies = []
    
    # Node.js dependencies
    if 'package.json' in file_contents:
        try:
            package_data = json.loads(file_contents['package.json'])
            deps = package_data.get('dependencies', {})
            dev_deps = package_data.get('devDependencies', {})
            dependencies.extend(list(deps.keys()))
            dependencies.extend(list(dev_deps.keys()))
        except json.JSONDecodeError:
            pass
    
    # Python dependencies
    if 'requirements.txt' in file_contents:
        lines = file_contents['requirements.txt'].strip().split('\n')
        for line in lines:
            if line.strip() and not line.startswith('#'):
                # Extract package name (before version specifier)
                package = re.split(r'[>=<~!]', line.strip())[0]
                dependencies.append(package)
    
    # Java dependencies (Maven)
    if 'pom.xml' in file_contents:
        # Simple regex to extract artifactId from Maven dependencies
        artifact_pattern = r'<artifactId>(.*?)</artifactId>'
        matches = re.findall(artifact_pattern, file_contents['pom.xml'])
        dependencies.extend(matches)
    
    # Go dependencies
    if 'go.mod' in file_contents:
        lines = file_contents['go.mod'].strip().split('\n')
        for line in lines:
            if line.strip().startswith('require'):
                continue
            if '/' in line and not line.strip().startswith('//'):
                # Extract module name
                parts = line.strip().split()
                if len(parts) >= 2:
                    dependencies.append(parts[0])
    
    return list(set(dependencies))  # Remove duplicates
