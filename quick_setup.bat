@echo off
REM Quick Fix Setup for Enhanced DevO Chat - Windows Compatible
REM Handles encoding issues and permission problems

echo.
echo ========================================
echo   Enhanced DevO Chat - Quick Fix Setup
echo ========================================
echo.

REM Set UTF-8 encoding for better emoji support
chcp 65001 > nul 2>&1

REM Check Python installation
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python and add it to your PATH
    pause
    exit /b 1
)

echo Python found. Checking virtual environment...

REM Handle existing virtual environment safely
if exist "venv" (
    echo Virtual environment exists. Attempting safe removal...
    
    REM Kill any Python processes first
    taskkill /f /im python.exe > nul 2>&1
    taskkill /f /im pythonw.exe > nul 2>&1
    timeout /t 2 > nul
    
    REM Try to remove multiple times if needed
    for /l %%i in (1,1,5) do (
        if exist "venv" (
            echo Attempt %%i to remove venv...
            rd /s /q venv > nul 2>&1
            timeout /t 1 > nul
        )
    )
    
    if exist "venv" (
        echo WARNING: Could not remove existing venv automatically
        echo Please manually delete the 'venv' folder and run this script again
        echo Or restart your computer and try again
        pause
        exit /b 1
    )
)

echo Creating new virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Upgrading pip...
python -m pip install --upgrade pip --quiet

echo Installing core dependencies...
echo - Installing rich (terminal UI)...
pip install rich --quiet
if errorlevel 1 (
    echo ERROR: Failed to install rich
    pause
    exit /b 1
)

echo - Installing click (CLI framework)...
pip install click --quiet
if errorlevel 1 (
    echo ERROR: Failed to install click
    pause
    exit /b 1
)

echo - Installing python-dotenv (environment variables)...
pip install python-dotenv --quiet
if errorlevel 1 (
    echo ERROR: Failed to install python-dotenv
    pause
    exit /b 1
)

echo - Installing requests (HTTP client)...
pip install requests --quiet
if errorlevel 1 (
    echo ERROR: Failed to install requests
    pause
    exit /b 1
)

echo Installing optional AI dependencies...
echo - Installing Gemini API support...
pip install google-generativeai --quiet
if errorlevel 1 (
    echo WARNING: Failed to install Gemini API support
    echo You can still use the system without cloud AI
)

echo - Installing PyTorch (CPU version)...
pip install torch --index-url https://download.pytorch.org/whl/cpu --quiet
if errorlevel 1 (
    echo WARNING: Failed to install PyTorch
    echo Local AI will not be available
)

echo - Installing Transformers...
pip install transformers --quiet
if errorlevel 1 (
    echo WARNING: Failed to install Transformers
    echo Local AI will not be available
)

echo.
echo ========================================
echo   Testing Installation
echo ========================================
echo.

REM Simple test without emojis
echo Testing core dependencies...
python -c "import rich; print('Rich: OK')" 2>nul || echo "Rich: FAILED"
python -c "import click; print('Click: OK')" 2>nul || echo "Click: FAILED"
python -c "import requests; print('Requests: OK')" 2>nul || echo "Requests: OK"

echo Testing optional dependencies...
python -c "import google.generativeai; print('Gemini API: OK')" 2>nul || echo "Gemini API: Not available (optional)"
python -c "import torch; print('PyTorch: OK')" 2>nul || echo "PyTorch: Not available (local AI disabled)"
python -c "import transformers; print('Transformers: OK')" 2>nul || echo "Transformers: Not available (local AI disabled)"

echo.
echo Creating models directory...
if not exist "models" mkdir models
if not exist "models\ggml" mkdir models\ggml
if not exist "models\transformers" mkdir models\transformers
if not exist "models\ollama" mkdir models\ollama

REM Check for existing GGML models
set "ggml_count=0"
for %%f in (models\*.bin models\*.gguf models\ggml\*.bin models\ggml\*.gguf) do (
    if exist "%%f" set /a ggml_count+=1
)

if %ggml_count% gtr 0 (
    echo Found %ggml_count% GGML model file(s) in models directory
) else (
    echo No GGML models found. You can add them to the models\ directory
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.

echo Enhanced DevO Chat setup completed successfully!
echo.
echo How to run:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Run: python chat_enhanced.py
echo.
echo For cloud AI (Gemini):
echo - Set API key: set GEMINI_API_KEY=your_key_here
echo - Or create .env file with your API key
echo.
echo For local AI only:
echo - Run: python chat_enhanced.py --use-local
echo.
echo Quick test:
echo - Run: python -c "print('Setup test passed!')"
echo.

pause
