@echo off
echo DevO Chat - AI Assistant for Development
echo =======================================
echo.

REM Check if uv is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: uv is not installed or not in PATH
    echo Please install uv first: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

echo Starting DevO Chat...
echo.
echo Available commands:
echo   - help        Show help
echo   - analyze     Analyze repository
echo   - suggest     Get suggestions  
echo   - deps        Check dependencies
echo   - security    Security analysis
echo   - containerize Help with Docker
echo   - context     Show repo context
echo   - exit        Exit chat
echo.

REM Start chat with current directory as repo path
uv run python repo_containerizer.py chat --repo-path . %*
