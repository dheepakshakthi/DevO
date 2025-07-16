# RepoContainerizer - Standalone CLI Application

## Overview

RepoContainerizer is a powerful, standalone command-line application inspired by modern CLI tools like Warp. It uses AI to automatically analyze GitHub repositories and generate production-ready Docker configurations.

## 🚀 Key Features

### **Warp-Inspired Design**
- **Beautiful CLI Interface**: Rich terminal output with colors, tables, and progress indicators
- **Interactive Setup**: Guided configuration process
- **Intuitive Commands**: Simple, memorable command structure
- **Smart Defaults**: Minimal configuration required to get started

### **AI-Powered Analysis**
- **Intelligent Detection**: Automatically identifies programming languages, frameworks, and dependencies
- **Context-Aware Generation**: Creates optimized Docker configurations based on project analysis
- **Fallback Systems**: Works even without internet or API access using built-in heuristics

### **Zero-Dependency Core**
- **Minimal Requirements**: Runs with just Python standard library
- **Enhanced Experience**: Optional rich output with additional packages
- **Standalone Executable**: Can be built into a single executable file

## 📦 Installation Options

### Option 1: Direct Python Usage
```bash
# Download the standalone script
curl -O https://raw.githubusercontent.com/your-repo/repocontainerizer/main/repocontainerizer.py

# Set executable permissions (Linux/Mac)
chmod +x repocontainerizer.py

# Run directly
python repocontainerizer.py setup
```

### Option 2: Enhanced Installation
```bash
# Install with enhanced features
pip install -r requirements-standalone.txt

# Run with enhanced output
python repocontainerizer.py setup
```

### Option 3: Windows Batch Interface
```cmd
# Download repocontainerizer.bat
# Double-click to run the interactive menu
repocontainerizer.bat
```

### Option 4: Standalone Executable
```bash
# Build standalone executable
python build_standalone.py

# Use the executable
./dist/repocontainerizer/repocontainerizer containerize https://github.com/owner/repo
```

## 🎯 Quick Start

### 1. Initial Setup
```bash
# Interactive setup (recommended)
python repocontainerizer.py setup

# Or configure manually
python repocontainerizer.py config set api_key your_gemini_api_key
python repocontainerizer.py config set default_output_dir ./containers
```

### 2. Containerize a Repository
```bash
# Basic usage
python repocontainerizer.py containerize https://github.com/owner/repo

# With custom options
python repocontainerizer.py containerize https://github.com/owner/repo \
  --output ./my-containers \
  --format json \
  --validate
```

### 3. Build and Run Container
```bash
# Navigate to output directory
cd ./containers

# Build the container
docker build -t my-app .

# Run the container
docker run -p 8080:8080 my-app

# Or use docker-compose
docker-compose up -d
```

## 🛠️ Command Reference

### Core Commands

#### `containerize`
Transform a GitHub repository into a containerized application.

```bash
python repocontainerizer.py containerize <repo_url> [options]

Options:
  --output, -o <dir>    Output directory (default: ./output)
  --format, -f <fmt>    Config format: yaml|json (default: yaml)
  --validate           Validate container by building it
  --verbose, -v        Verbose output
  --api-key <key>      Override configured API key
```

**Examples:**
```bash
# Basic containerization
python repocontainerizer.py containerize https://github.com/flask/flask

# Custom output directory
python repocontainerizer.py containerize https://github.com/express/express -o ./express-container

# JSON configuration with validation
python repocontainerizer.py containerize https://github.com/spring-projects/spring-boot \
  --format json --validate

# Verbose output with custom API key
python repocontainerizer.py containerize https://github.com/golang/go \
  --verbose --api-key your_api_key_here
```

#### `config`
Manage application configuration.

```bash
python repocontainerizer.py config [subcommand] [options]

Subcommands:
  (none)              Show current configuration
  set <key> <value>   Set configuration value
  get <key>           Get configuration value
  reset               Reset to default configuration
```

**Examples:**
```bash
# Show current configuration
python repocontainerizer.py config

# Set API key
python repocontainerizer.py config set api_key your_gemini_api_key

# Set default output directory
python repocontainerizer.py config set default_output_dir ./containers

# Enable validation by default
python repocontainerizer.py config set validate_by_default true

# Get a specific value
python repocontainerizer.py config get api_key
```

#### `validate`
Validate a generated Dockerfile by building it.

```bash
python repocontainerizer.py validate <dockerfile_path>
```

**Examples:**
```bash
# Validate a Dockerfile
python repocontainerizer.py validate ./output/Dockerfile

# Validate in a specific directory
python repocontainerizer.py validate ./my-containers/Dockerfile
```

#### `setup`
Interactive setup and configuration.

```bash
python repocontainerizer.py setup
```

This command provides a guided setup process that:
- Configures your Gemini API key
- Sets default preferences
- Validates your environment
- Provides usage tips

#### `version`
Display version and system information.

```bash
python repocontainerizer.py version
```

#### `help`
Show comprehensive help information.

```bash
python repocontainerizer.py help
```

## 🎨 Windows Interactive Interface

For Windows users, the `repocontainerizer.bat` file provides a beautiful menu-driven interface:

```cmd
repocontainerizer.bat
```

**Features:**
- 🚀 Interactive repository containerization
- ⚙️ Setup and configuration management
- 🔍 Dockerfile validation
- 📊 System information display
- 🏗️ Standalone executable building
- 📖 Integrated help system

## 🔧 Configuration

### Configuration File Location
- **Windows**: `%USERPROFILE%\.repocontainerizer\config.json`
- **Linux/Mac**: `~/.repocontainerizer/config.json`

### Configuration Options

```json
{
  "api_key": "your_gemini_api_key",
  "default_output_dir": "./output",
  "default_format": "yaml",
  "validate_by_default": false,
  "theme": "auto",
  "last_updated": "2024-01-01T00:00:00"
}
```

### Environment Variables

You can also use environment variables:
- `GEMINI_API_KEY`: Your Gemini API key
- `REPOCONTAINERIZER_OUTPUT`: Default output directory
- `REPOCONTAINERIZER_FORMAT`: Default format (yaml/json)

## 📁 Generated Files

Each containerization produces these files:

### 1. **Dockerfile**
Production-ready container configuration with:
- Multi-stage builds (when appropriate)
- Security best practices (non-root user, minimal base images)
- Optimized layer caching
- Framework-specific optimizations

### 2. **docker-compose.yml**
Orchestration configuration including:
- Service definitions
- Network configuration
- Volume mounts
- Environment variables
- Health checks

### 3. **container-config.yaml/json**
Unified configuration containing:
- Repository analysis results
- Detected technologies
- Container configuration
- Build and run commands

### 4. **README.md**
Generated documentation with:
- Quick start instructions
- Build and run commands
- Configuration details
- Project-specific notes

## 🎯 Advanced Usage

### Batch Processing
```bash
# Process multiple repositories
for repo in repo1 repo2 repo3; do
  python repocontainerizer.py containerize "https://github.com/owner/$repo" \
    --output "./containers/$repo"
done
```

### CI/CD Integration
```yaml
# GitHub Actions example
name: Auto-containerize
on: [push]
jobs:
  containerize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Download RepoContainerizer
        run: |
          curl -O https://raw.githubusercontent.com/your-repo/repocontainerizer/main/repocontainerizer.py
      - name: Containerize
        run: |
          python repocontainerizer.py containerize https://github.com/${{ github.repository }}
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

### Custom Templates
You can extend the tool by modifying the Dockerfile templates in the code or by using the generated files as starting points.

## 🛡️ Security Features

### Container Security
- **Non-root users**: All generated containers run as non-root users
- **Minimal base images**: Uses slim/alpine images when possible
- **Security scanning ready**: Compatible with security scanning tools
- **Environment variable protection**: Sensitive data handled via environment variables

### API Security
- **API key protection**: Keys are stored securely and never logged
- **Rate limiting**: Respects API rate limits
- **Fallback modes**: Works without API access using built-in analysis

## 🚀 Performance Optimization

### Caching
- **Configuration caching**: Stores settings locally
- **Analysis caching**: Caches repository analysis results
- **Template caching**: Reuses generated templates

### Efficient Processing
- **Minimal dependencies**: Core functionality requires only Python standard library
- **Lazy loading**: Optional features loaded only when needed
- **Concurrent processing**: Parallel analysis where possible

## 🔍 Troubleshooting

### Common Issues

#### "API key required"
```bash
# Set API key
python repocontainerizer.py config set api_key your_api_key

# Or use environment variable
export GEMINI_API_KEY=your_api_key
```

#### "Repository not found"
- Ensure the repository URL is correct
- Check if the repository is public
- Verify internet connectivity

#### "Docker build failed"
- Ensure Docker is installed and running
- Check the generated Dockerfile for syntax errors
- Review the build logs for specific errors

#### "Import errors"
```bash
# Install optional dependencies
pip install -r requirements-standalone.txt

# Or use minimal mode (works without additional packages)
python repocontainerizer.py --help
```

### Debug Mode
```bash
# Enable verbose logging
python repocontainerizer.py containerize https://github.com/owner/repo --verbose

# Check logs
# Windows: %USERPROFILE%\.repocontainerizer\logs\
# Linux/Mac: ~/.repocontainerizer/logs/
```

## 🧪 Testing

### Run Tests
```bash
# Run the test suite
python test_standalone.py

# Test specific functionality
python repocontainerizer.py version
python repocontainerizer.py help
```

### Manual Testing
```bash
# Test with a simple repository
python repocontainerizer.py containerize https://github.com/octocat/Hello-World

# Verify generated files
ls -la ./output/
docker build -t test-app ./output/
```

## 🏗️ Building Standalone Executable

### Requirements
- Python 3.8+
- PyInstaller

### Build Process
```bash
# Install build dependencies
pip install pyinstaller

# Build executable
python build_standalone.py

# Or use the Windows interface
repocontainerizer.bat
# Choose option 5: Build standalone executable
```

### Distribution
The build process creates a `dist/repocontainerizer/` directory containing:
- Standalone executable
- Installation scripts
- Documentation
- Usage examples

## 🤝 Contributing

### Development Setup
```bash
# Clone the repository
git clone https://github.com/your-repo/repocontainerizer.git
cd repocontainerizer

# Install development dependencies
pip install -r requirements-standalone.txt

# Run tests
python test_standalone.py
```

### Adding New Features
1. Extend the appropriate class in `repocontainerizer.py`
2. Add new CLI commands in the `run()` method
3. Update the help text and documentation
4. Add tests to `test_standalone.py`

## 📊 Metrics and Analytics

### Usage Statistics
The tool collects anonymous usage statistics to improve functionality:
- Command usage frequency
- Success/failure rates
- Performance metrics
- Error patterns

### Performance Monitoring
- Repository analysis time
- Container build success rates
- API response times
- User experience metrics

## 🔮 Future Enhancements

### Planned Features
- **Kubernetes support**: Generate Kubernetes manifests
- **Cloud deployment**: Direct deployment to cloud platforms
- **Security scanning**: Integrated vulnerability scanning
- **Template customization**: User-defined templates
- **Plugin system**: Extensible architecture

### Community Requests
- Multi-language support
- Advanced configuration options
- Integration with popular CI/CD platforms
- Web interface
- Desktop application

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by modern CLI tools like Warp
- Built with Python and love for automation
- Thanks to the open-source community
- Powered by Google Gemini API

---

**Happy containerizing! 🐳**

For support, issues, or contributions, visit: https://github.com/your-repo/repocontainerizer
