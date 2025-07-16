# RepoContainerizer Quick Start Guide

## Overview
RepoContainerizer is an AI-powered tool that automatically analyzes GitHub repositories and generates Docker containerization files. It uses Google's Gemini AI to understand code structure, detect tech stacks, and create production-ready containers.

## What it does
1. **Clones** a GitHub repository
2. **Analyzes** the code structure and dependencies
3. **Detects** the programming language, framework, and tech stack
4. **Generates** optimized Dockerfile and docker-compose.yml
5. **Creates** configuration files with environment variables and commands
6. **Validates** the container (optional)

## Quick Start

### 1. Set up your API key
```bash
# Windows
set GEMINI_API_KEY=AIzaSyAwxg1aGIsvBSb17SAE-lFTz_Bh-lIDvrI

# Linux/Mac
export GEMINI_API_KEY=AIzaSyAwxg1aGIsvBSb17SAE-lFTz_Bh-lIDvrI
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the tool
```bash
# Basic usage
python repo_containerizer.py containerize https://github.com/owner/repo

# With options
python repo_containerizer.py containerize https://github.com/owner/repo --output ./my-containers --validate
```

## Command Options

### containerize
```bash
python repo_containerizer.py containerize REPO_URL [OPTIONS]
```

**Options:**
- `--output, -o`: Output directory for generated files (default: ./output)
- `--format, -f`: Config file format (yaml/json, default: yaml)
- `--validate`: Build and validate the container
- `--api-key`: Gemini API key (optional if env var is set)

### validate
```bash
python repo_containerizer.py validate path/to/Dockerfile
```

### setup
```bash
python repo_containerizer.py setup
```

## Generated Files

The tool creates these files in the output directory:

1. **Dockerfile** - Production-ready container configuration
2. **docker-compose.yml** - Multi-service orchestration
3. **container-config.yml** - Unified configuration with analysis results
4. **.env.example** - Environment variable template
5. **CONTAINERIZATION_README.md** - Setup and usage instructions

## Example Output Structure

```
output/
├── Dockerfile
├── docker-compose.yml
├── container-config.yml
├── .env.example
└── CONTAINERIZATION_README.md
```

## Supported Technologies

### Languages
- Python (Django, Flask, FastAPI)
- JavaScript/TypeScript (Express, Next.js, React)
- Java (Spring Boot)
- Go (Gin)
- PHP (Laravel)
- Ruby (Rails)

### Databases
- PostgreSQL
- MySQL
- MongoDB
- Redis
- SQLite

### Package Managers
- npm, yarn, pnpm
- pip, pipenv, poetry
- maven, gradle
- cargo, go mod

## Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)

## Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   ❌ API key required. Set GEMINI_API_KEY environment variable
   ```
   **Solution**: Set the GEMINI_API_KEY environment variable

2. **Import Errors**
   ```
   ❌ Import "click" could not be resolved
   ```
   **Solution**: Install dependencies with `pip install -r requirements.txt`

3. **Git Clone Error**
   ```
   ❌ Error cloning repository
   ```
   **Solution**: Check internet connection and repository URL

4. **Docker Validation Failed**
   ```
   ❌ Container build failed
   ```
   **Solution**: Install Docker or skip validation with `--no-validate`

### Testing the Setup

Run the test script to verify everything is working:
```bash
python test_containerizer.py
```

### Example Usage

Run the example script to see the tool in action:
```bash
python example.py
```

## Advanced Usage

### Custom Output Directory
```bash
python repo_containerizer.py containerize https://github.com/owner/repo --output ./custom-output
```

### JSON Configuration
```bash
python repo_containerizer.py containerize https://github.com/owner/repo --format json
```

### With Validation
```bash
python repo_containerizer.py containerize https://github.com/owner/repo --validate
```

### Multiple Options
```bash
python repo_containerizer.py containerize https://github.com/owner/repo \
  --output ./containers \
  --format yaml \
  --validate \
  --api-key your_api_key
```

## Integration with CI/CD

You can integrate RepoContainerizer into your CI/CD pipeline:

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
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Containerize
        run: |
          python repo_containerizer.py containerize https://github.com/${{ github.repository }} --output ./containers
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

## Best Practices

1. **Always validate** your containers before deployment
2. **Review generated files** for security and optimization
3. **Customize environment variables** for your specific use case
4. **Test locally** before pushing to production
5. **Keep API keys secure** and never commit them to version control

## Future Enhancements

- Support for more programming languages
- Integration with cloud platforms (AWS, GCP, Azure)
- Kubernetes manifest generation
- Security scanning integration
- Performance optimization suggestions

## Support

For issues and questions:
- Check the troubleshooting section above
- Run the test script: `python test_containerizer.py`
- Review the generated README files in the output directory

---

*Happy containerizing! 🐳*
