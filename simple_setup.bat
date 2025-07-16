@echo off
REM Simple Setup Script for Enhanced DevO Chat
REM Handles Windows permission issues and virtual environment setup

echo.
echo ========================================
echo   Enhanced DevO Chat - Simple Setup
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges
) else (
    echo Note: Running without administrator privileges
    echo If you encounter permission errors, try running as administrator
    echo.
)

REM Kill any Python processes that might be using the venv
echo Stopping any running Python processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1

REM Wait a moment for processes to close
timeout /t 2 /nobreak >nul

REM Handle existing virtual environment
if exist "venv" (
    echo Virtual environment exists. Attempting to remove...
    
    REM Try to deactivate first
    if exist "venv\Scripts\deactivate.bat" (
        call venv\Scripts\deactivate.bat 2>nul
    )
    
    REM Force remove with retries
    for /l %%i in (1,1,3) do (
        echo Attempt %%i to remove virtual environment...
        rmdir /s /q venv >nul 2>&1
        if not exist "venv" goto create_venv
        timeout /t 2 /nobreak >nul
    )
    
    REM If still exists, try alternative method
    if exist "venv" (
        echo Using alternative removal method...
        rd venv /s /q >nul 2>&1
        if exist "venv" (
            echo WARNING: Could not fully remove existing venv
            echo Please manually delete the 'venv' folder and run this script again
            echo Or restart your computer and try again
            pause
            exit /b 1
        )
    )
)

:create_venv
echo Creating new virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Please ensure Python is installed and added to PATH
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
python -m pip install --upgrade pip

echo Installing core dependencies...
pip install rich>=13.0.0
if errorlevel 1 (
    echo ERROR: Failed to install rich
    pause
    exit /b 1
)

pip install click>=8.0.0
if errorlevel 1 (
    echo ERROR: Failed to install click
    pause
    exit /b 1
)

pip install python-dotenv>=1.0.0
if errorlevel 1 (
    echo ERROR: Failed to install python-dotenv
    pause
    exit /b 1
)

pip install requests>=2.28.0
if errorlevel 1 (
    echo ERROR: Failed to install requests
    pause
    exit /b 1
)

echo Installing Gemini API support...
pip install google-generativeai>=0.3.0
if errorlevel 1 (
    echo WARNING: Failed to install Gemini API support
    echo You can still use local AI
)

echo Installing basic AI dependencies...
pip install torch --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo WARNING: Failed to install PyTorch
    echo Local AI may not work properly
)

pip install transformers>=4.35.0
if errorlevel 1 (
    echo WARNING: Failed to install transformers
    echo Local AI may not work properly
)

echo.
echo ========================================
echo   Testing Installation
echo ========================================
echo.

REM Test basic imports
python -c "import rich; print('✅ Rich imported successfully')"
python -c "import click; print('✅ Click imported successfully')"
python -c "import requests; print('✅ Requests imported successfully')"

REM Test optional imports
python -c "import google.generativeai; print('✅ Gemini API available')" 2>nul || echo "⚠️  Gemini API not available (optional)"
python -c "import torch; print('✅ PyTorch available')" 2>nul || echo "⚠️  PyTorch not available (local AI disabled)"
python -c "import transformers; print('✅ Transformers available')" 2>nul || echo "⚠️  Transformers not available (local AI disabled)"

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.

echo 🎉 Enhanced DevO Chat setup completed!
echo.
echo To run the chat system:
echo 1. Make sure virtual environment is activated: venv\Scripts\activate
echo 2. Run: python chat_enhanced.py
echo.
echo For Gemini API (cloud AI):
echo - Set environment variable: set GEMINI_API_KEY=your_key_here
echo - Or create .env file with your API key
echo.
echo For local AI only:
echo - Run: python chat_enhanced.py --use-local
echo.
echo Test your setup:
echo - Run: python test_enhanced.py
echo.

pause
