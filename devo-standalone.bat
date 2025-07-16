@echo off
echo DevO - AI-Powered Repository Containerizer (Standalone)
echo ======================================================
echo.

REM Check if uv is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: uv is not installed or not in PATH
    echo Please install uv first: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

echo Using uv to run DevO (standalone version)...
echo.

REM Run the standalone containerizer with all provided arguments
uv run python repocontainerizer.py %*
