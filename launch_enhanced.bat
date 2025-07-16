@echo off
title Enhanced DevO Chat - Local LLM Launcher
color 0a

:menu
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                    Enhanced DevO Chat - Local LLM Launcher                  ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo Select an option:
echo.
echo 1. 🚀 Quick Start (Auto-detect best AI)
echo 2. 🤖 Use Local LLM Only (CodeLlama)
echo 3. ☁️  Use Cloud AI Only (Gemini)
echo 4. 🔧 Run Automation Demo
echo 5. ⚙️  Setup Local LLM (First Time)
echo 6. 📚 View Documentation
echo 7. 🧪 Test Setup
echo 8. 🚪 Exit
echo.

set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" goto quickstart
if "%choice%"=="2" goto local
if "%choice%"=="3" goto cloud
if "%choice%"=="4" goto demo
if "%choice%"=="5" goto setup
if "%choice%"=="6" goto docs
if "%choice%"=="7" goto test
if "%choice%"=="8" goto exit
goto invalid

:quickstart
cls
echo Starting Enhanced DevO Chat (Auto-detect mode)...
echo.
python chat_enhanced.py
goto menu

:local
cls
echo Starting Enhanced DevO Chat (Local LLM Only)...
echo.
echo This will use CodeLlama 7B running locally on your machine.
echo First run may take a while to load the model.
echo.
python chat_enhanced.py --use-local
goto menu

:cloud
cls
echo Starting Enhanced DevO Chat (Cloud AI Only)...
echo.
echo This requires GEMINI_API_KEY environment variable.
echo.
if not defined GEMINI_API_KEY (
    echo ❌ GEMINI_API_KEY not found!
    echo.
    echo Please set your API key:
    set /p api_key="Enter your Gemini API key: "
    set GEMINI_API_KEY=%api_key%
)
python chat_enhanced.py
goto menu

:demo
cls
echo Starting Automation Demo...
echo.
echo This demonstrates code generation, fixing, and optimization.
echo.
python automation_demo.py
pause
goto menu

:setup
cls
echo Setting up Local LLM...
echo.
echo This will install dependencies and download CodeLlama model.
echo This may take 10-30 minutes depending on your internet speed.
echo.
set /p confirm="Continue with setup? (y/n): "
if /i "%confirm%"=="y" (
    python setup_local_llm.py
) else (
    echo Setup cancelled.
)
pause
goto menu

:docs
cls
echo Opening Documentation...
echo.
echo Available documentation files:
echo.
echo 1. LOCAL_LLM_GUIDE.md - Complete setup and usage guide
echo 2. CHAT_GUIDE.md - Original chat features
echo 3. README.md - Project overview
echo.
echo You can open these files in any text editor or markdown viewer.
echo.
pause
goto menu

:test
cls
echo Testing Setup...
echo.
echo Checking dependencies...
python -c "
import sys
print('Python version:', sys.version)
try:
    import torch
    print('✅ PyTorch:', torch.__version__)
    print('✅ CUDA available:', torch.cuda.is_available())
except ImportError:
    print('❌ PyTorch not installed')

try:
    import transformers
    print('✅ Transformers:', transformers.__version__)
except ImportError:
    print('❌ Transformers not installed')

try:
    import rich
    print('✅ Rich:', rich.__version__)
except ImportError:
    print('❌ Rich not installed')

try:
    import requests
    print('✅ Requests available')
except ImportError:
    print('❌ Requests not installed')
"

echo.
echo Checking Ollama...
ollama --version 2>nul
if %errorlevel% equ 0 (
    echo ✅ Ollama is installed
    
    echo Checking Ollama service...
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Ollama service is running
        
        echo Checking CodeLlama model...
        ollama list | findstr "codellama" >nul
        if %errorlevel% equ 0 (
            echo ✅ CodeLlama model is available
        ) else (
            echo ❌ CodeLlama model not found
            echo You can install it with: ollama pull codellama:7b-instruct
        )
    ) else (
        echo ❌ Ollama service not running
        echo Start it with: ollama serve
    )
) else (
    echo ❌ Ollama not installed
    echo Download from: https://ollama.ai/download
)

echo.
echo Checking environment variables...
if defined GEMINI_API_KEY (
    echo ✅ GEMINI_API_KEY is set
) else (
    echo ❌ GEMINI_API_KEY not set (optional for local-only use)
)

echo.
pause
goto menu

:invalid
cls
echo Invalid choice. Please select 1-8.
timeout /t 2 >nul
goto menu

:exit
cls
echo.
echo Thank you for using Enhanced DevO Chat!
echo.
echo Quick reminder:
echo • For local AI: python chat_enhanced.py --use-local
echo • For cloud AI: python chat_enhanced.py
echo • For automation: python automation_demo.py
echo.
echo Happy coding! 🚀
echo.
pause
exit /b 0
