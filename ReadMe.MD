# DevO 🚀
## This project is a prototype in development
An advanced LLM-powered AI agent tool that automates the process of understanding and containerizing GitHub repositories. This tool eliminates the guesswork from running code by automatically analyzing repositories and generating production-ready Docker configurations.

## Features

- **🤖 AI-Powered Analysis**: Uses Google's Gemini API to intelligently analyze repository structure and tech stack
- **📦 Automatic Containerization**: Generates optimized Dockerfiles with security best practices
- **🔧 Multi-Language Support**: Supports Python, JavaScript/TypeScript, Java, Go, and more
- **🎯 Framework Detection**: Recognizes popular frameworks like Django, Flask, Express, Next.js, Spring, etc.
- **📋 Unified Configuration**: Creates JSON/YAML config files with ports, environment variables, and commands
- **🏥 Health Checks**: Automatically configures container health checks
- **✅ Validation**: Optional container build validation
- **🎨 Beautiful CLI**: Rich terminal interface with progress indicators and colored output

## Installation

### Prerequisites

- Python 3.9+
- Git
- **uv** (recommended) or pip
- Docker (optional, for validation)
- Google Gemini API key

### Quick Setup with uv (Recommended)

#### Windows
```cmd
# Clone the repository
git clone https://github.com/dheepakshakthi/DevO-Hackfinity.git
cd DevO-Hackfinity

# Install uv if not already installed
# Visit: https://docs.astral.sh/uv/getting-started/installation/

# Install dependencies using uv
uv sync

# Set up API key (choose one method)
# Method 1: Create .env file (recommended)
copy .env.example .env
# Edit .env and add your API key: GEMINI_API_KEY=your_api_key_here

# Method 2: Environment variable (temporary)
set GEMINI_API_KEY=your_api_key_here

# Run the tool
uv run python repo_containerizer.py --help
```

#### Linux/Mac
```bash
# Clone the repository
git clone https://github.com/dheepakshakthi/DevO-Hackfinity.git
cd DevO-Hackfinity

# Install uv if not already installed
# Visit: https://docs.astral.sh/uv/getting-started/installation/

# Install dependencies using uv
uv sync

# Set up API key (choose one method)
# Method 1: Create .env file (recommended)
cp .env.example .env
# Edit .env and add your API key: GEMINI_API_KEY=your_api_key_here

# Method 2: Environment variable (temporary)
export GEMINI_API_KEY=your_api_key_here

# Run the tool
uv run python repo_containerizer.py --help
```

### Alternative Setup with pip

#### Windows
```cmd
# Clone the repository
git clone https://github.com/dheepakshakthi/DevO-Hackfinity.git
cd DevO-Hackfinity

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set API key
set GEMINI_API_KEY=your_api_key_here
```

#### Linux/Mac
```bash
# Clone the repository
git clone https://github.com/dheepakshakthi/DevO-Hackfinity.git
cd DevO-Hackfinity

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API key
export GEMINI_API_KEY=your_api_key_here
```

## Usage

### Using uv (Recommended)

```bash
# Containerize a GitHub repository
uv run python repo_containerizer.py containerize https://github.com/owner/repo

# Specify output directory
uv run python repo_containerizer.py containerize https://github.com/owner/repo --output ./my-output

# Generate JSON config instead of YAML
uv run python repo_containerizer.py containerize https://github.com/owner/repo --format json

# Validate container by building it
uv run python repo_containerizer.py containerize https://github.com/owner/repo --validate
```

### Using batch files (Windows convenience)

```cmd
# Use the convenient batch file
devo.bat containerize https://github.com/owner/repo

# Or use the standalone version
devo-standalone.bat containerize https://github.com/owner/repo
```

### Advanced Usage

```bash
# Set API key via command line
uv run python repo_containerizer.py containerize https://github.com/owner/repo --api-key your_api_key

# Combine multiple options
uv run python repo_containerizer.py containerize https://github.com/owner/repo \
  --output ./output \
  --format yaml \
  --validate \
  --api-key your_api_key
```

### CLI Commands

```bash
# Show help
uv run python repo_containerizer.py --help

# Containerize a repository
python repo_containerizer.py containerize REPO_URL [OPTIONS]

# Validate a generated Dockerfile
python repo_containerizer.py validate path/to/Dockerfile

# Setup environment and check dependencies
python repo_containerizer.py setup
```

## Generated Files

RepoContainerizer generates the following files:

- **`Dockerfile`**: Production-ready container configuration
- **`docker-compose.yml`**: Multi-service orchestration
- **`container-config.yml/json`**: Unified configuration with analysis results
- **`.env.example`**: Environment variable template
- **`CONTAINERIZATION_README.md`**: Setup and usage instructions

## Example Output

```
🚀 RepoContainerizer
AI-Powered GitHub Repository Containerization

🔄 Cloning repository: https://github.com/example/flask-app
✅ Repository cloned to: /tmp/repo_xyz
📊 Analyzing repository structure...
📖 Reading important files...
🤖 Analyzing repository with AI...
📝 Generating containerization files...
✅ Containerization Complete!

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                 Analysis Results                    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Primary Language │ Python                          │
│ Framework        │ Flask                           │
│ Package Manager  │ pip                             │
│ Database         │ PostgreSQL                      │
│ Port             │ 5000                            │
└──────────────────┴─────────────────────────────────┘

Generated Files:
  📄 ./output/Dockerfile
  📄 ./output/docker-compose.yml
  📄 ./output/container-config.yml
  📄 ./output/.env.example
  📄 ./output/CONTAINERIZATION_README.md

Next Steps:
1. Navigate to the output directory: cd ./output
2. Build the container: docker build -t my-app .
3. Run the container: docker run -p 5000:8080 my-app
```

## Supported Technologies

### Languages
- Python (Django, Flask, FastAPI, generic)
- JavaScript/TypeScript (Express, Next.js, React, Vue, Angular)
- Java (Spring Boot, generic)
- Go (Gin, generic)
- PHP (Laravel, generic)
- Ruby (Rails, generic)

### Databases
- PostgreSQL
- MySQL
- SQLite
- MongoDB
- Redis
- Elasticsearch

### Package Managers
- npm, yarn, pnpm (JavaScript)
- pip, pipenv, poetry (Python)
- maven, gradle (Java)
- cargo (Rust)
- go mod (Go)
- composer (PHP)
- bundle (Ruby)

## Configuration

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)

### API Key Setup

1. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set the environment variable:
   ```bash
   # Linux/Mac
   export GEMINI_API_KEY=your_api_key_here
   
   # Windows
   set GEMINI_API_KEY=your_api_key_here
   ```
