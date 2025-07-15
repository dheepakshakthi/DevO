# DevO 🚀

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

- Python 3.8+
- Git
- Docker (optional, for validation)
- Google Gemini API key

### Quick Setup

#### Windows
```cmd
# Clone the repository
git clone https://github.com/your-username/repo-containerizer.git
cd repo-containerizer

# Run setup script
setup.bat

# Set API key
set GEMINI_API_KEY=your_api_key_here
```

#### Linux/Mac
```bash
# Clone the repository
git clone https://github.com/your-username/repo-containerizer.git
cd repo-containerizer

# Make setup script executable and run
chmod +x setup.sh
./setup.sh

# Set API key
export GEMINI_API_KEY=your_api_key_here
```

#### Manual Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set API key
export GEMINI_API_KEY=your_api_key_here
```

## Usage

### Basic Usage

```bash
# Containerize a GitHub repository
python repo_containerizer.py containerize https://github.com/owner/repo

# Specify output directory
python repo_containerizer.py containerize https://github.com/owner/repo --output ./my-output

# Generate JSON config instead of YAML
python repo_containerizer.py containerize https://github.com/owner/repo --format json

# Validate container by building it
python repo_containerizer.py containerize https://github.com/owner/repo --validate
```

### Advanced Usage

```bash
# Set API key via command line
python repo_containerizer.py containerize https://github.com/owner/repo --api-key your_api_key

# Combine multiple options
python repo_containerizer.py containerize https://github.com/owner/repo \
  --output ./output \
  --format yaml \
  --validate \
  --api-key your_api_key
```

### CLI Commands

```bash
# Show help
python repo_containerizer.py --help

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

## Architecture

```
RepoContainerizer/
├── repo_containerizer.py    # Main CLI application
├── utils.py                 # Utility functions for analysis
├── templates.py             # Docker templates for different stacks
├── requirements.txt         # Python dependencies
├── setup.sh                 # Linux/Mac setup script
├── setup.bat                # Windows setup script
└── README.md               # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Future Impact

### Zero-friction onboarding
Developers can spin up projects instantly, without needing manual instructions.

### Accelerates innovation
Reduces time wasted on setup, encouraging faster prototyping and collaboration.

### Standardizes deployment
Enforces best practices for containerization across all projects.

### Boosts open-source adoption
Makes more repositories immediately usable, even for non-experts.

### Supports AI development
Allows LLMs and agents to run and test code automatically without human help.

## Support

- 📧 Email: support@repocontainerizer.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/repo-containerizer/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/repo-containerizer/discussions)

---

*Made with ❤️ by the RepoContainerizer team*

