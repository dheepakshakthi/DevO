@echo off
echo Installing RepoContainerizer...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: pip is not installed or not in PATH
    pause
    exit /b 1
)

REM Install required packages
echo Installing Python dependencies...
pip install -r requirements.txt

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: Git is not installed or not in PATH
    echo Please install Git for repository cloning functionality
)

REM Check if docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: Docker is not installed or not in PATH
    echo Please install Docker for container validation functionality
)

REM Set up environment variable
echo.
echo Setup complete!
echo.
echo To use RepoContainerizer, set your Gemini API key:
echo set GEMINI_API_KEY=your_api_key_here
echo.
echo Then run:
echo python repo_containerizer.py --help
echo.
pause
