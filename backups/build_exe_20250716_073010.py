#!/usr/bin/env python3
"""
Build Script for DevO Chat Standalone Executable
Creates a standalone .exe file that can run without Python installation
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import json

def create_spec_file():
    """Create PyInstaller spec file for DevO Chat"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['chat.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates.py', '.'),
        ('utils.py', '.'),
        ('auto_setup.py', '.'),
        ('*.md', '.'),
        ('requirements.txt', '.'),
        ('pyproject.toml', '.'),
    ],
    hiddenimports=[
        'google.generativeai',
        'google.ai.generativelanguage',
        'google.ai.generativelanguage_v1beta',
        'google.auth',
        'google.auth.transport',
        'google.oauth2',
        'google.protobuf',
        'rich',
        'rich.console',
        'rich.panel',
        'rich.table',
        'rich.markdown',
        'rich.syntax',
        'rich.progress',
        'rich.prompt',
        'rich.live',
        'rich.spinner',
        'rich.columns',
        'rich.layout',
        'rich.align',
        'rich.text',
        'click',
        'pathlib',
        'dotenv',
        'json',
        'datetime',
        'tempfile',
        'subprocess',
        'urllib.parse',
        'typing',
        'asyncio',
        'traceback',
        'shutil',
        'os',
        'sys',
        're',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='devochat',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
"""
    
    with open('devochat.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Created devochat.spec file")

def create_build_requirements():
    """Create requirements file for building"""
    build_requirements = """
# Build requirements for DevO Chat standalone executable
pyinstaller==6.3.0
google-generativeai>=0.3.0
rich>=13.0.0
click>=8.0.0
python-dotenv>=1.0.0
pathlib2>=2.3.0
requests>=2.28.0
urllib3>=1.26.0
certifi>=2022.12.7
charset-normalizer>=3.0.0
idna>=3.4
six>=1.16.0
protobuf>=4.21.0
grpcio>=1.50.0
grpcio-status>=1.50.0
googleapis-common-protos>=1.56.0
google-auth>=2.15.0
google-auth-oauthlib>=0.8.0
google-auth-httplib2>=0.1.0
httplib2>=0.20.0
oauth2lib>=4.1.0
pyasn1>=0.4.8
pyasn1-modules>=0.2.8
rsa>=4.9
cachetools>=5.2.0
"""
    
    with open('build-requirements.txt', 'w', encoding='utf-8') as f:
        f.write(build_requirements.strip())
    
    print("✅ Created build-requirements.txt")

def create_build_script():
    """Create build script for Windows"""
    build_script = """@echo off
REM DevO Chat Standalone Executable Build Script
REM Creates a standalone .exe file that can run without Python installation

echo.
echo ============================================
echo   DevO Chat Standalone Executable Builder
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python first: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Create virtual environment for building
echo Creating build environment...
python -m venv build_env
call build_env\\Scripts\\activate.bat

REM Install build dependencies
echo Installing build dependencies...
pip install -r build-requirements.txt

REM Clean previous builds
echo Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Build the executable
echo Building DevO Chat executable...
pyinstaller devochat.spec --clean --noconfirm

REM Check if build was successful
if exist dist\\devochat.exe (
    echo.
    echo ✅ Build successful!
    echo.
    echo 📁 Executable location: dist\\devochat.exe
    echo 📦 Size: 
    dir dist\\devochat.exe | findstr devochat.exe
    echo.
    echo 🚀 You can now distribute dist\\devochat.exe
    echo    It runs without requiring Python installation!
    echo.
    echo Usage: devochat.exe --help
    echo        devochat.exe --repo-path . 
    echo        devochat.exe --api-key YOUR_KEY
    echo.
) else (
    echo.
    echo ❌ Build failed! Check the output above for errors.
    echo.
)

REM Cleanup
call deactivate
echo.
echo Build process complete!
pause
"""
    
    with open('build_standalone.bat', 'w', encoding='utf-8') as f:
        f.write(build_script)
    
    print("✅ Created build_standalone.bat")

def create_launcher_script():
    """Create launcher script for the built executable"""
    launcher_script = """@echo off
REM DevO Chat Standalone Executable Launcher
REM Launches the standalone executable with proper configuration

echo.
echo ========================================
echo   DevO Chat - Standalone Executable
echo ========================================
echo.

REM Check if executable exists
if not exist "devochat.exe" (
    echo ERROR: devochat.exe not found!
    echo Please build the executable first using build_standalone.bat
    pause
    exit /b 1
)

REM Check for API key
if "%GEMINI_API_KEY%"=="" (
    echo WARNING: GEMINI_API_KEY environment variable not set
    echo You can:
    echo 1. Set environment variable: set GEMINI_API_KEY=your_key_here
    echo 2. Create .env file with: GEMINI_API_KEY=your_key_here
    echo 3. Use --api-key parameter: devochat.exe --api-key your_key_here
    echo.
)

echo Starting DevO Chat...
echo Repository: Current directory
echo.

REM Launch the executable
devochat.exe --repo-path . %*

echo.
echo DevO Chat session ended.
pause
"""
    
    with open('launch_devochat.bat', 'w', encoding='utf-8') as f:
        f.write(launcher_script)
    
    print("✅ Created launch_devochat.bat")

def create_distribution_readme():
    """Create README for distribution"""
    readme_content = """# DevO Chat - Standalone Executable

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
devochat.exe --repo-path "C:\\path\\to\\your\\project"

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

Your AI development assistant is ready to help with code analysis, dependency management,
    containerization, and more - all through natural conversation!
"""
    
    with open('DISTRIBUTION_README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ Created DISTRIBUTION_README.md")

def create_env_example():
    """Create example .env file for distribution"""
    env_content = """# DevO Chat Environment Configuration
# Copy this file to .env and add your API key

# Required: Your Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Default repository path
# DEFAULT_REPO_PATH=.

# Optional: Enable debug mode
# DEBUG=false
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Created .env.example")

def create_icon():
    """Create a simple icon for the executable"""
    print("ℹ️  For a custom icon, place icon.ico in the current directory")
    print("   The build script will automatically include it")

def main():
    """Main build preparation function"""
    print("🛠️  Preparing DevO Chat for standalone executable build...")
    print()
    
    # Create all necessary files
    create_spec_file()
    create_build_requirements()
    create_build_script()
    create_launcher_script()
    create_distribution_readme()
    create_env_example()
    create_icon()
    
    print()
    print("🎉 Build preparation complete!")
    print()
    print("📋 Next steps:")
    print("1. Run: build_standalone.bat")
    print("2. Wait for build to complete")
    print("3. Test: dist\\devochat.exe --help")
    print("4. Distribute: Copy dist\\devochat.exe to target systems")
    print()
    print("📁 Files created:")
    print("  - devochat.spec (PyInstaller specification)")
    print("  - build-requirements.txt (Build dependencies)")
    print("  - build_standalone.bat (Build script)")
    print("  - launch_devochat.bat (Launcher script)")
    print("  - DISTRIBUTION_README.md (User documentation)")
    print("  - .env.example (Environment configuration example)")
    print()
    print("💡 Tips:")
    print("  - Build process may take 5-10 minutes")
    print("  - Executable will be ~50-100MB")
    print("  - No Python installation required on target systems")
    print("  - Include launch_devochat.bat for user convenience")

if __name__ == '__main__':
    main()