@echo off
echo DevO Chat - Enhanced Interactive Launch
echo ========================================

cd /d "C:\DevO-Hackfinity"

REM Check if virtual environment exists, create if not
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating Python environment...
call .venv\Scripts\activate.bat

REM Install required packages
echo Installing/updating dependencies...
pip install --upgrade rich pyyaml requests google-genai python-dotenv

REM Launch the enhanced chat system with interactive selection
echo.
echo ========================================
echo Launching Enhanced DevO Chat (Interactive Mode)
echo ========================================
echo.
python chat_enhanced.py --interactive

REM Keep window open on error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)
