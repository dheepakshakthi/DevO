@echo off
title DevO Unified Chat Assistant
cls

echo.
echo ========================================
echo     DevO Unified Chat Assistant
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment not found. Creating...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        echo [INFO] Please ensure Python is installed and available in PATH
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import rich, click, google.generativeai, psutil" 2>nul
if errorlevel 1 (
    echo [INFO] Installing required dependencies...
    echo [INFO] This may take a few minutes...
    pip install --upgrade pip
    pip install rich click google-generativeai psutil python-dotenv requests
    
    REM Try to install PyTorch with CUDA support
    echo [INFO] Installing PyTorch with CUDA support...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    
    REM Install transformers and accelerate for local LLM support
    echo [INFO] Installing transformers and accelerate...
    pip install transformers accelerate
    
    if errorlevel 1 (
        echo [WARNING] Some dependencies may have failed to install
        echo [INFO] The assistant will still work with basic functionality
    )
)

REM Check for Gemini API key
if "%GEMINI_API_KEY%"=="" (
    if not exist ".env" (
        echo [WARNING] No Gemini API key found
        echo [INFO] You can either:
        echo   1. Set GEMINI_API_KEY environment variable
        echo   2. Create a .env file with GEMINI_API_KEY=your_key_here
        echo   3. Use local LLM only mode
        echo.
    )
)

REM Check for CUDA availability
echo [INFO] Checking GPU support...
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU Only\"}')" 2>nul

echo.
echo [INFO] Starting DevO Unified Chat Assistant...
echo.

REM Run the unified chat
python unified_chat.py

if errorlevel 1 (
    echo.
    echo [ERROR] Application encountered an error
    echo [INFO] Check the error message above for details
    pause
) else (
    echo.
    echo [INFO] Application closed normally
)

pause
