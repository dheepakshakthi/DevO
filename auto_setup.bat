@echo off
REM DevO Auto Setup - Automatic Repository Setup with AI
REM Clones repository, installs dependencies, and fixes errors automatically

echo.
echo =============================================
echo   DevO Auto Setup - AI-Powered Repository Setup
echo =============================================
echo.

if "%1"=="" (
    echo Usage: %0 ^<repository_url^>
    echo.
    echo Example: %0 https://github.com/user/repo.git
    echo.
    echo Features:
    echo   - Automatic repository cloning
    echo   - Language and framework detection
    echo   - Dependency installation with error correction
    echo   - AI-powered issue fixing
    echo   - Setup validation and reporting
    echo.
    pause
    exit /b 1
)

REM Check if uv is available
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: uv is not installed or not in PATH
    echo Please install uv first: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

echo Repository URL: %1
echo Starting automatic setup...
echo.

REM Run the auto setup
uv run python auto_setup.py %1

echo.
echo Auto setup completed!
echo You can now use the repository or run DevO chat for AI assistance.
pause
