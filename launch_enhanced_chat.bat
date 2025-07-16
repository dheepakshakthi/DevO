@echo off
REM Enhanced DevO Chat Launcher - GPU Support
REM Combines Gemini API with Local LLM and Automation

echo.
echo ========================================
echo   Enhanced DevO Chat Launcher
echo   AI Development Assistant
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo Please ensure Python is installed and added to PATH
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import rich, click" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements_unified.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Set default environment variables if not exists
if not defined GEMINI_API_KEY (
    echo.
    echo WARNING: GEMINI_API_KEY not set
    echo You can either:
    echo 1. Set environment variable: set GEMINI_API_KEY=your_key_here
    echo 2. Create .env file with: GEMINI_API_KEY=your_key_here
    echo 3. Use local AI only with --use-local flag
    echo.
)

REM GPU Detection and Setup
echo Checking GPU availability...
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU Count: {torch.cuda.device_count()}' if torch.cuda.is_available() else 'Using CPU')" 2>nul

echo.
echo ========================================
echo   Starting Enhanced DevO Chat
echo ========================================
echo.

REM Parse command line arguments
set "ARGS="
set "USE_LOCAL="
set "MODEL="
set "REPO_PATH=."

:parse_args
if "%~1"=="" goto run_chat
if "%~1"=="--local" set "USE_LOCAL=--use-local"
if "%~1"=="-l" set "USE_LOCAL=--use-local"
if "%~1"=="--model" (
    shift
    set "MODEL=--local-model %~1"
)
if "%~1"=="--repo" (
    shift
    set "REPO_PATH=%~1"
)
if "%~1"=="--help" (
    python chat_enhanced.py --help
    pause
    exit /b 0
)
shift
goto parse_args

:run_chat
REM Run the enhanced chat system
python chat_enhanced.py --repo-path "%REPO_PATH%" %USE_LOCAL% %MODEL%

if errorlevel 1 (
    echo.
    echo ERROR: Chat session failed
    echo Check the error messages above
    echo.
    pause
)

echo.
echo ========================================
echo   Session Ended
echo ========================================
pause
