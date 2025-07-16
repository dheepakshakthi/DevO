# DevO Chat - Standalone Executable

## Quick Start

1. **Run the executable directly:**
   ```cmd
   dist\devochat.exe
   ```

2. **Or use the launcher:**
   ```cmd
   launch_devochat.bat
   ```

## Features

- **Unified Chat Interface**: One command for all development tasks
- **Repository Analysis**: Automatic code analysis and suggestions
- **Auto Setup**: Automatically clone repositories and install dependencies
- **Containerization**: Generate Docker files and configurations
- **AI-Powered**: Uses Gemini AI for intelligent code suggestions
- **Dependency Management**: Detect and fix missing dependencies
- **Session Management**: Save and load conversation sessions

## Usage Examples

### Basic Chat
```cmd
dist\devochat.exe
```

### Analyze Repository
```cmd
dist\devochat.exe -r "C:\path\to\repo"
```

### With API Key
```cmd
dist\devochat.exe -k "your-api-key"
```

### Save Session
```cmd
dist\devochat.exe -s "session.json"
```

### Load Session
```cmd
dist\devochat.exe -l "session.json"
```

## Available Commands in Chat

- `analyze <repo-path>` - Analyze repository structure and dependencies
- `containerize <repo-path>` - Generate Docker configuration
- `auto-setup <repo-url>` - Clone and setup repository automatically
- `help` - Show available commands
- `exit` - Exit the application

## Environment Variables

- `GEMINI_API_KEY` - Your Gemini API key
- `DEVOCHAT_CONFIG` - Path to configuration file

## Configuration

The application uses `sample-config.yml` for configuration. You can modify:
- Default API settings
- Output directories
- Template configurations
- Logging preferences

## Distribution

The `devochat.exe` file is completely standalone and can be:
- Copied to any Windows machine
- Run without Python installation
- Distributed as a single file

## File Size

The executable is approximately 50-60 MB and includes:
- Python runtime
- All dependencies (Google AI, Rich, Click, etc.)
- Application code and templates
- Configuration files

## Requirements

- Windows 10 or later
- No additional software required
- Internet connection for AI features

## Troubleshooting

1. **Missing dependencies**: The executable includes all dependencies
2. **API key issues**: Set GEMINI_API_KEY environment variable
3. **Permission errors**: Run as administrator if needed
4. **Network issues**: Check internet connection for AI features

## Support

For issues or questions, check the main repository documentation or create an issue in the project repository.
