# Quick Start Guide for DevO 🚀

## Installation

1. **Install uv** (if not already installed):
   ```bash
   # Windows (PowerShell)
   iwr -useb https://astral.sh/uv/install.ps1 | iex
   
   # Linux/Mac
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and setup**:
   ```bash
   git clone https://github.com/dheepakshakthi/DevO-Hackfinity.git
   cd DevO-Hackfinity
   uv sync
   ```

3. **Set your API key**:
   ```bash
   # Windows
   set GEMINI_API_KEY=your_api_key_here
   
   # Linux/Mac
   export GEMINI_API_KEY=your_api_key_here
   ```

## Basic Usage

### 1. Containerize a Repository
```bash
uv run python repo_containerizer.py containerize https://github.com/owner/repo
```

### 2. Using Windows Batch Files
```cmd
devo.bat containerize https://github.com/owner/repo
```

### 3. Standalone Version
```bash
uv run python repocontainerizer.py containerize https://github.com/owner/repo
```

## Common Options

- `--output ./my-output` - Specify output directory
- `--validate` - Build container to validate
- `--format json` - Output JSON instead of YAML
- `--api-key KEY` - Set API key directly

## Examples

```bash
# Basic containerization
uv run python repo_containerizer.py containerize https://github.com/flask/flask

# With validation
uv run python repo_containerizer.py containerize https://github.com/flask/flask --validate

# Custom output directory
uv run python repo_containerizer.py containerize https://github.com/flask/flask --output ./flask-docker
```

## Getting Help

```bash
uv run python repo_containerizer.py --help
uv run python repo_containerizer.py containerize --help
```

## What Gets Generated

- `Dockerfile` - Optimized container configuration
- `docker-compose.yml` - Multi-service setup
- `container-config.yaml` - Configuration metadata
- `README.md` - Usage instructions

## Troubleshooting

1. **API Key Issues**: Make sure your Gemini API key is set correctly
2. **Dependencies**: Run `uv sync` to install all dependencies
3. **Python Version**: Requires Python 3.9+
4. **Tests**: Run `uv run python -m pytest` to verify everything works

## Next Steps

- Check the full README.md for detailed documentation
- Look at the `output/` directory for examples
- Run tests with `uv run python -m pytest`
- Try the demo: `uv run python demo.py`
