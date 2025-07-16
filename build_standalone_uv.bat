@echo off
REM DevO Chat Standalone Executable Build Script (UV Version)
REM Creates a standalone .exe file using uv package manager

echo.
echo ============================================
echo   DevO Chat Standalone Executable Builder
echo   Using UV Package Manager
echo ============================================
echo.

REM Check if uv is available
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: uv is not installed or not in PATH
    echo Please install uv first: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python first: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ UV version: 
uv --version
echo ✅ Python version:
python --version
echo.

REM Install PyInstaller and build dependencies using uv
echo Installing PyInstaller and build dependencies...
uv add --dev pyinstaller
uv add --dev google-generativeai
uv add --dev rich
uv add --dev click
uv add --dev python-dotenv

REM Clean previous builds
echo Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Build the executable using uv run
echo Building DevO Chat executable...
echo This may take 5-10 minutes...
echo.

uv run pyinstaller devochat.spec --clean --noconfirm

REM Check if build was successful
if exist dist\devochat.exe (
    echo.
    echo ✅ Build successful!
    echo.
    echo 📁 Executable location: dist\devochat.exe
    echo 📦 Size: 
    dir dist\devochat.exe | findstr devochat.exe
    echo.
    echo 🚀 Testing executable...
    dist\devochat.exe --help
    echo.
    echo 🎉 DevO Chat standalone executable is ready!
    echo.
    echo 📋 Next steps:
    echo 1. Test: dist\devochat.exe --repo-path . --api-key YOUR_KEY
    echo 2. Distribute: Copy dist\devochat.exe to target systems
    echo 3. Use launch_devochat.bat for easy launching
    echo.
    echo 📁 Distribution files:
    echo   - dist\devochat.exe (main executable)
    echo   - launch_devochat.bat (launcher script)
    echo   - DISTRIBUTION_README.md (user guide)
    echo   - .env.example (configuration template)
    echo.
) else (
    echo.
    echo ❌ Build failed! Check the output above for errors.
    echo.
    echo 🔧 Troubleshooting:
    echo 1. Ensure all dependencies are installed
    echo 2. Check for any import errors in the code
    echo 3. Verify all required files exist
    echo 4. Try running: uv run python chat.py --help
    echo.
)

echo Build process complete!
pause
