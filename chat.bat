@echo off
echo DevO Chat - Unified AI Development Assistant
echo ==========================================
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
echo Repository will be analyzed automatically.
echo Chat naturally about your code and development needs!
echo.

REM Run the unified chat application
uv run python chat.py --repo-path .

echo.
echo Chat session ended. Thanks for using DevO!
pause
