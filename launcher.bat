@echo off
echo.
echo ===============================================
echo   RepoContainerizer - AI-Powered Containerization
echo ===============================================
echo.

REM Check if API key is set
if "%GEMINI_API_KEY%"=="" (
    echo ❌ GEMINI_API_KEY environment variable is not set
    echo.
    echo Please set your API key:
    echo set GEMINI_API_KEY=your_api_key_here
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Show menu
echo What would you like to do?
echo.
echo 1. Containerize a GitHub repository
echo 2. Validate a Dockerfile
echo 3. Setup and test environment
echo 4. Run example
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto containerize
if "%choice%"=="2" goto validate
if "%choice%"=="3" goto setup
if "%choice%"=="4" goto example
if "%choice%"=="5" goto exit
goto invalid

:containerize
echo.
set /p repo_url="Enter GitHub repository URL: "
if "%repo_url%"=="" (
    echo ❌ Repository URL is required
    pause
    goto menu
)
echo.
echo 🚀 Containerizing repository...
python repo_containerizer.py containerize "%repo_url%" --output ./output
echo.
echo ✅ Done! Check the ./output directory for generated files.
pause
goto menu

:validate
echo.
set /p dockerfile_path="Enter path to Dockerfile: "
if "%dockerfile_path%"=="" (
    echo ❌ Dockerfile path is required
    pause
    goto menu
)
echo.
echo 🔍 Validating Dockerfile...
python repo_containerizer.py validate "%dockerfile_path%"
pause
goto menu

:setup
echo.
echo 🔧 Setting up and testing environment...
python repo_containerizer.py setup
echo.
echo 🧪 Running tests...
python test_containerizer.py
pause
goto menu

:example
echo.
echo 🎯 Running example...
python example.py
pause
goto menu

:invalid
echo.
echo ❌ Invalid choice. Please enter 1-5.
pause
goto menu

:exit
echo.
echo 👋 Thanks for using RepoContainerizer!
pause
exit /b 0

:menu
echo.
echo Press any key to continue...
pause >nul
goto start

:start
cls
goto menu
