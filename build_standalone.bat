@echo off
REM DevO Chat Standalone Executable Build Script
REM Creates a standalone .exe file that can run without Python installation

echo.
echo ============================================
echo   DevO Chat Standalone Executable Builder
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python first: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Create virtual environment for building
echo Creating build environment...
python -m venv build_env
call build_env\Scripts\activate.bat

REM Install build dependencies
echo Installing build dependencies...
pip install -r build-requirements.txt

REM Clean previous builds
echo Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM Build the executable
echo Building DevO Chat executable...
pyinstaller devochat.spec --clean --noconfirm

REM Check if build was successful
if exist dist\devochat.exe (
    echo.
    echo ✅ Build successful!
    echo.
    echo 📁 Executable location: dist\devochat.exe
    echo 📦 Size: 
    dir dist\devochat.exe | findstr devochat.exe
    echo.
    echo 🚀 You can now distribute dist\devochat.exe
    echo    It runs without requiring Python installation!
    echo.
    echo Usage: devochat.exe --help
    echo        devochat.exe --repo-path . 
    echo        devochat.exe --api-key YOUR_KEY
    echo.
) else (
    echo.
    echo ❌ Build failed! Check the output above for errors.
    echo.
)

REM Cleanup
call deactivate
echo.
echo Build process complete!
pause
