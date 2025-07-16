# DevO Chat - Standalone Executable

## 📦 Distribution Package

This folder contains the standalone executable version of DevO Chat - your AI-powered development assistant.

### 📁 Contents

- `devochat.exe` - Main executable (standalone, no Python required)
- `launch_devochat.bat` - Convenience launcher script
- `README.md` - This file
- `.env.example` - Example environment file for API key

### 🚀 Quick Start

1. **Set up API Key** (required):
   ```cmd
   # Option 1: Environment variable
   set GEMINI_API_KEY=your_api_key_here
   
   # Option 2: Create .env file
   echo GEMINI_API_KEY=your_api_key_here > .env
   
   # Option 3: Use command line parameter
   devochat.exe --api-key your_api_key_here
   ```

2. **Run DevO Chat**:
   ```cmd
   # Using launcher script (recommended)
   launch_devochat.bat
   
   # Or run directly
   devochat.exe --repo-path .
   ```

### 💬 Usage Examples

```cmd
# Basic usage (analyze current directory)
devochat.exe --repo-path .

# With specific API key
devochat.exe --repo-path . --api-key YOUR_API_KEY

# Save session
devochat.exe --repo-path . --save-session my_session.json

# Load previous session
devochat.exe --repo-path . --load-session my_session.json

# Analyze different repository
devochat.exe --repo-path "C:\path\to\your\project"

# Show help
devochat.exe --help
```

### 🎯 Features

- **🤖 AI Assistant**: Gemini-powered code analysis and suggestions
- **📊 Repository Analysis**: Automatic language, framework, and dependency detection
- **🔧 Auto Setup**: Automatic repository setup with `setup <repo_url>`
- **🐳 Containerization**: Docker and deployment assistance
- **🔒 Security Analysis**: Vulnerability detection and fixes
- **📦 Dependency Management**: Missing package detection and resolution
- **💬 Natural Conversation**: Chat naturally about your development needs

### 🔧 System Requirements

- **Windows 10/11** (x64)
- **Internet connection** (for AI features)
- **Git** (optional, for auto setup feature)

### 🛠️ Troubleshooting

#### **"devochat.exe not found"**
- Ensure you're in the correct directory
- Check if the executable was built successfully

#### **"API key required"**
- Set the GEMINI_API_KEY environment variable
- Or create a .env file with your API key
- Or use the --api-key parameter

#### **"Permission denied"**
- Right-click on devochat.exe → Properties → Unblock
- Run as administrator if needed

#### **"Cannot analyze repository"**
- Ensure you have read permissions in the target directory
- Check if the path exists and is accessible

### 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Ensure your API key is valid and active
- Verify internet connection for AI features

### 🎉 Enjoy DevO Chat!

Your AI development assistant is ready to help with code analysis, dependency management, containerization, and more - all through natural conversation!
