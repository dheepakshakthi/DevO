@echo off
REM Enhanced DevO Chat - Final Launcher
REM Fixed for Windows with proper Python detection

echo.
echo ========================================
echo   Enhanced DevO Chat - Ready to Use!
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 > nul 2>&1

REM Find Python using py launcher (recommended for Windows)
echo Checking Python installation...
py --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python launcher not found!
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

py --version
echo.

REM Quick dependency check
echo Checking dependencies...
py -c "import rich, google.generativeai, click, requests; print('✓ All core dependencies available')" 2>nul
if %errorlevel% neq 0 (
    echo Installing missing dependencies...
    py -m pip install --user rich click requests google-generativeai python-dotenv
)

REM Check for API key
if not defined GEMINI_API_KEY (
    if exist ".env" (
        echo ✓ Found .env file for configuration
    ) else (
        echo.
        echo 📝 NOTE: No GEMINI_API_KEY found
        echo    For cloud AI features, either:
        echo    1. Set environment variable: set GEMINI_API_KEY=your_key
        echo    2. Create .env file with: GEMINI_API_KEY=your_key
        echo    3. Use local AI only (no API key needed)
        echo.
    )
)

REM Show options menu
echo ========================================
echo   Choose your AI mode:
echo ========================================
echo.
echo 1. 🤖 Enhanced Chat (Auto-detect AI)
echo 2. ☁️  Cloud AI only (Gemini - requires API key)
echo 3. 🏠 Local AI only (no API key needed)
echo 4. 📜 Original chat.py (basic Gemini)
echo 5. 🔧 Test installation
echo 6. ❌ Exit
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Starting Enhanced DevO Chat in auto-detect mode...
    py chat_enhanced.py
) else if "%choice%"=="2" (
    if not defined GEMINI_API_KEY (
        echo.
        echo ❌ ERROR: GEMINI_API_KEY not set!
        echo Please set your API key first: set GEMINI_API_KEY=your_key
        pause
        exit /b 1
    )
    echo.
    echo ☁️ Starting Enhanced DevO Chat with Cloud AI...
    py chat_enhanced.py --api-key %GEMINI_API_KEY%
) else if "%choice%"=="3" (
    echo.
    echo 🏠 Starting Enhanced DevO Chat with Local AI...
    echo Note: Local AI requires additional setup (Ollama or local models)
    py chat_enhanced.py --use-local
) else if "%choice%"=="4" (
    echo.
    echo 📜 Starting original chat.py...
    py chat.py
) else if "%choice%"=="5" (
    echo.
    echo 🔧 Testing installation...
    echo.
    py -c "print('✓ Python:', __import__('sys').version.split()[0])"
    py -c "import rich; print('✓ Rich UI library')"
    py -c "import google.generativeai; print('✓ Google Gemini API')"
    py -c "import click; print('✓ Click CLI framework')"
    py -c "import requests; print('✓ HTTP requests library')"
    echo.
    echo ✅ All dependencies are working!
    if exist "chat_enhanced.py" (
        echo ✅ Enhanced chat system available
    ) else (
        echo ❌ Enhanced chat system not found
    )
    if exist "chat.py" (
        echo ✅ Original chat system available
    ) else (
        echo ❌ Original chat system not found
    )
    echo.
    pause
    goto menu
) else if "%choice%"=="6" (
    echo.
    echo 👋 Goodbye! Thanks for using DevO Chat!
    exit /b 0
) else (
    echo.
    echo ❌ Invalid choice. Starting enhanced chat in auto-detect mode...
    py chat_enhanced.py
)

REM Handle errors
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Chat system failed to start
    echo.
    echo 🔧 Troubleshooting steps:
    echo 1. Run option 5 to test installation
    echo 2. Check if you have internet connection
    echo 3. For local AI: install Ollama or local models
    echo 4. For cloud AI: verify your GEMINI_API_KEY
    echo.
    pause
)

:menu
REM Allow user to return to menu
echo.
echo Press any key to return to menu, or Ctrl+C to exit...
pause > nul
cls
goto :eof

echo.
echo 📱 Session ended. Thank you for using DevO Chat!
pause > nul
