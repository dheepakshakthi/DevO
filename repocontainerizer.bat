@echo off
setlocal enabledelayedexpansion

REM RepoContainerizer - Standalone CLI Application
REM Windows Command Line Interface

title RepoContainerizer

:main
cls
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🚀 RepoContainerizer                      ║
echo ║              AI-Powered Repository Containerization          ║
echo ║                     Standalone Version                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if the main script exists
if not exist "repocontainerizer.py" (
    echo ❌ repocontainerizer.py not found in current directory
    echo Please ensure you're running this from the correct directory
    pause
    exit /b 1
)

REM Main menu
echo What would you like to do?
echo.
echo 1. 🚀 Containerize a GitHub repository
echo 2. ⚙️  Setup and configuration
echo 3. 🔍 Validate a Dockerfile
echo 4. 📊 Show version and info
echo 5. 🏗️  Build standalone executable
echo 6. 📖 Show help
echo 7. 🚪 Exit
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto containerize
if "%choice%"=="2" goto setup
if "%choice%"=="3" goto validate
if "%choice%"=="4" goto version
if "%choice%"=="5" goto build
if "%choice%"=="6" goto help
if "%choice%"=="7" goto exit
goto invalid_choice

:containerize
echo.
echo 🚀 Repository Containerization
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
set /p repo_url="Enter GitHub repository URL: "
if "%repo_url%"=="" (
    echo ❌ Repository URL is required
    pause
    goto main
)

echo.
echo Options:
echo.
set /p output_dir="Output directory (press Enter for default): "
set /p format_type="Config format (yaml/json, press Enter for yaml): "
set /p validate_choice="Validate container after generation? (y/N): "

REM Build command
set "cmd=python repocontainerizer.py containerize "%repo_url%""

if not "%output_dir%"=="" (
    set "cmd=!cmd! --output "%output_dir%""
)

if not "%format_type%"=="" (
    set "cmd=!cmd! --format "%format_type%""
)

if /i "%validate_choice%"=="y" (
    set "cmd=!cmd! --validate"
)

echo.
echo 🔄 Running: !cmd!
echo.
!cmd!
echo.
echo ✅ Containerization process completed!
pause
goto main

:setup
echo.
echo ⚙️  Setup and Configuration
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
python repocontainerizer.py setup
pause
goto main

:validate
echo.
echo 🔍 Dockerfile Validation
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
set /p dockerfile_path="Enter path to Dockerfile: "
if "%dockerfile_path%"=="" (
    echo ❌ Dockerfile path is required
    pause
    goto main
)

echo.
python repocontainerizer.py validate "%dockerfile_path%"
pause
goto main

:version
echo.
echo 📊 Version Information
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
python repocontainerizer.py version
echo.
echo System Information:
echo Platform: %OS%
echo Architecture: %PROCESSOR_ARCHITECTURE%
echo Python Version:
python --version
echo.
pause
goto main

:build
echo.
echo 🏗️  Building Standalone Executable
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo This will create a standalone executable that can run without Python installed.
echo.
set /p confirm="Continue with build? (y/N): "
if not /i "%confirm%"=="y" goto main

echo.
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building executable...
python build_standalone.py

echo.
echo ✅ Build process completed!
echo Check the dist/ directory for the standalone executable.
pause
goto main

:help
echo.
echo 📖 Help and Usage
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
python repocontainerizer.py help
echo.
echo Windows-specific commands:
echo   repocontainerizer.bat    - This interactive menu
echo   build_standalone.py      - Create standalone executable
echo.
echo Configuration files are stored in:
echo   %USERPROFILE%\.repocontainerizer\
echo.
pause
goto main

:invalid_choice
echo.
echo ❌ Invalid choice. Please enter a number between 1-7.
pause
goto main

:exit
echo.
echo 👋 Thanks for using RepoContainerizer!
echo.
echo If you found this tool useful, please consider:
echo   - ⭐ Starring the repository
echo   - 🐛 Reporting issues
echo   - 💡 Suggesting improvements
echo.
pause
exit /b 0
