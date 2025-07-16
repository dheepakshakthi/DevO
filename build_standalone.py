        import PyInstaller
from pathlib import Path
import os
import platform
import shutil
import subprocess
import sys

#!/usr/bin/env python3
"""
Build script for creating standalone executables
"""


def install_pyinstaller():
    """Install PyInstaller if not available"""
    try:
        print("✅ PyInstaller is already installed")
        return True
    except ImportError:
        print("📦 Installing PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False

def build_executable():
# TODO: Consider breaking this function into smaller functions
    """Build standalone executable"""
    print("🔨 Building standalone executable...")
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "repocontainerizer",
        "--clean",
        "--noconfirm",
        "repocontainerizer.py"
    ]
    
    # Add Windows-specific options
    if platform.system() == "Windows":
        cmd.extend([
            "--console",
            "--icon=NONE"
        ])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e.stderr}")
        return False

def create_distribution():
# TODO: Consider breaking this function into smaller functions
    """Create distribution package"""
    print("📦 Creating distribution package...")
    
    # Create dist directory structure
    dist_dir = Path("dist/repocontainerizer")
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy executable
    exe_name = "repocontainerizer.exe" if platform.system() == "Windows" else "repocontainerizer"
    exe_path = Path("dist") / exe_name
    
    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir / exe_name)
        print(f"✅ Copied executable: {exe_name}")
    else:
        print(f"❌ Executable not found: {exe_path}")
        return False
    
    # Create documentation
    docs = [
        ("README.md", "README.md"),
        ("QUICK_START.md", "QUICK_START.md"),
        ("requirements.txt", "requirements.txt")
    ]
    
    for src, dst in docs:
        if Path(src).exists():
            shutil.copy2(src, dist_dir / dst)
            print(f"✅ Copied: {dst}")
    
    # Create installation script
    if platform.system() == "Windows":
        install_script = """@echo off
echo Installing RepoContainerizer...

REM Create installation directory
set INSTALL_DIR=%USERPROFILE%\\AppData\\Local\\RepoContainerizer
mkdir "%INSTALL_DIR%" 2>nul

REM Copy executable
copy "repocontainerizer.exe" "%INSTALL_DIR%\\" >nul

REM Add to PATH (requires admin privileges)
echo Adding to PATH...
setx PATH "%PATH%;%INSTALL_DIR%"

echo.
echo ✅ Installation complete!
echo.
echo You can now use 'repocontainerizer' from anywhere in the command line.
echo.
echo To get started:
echo   repocontainerizer setup
echo   repocontainerizer containerize https://github.com/owner/repo
echo.
pause
"""
        with open(dist_dir / "install.bat", "w") as f:
            f.write(install_script)
    else:
        install_script = """#!/bin/bash
echo "Installing RepoContainerizer..."

# Create installation directory
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# Copy executable
cp "repocontainerizer" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/repocontainerizer"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Restart your terminal or run: source ~/.bashrc"
echo ""
echo "You can now use 'repocontainerizer' from anywhere in the command line."
echo ""
echo "To get started:"
echo "  repocontainerizer setup"
echo "  repocontainerizer containerize https://github.com/owner/repo"
echo ""
"""
        with open(dist_dir / "install.sh", "w") as f:
            f.write(install_script)
        
        # Make install script executable
        os.chmod(dist_dir / "install.sh", 0o755)
    
    # Create usage guide
    usage_guide = f"""# RepoContainerizer - Standalone Application

## Quick Start

### 1. Installation
Run the installation script:
- Windows: Double-click `install.bat`
- Linux/Mac: Run `./install.sh`

### 2. Setup
```bash
repocontainerizer setup
```

### 3. Usage
```bash
# Containerize a repository
repocontainerizer containerize https://github.com/owner/repo

# With options
repocontainerizer containerize https://github.com/owner/repo --output ./containers --validate

# Get help
repocontainerizer help
```

## Commands

- `containerize <repo_url>` - Containerize a GitHub repository
- `config` - Manage configuration
- `validate <dockerfile>` - Validate a Dockerfile
- `setup` - Interactive setup
- `version` - Show version
- `help` - Show help

## Configuration

The tool stores configuration in:
- Windows: `%USERPROFILE%\\.repocontainerizer\\config.json`
- Linux/Mac: `~/.repocontainerizer/config.json`

## Requirements

- Internet connection for GitHub repository access
- Docker (optional, for validation)
- Gemini API key (get from https://makersuite.google.com/app/apikey)

## Support

For issues and support, visit: https://github.com/your-username/repocontainerizer
"""
    
    with open(dist_dir / "USAGE.md", "w") as f:
        f.write(usage_guide)
    
    print(f"✅ Distribution package created: {dist_dir}")
    return True

def main():
    """Main build process"""
    print("🚀 RepoContainerizer Build Process")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("repocontainerizer.py").exists():
        print("❌ repocontainerizer.py not found in current directory")
        sys.exit(1)
    
    # Install PyInstaller
    if not install_pyinstaller():
        sys.exit(1)
    
    # Build executable
    if not build_executable():
        sys.exit(1)
    
    # Create distribution
    if not create_distribution():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Build Complete!")
    print("=" * 50)
    
    # Show results
    dist_dir = Path("dist/repocontainerizer")
    print(f"📦 Distribution package: {dist_dir}")
    print("\nFiles created:")
    for file in dist_dir.iterdir():
        print(f"  📄 {file.name}")
    
    print(f"\n🎯 Next steps:")
    print(f"1. Navigate to: {dist_dir}")
    print(f"2. Run installation script")
    print(f"3. Use 'repocontainerizer setup' to configure")
    print(f"4. Start containerizing repositories!")

if __name__ == "__main__":
    main()