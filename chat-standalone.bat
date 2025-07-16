@echo off
echo DevO Chat - Standalone Mode
echo ==========================
echo.

REM Check if uv is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: uv is not installed or not in PATH
    echo Please install uv first: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

echo Starting DevO Chat (Standalone)...
echo.

REM Run the standalone chat application
uv run python chat.py --repo-path . %*
