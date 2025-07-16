@echo off
echo DevO Chat - Quick Launch (System Python)
echo ==========================================

cd /d "C:\DevO-Hackfinity"

REM Install to system Python
echo Installing dependencies to system Python...
python -m pip install --user rich pyyaml requests google-genai python-dotenv

REM Launch the enhanced chat system
echo.
echo ==========================================
echo Launching Enhanced DevO Chat (Interactive Mode)
echo ==========================================
echo.
python chat_enhanced.py --interactive

REM Keep window open on error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)
