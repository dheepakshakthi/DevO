# DevO Chat Standalone Executable - UV Build Guide

## 🚀 **Building Standalone Executable with UV**

This guide shows you how to create a standalone `.exe` file of DevO Chat using the UV package manager.

### 📋 **Prerequisites**

1. **UV Package Manager** - Install from https://docs.astral.sh/uv/getting-started/installation/
2. **Python 3.11+** - Install from https://www.python.org/downloads/
3. **Git** (optional) - For version control

### 🛠️ **Build Process**

#### **Step 1: Prepare Build Environment**
```cmd
# Ensure UV is working
uv --version

# Check Python version
python --version
```

#### **Step 2: Run Build Script**
```cmd
# Use the UV-specific build script
.\build_standalone_uv.bat
```

#### **Step 3: Alternative Manual Build**
If you prefer manual control:
```cmd
# Install build dependencies
uv add --dev pyinstaller
uv add --dev google-generativeai
uv add --dev rich
uv add --dev click
uv add --dev python-dotenv

# Clean previous builds
rmdir /s /q dist
rmdir /s /q build

# Build executable
uv run pyinstaller devochat.spec --clean --noconfirm
```

### 📁 **Build Output**

After successful build:
```
dist/
├── devochat.exe          # Main executable (~50-100MB)
├── launch_devochat.bat   # Launcher script
├── DISTRIBUTION_README.md # User documentation
└── .env.example         # Configuration template
```

### 🎯 **Testing the Executable**

```cmd
# Test help command
dist\devochat.exe --help

# Test with current directory
dist\devochat.exe --repo-path . --api-key YOUR_API_KEY

# Test auto setup feature
dist\devochat.exe --repo-path . --api-key YOUR_API_KEY
# Then in chat: setup https://github.com/user/repo.git
```

### 📦 **Distribution Package**

Create a distribution folder:
```cmd
mkdir devochat_distribution
copy dist\devochat.exe devochat_distribution\
copy launch_devochat.bat devochat_distribution\
copy DISTRIBUTION_README.md devochat_distribution\README.md
copy .env.example devochat_distribution\
```

### 🎪 **Advanced Build Options**

#### **Custom Icon**
1. Place `icon.ico` in the project directory
2. The build script will automatically include it

#### **Build with UPX Compression**
```cmd
# Install UPX compressor
# Download from https://upx.github.io/
# Add to PATH

# Build with compression (smaller file size)
uv run pyinstaller devochat.spec --clean --noconfirm --upx-dir="C:\path\to\upx"
```

#### **Debug Build**
```cmd
# Build with debug information
uv run pyinstaller devochat.spec --clean --noconfirm --debug
```

### 🔧 **Build Troubleshooting**

#### **Common Issues**

1. **"uv not found"**
   ```cmd
   # Install UV
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **"PyInstaller not found"**
   ```cmd
   # Install PyInstaller
   uv add --dev pyinstaller
   ```

3. **"Module not found" errors**
   ```cmd
   # Install missing dependencies
   uv add --dev [missing_module]
   ```

4. **"Permission denied"**
   ```cmd
   # Run as administrator
   # Or check antivirus settings
   ```

5. **Large executable size**
   ```cmd
   # Use UPX compression
   # Or exclude unnecessary modules in devochat.spec
   ```

#### **Build Optimization**

Edit `devochat.spec` to optimize:
```python
# Exclude unnecessary modules
excludes=[
    'tkinter',
    'matplotlib',
    'numpy',
    'scipy',
    'pandas'
]

# Add missing hidden imports
hiddenimports=[
    'your_missing_module'
]
```

### 🚀 **Deployment Options**

#### **Single File Distribution**
```cmd
# Just distribute devochat.exe
# Users need to set GEMINI_API_KEY environment variable
```

#### **Complete Package**
```cmd
# Distribute folder with:
# - devochat.exe
# - launch_devochat.bat
# - README.md
# - .env.example
```

#### **Installer Creation**
Use tools like:
- **Inno Setup** - Free installer creator
- **NSIS** - Nullsoft Scriptable Install System
- **Advanced Installer** - Professional installer

### 📊 **Build Performance**

| Aspect | Details |
|--------|---------|
| Build Time | 5-10 minutes |
| Executable Size | 50-100MB |
| Startup Time | 2-5 seconds |
| Memory Usage | 50-150MB |
| Dependencies | None (standalone) |

### 🎁 **Features in Standalone Executable**

✅ **Full DevO Chat functionality**
✅ **AI-powered code analysis**
✅ **Repository auto-setup**
✅ **Dependency management**
✅ **Natural language chat**
✅ **No Python installation required**
✅ **Portable single file**
✅ **Windows 10/11 compatible**

### 🎯 **Usage Examples**

```cmd
# Basic usage
devochat.exe --repo-path "C:\MyProject"

# With API key
devochat.exe --repo-path . --api-key "your_api_key"

# Save session
devochat.exe --repo-path . --save-session session.json

# Load session
devochat.exe --repo-path . --load-session session.json

# Show help
devochat.exe --help
```

### 🔒 **Security Considerations**

- **API Key**: Never embed API keys in the executable
- **Environment Variables**: Use environment variables or .env files
- **Code Signing**: Consider signing the executable for trust
- **Antivirus**: Some antivirus may flag PyInstaller executables

### 📞 **Support & Troubleshooting**

If you encounter issues:
1. Check the build output for specific errors
2. Verify all dependencies are installed
3. Test the Python version works: `uv run python chat.py --help`
4. Check Windows compatibility
5. Verify API key is set correctly

The standalone executable makes DevO Chat easily distributable and usable on any Windows system without requiring Python installation! 🎉
