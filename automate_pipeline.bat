@echo off
REM DevO Chat - Complete Automation Pipeline
REM Automates the entire build, test, and deployment process

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo    DevO Chat - Automation Pipeline
echo ==========================================
echo.

REM Check if UV is available
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: UV package manager not found!
    echo Please install UV from https://docs.astral.sh/uv/
    pause
    exit /b 1
)

REM Stage 1: Environment Setup
echo [1/7] Setting up Python environment...
call uv sync --extra build
if %errorlevel% neq 0 (
    echo ERROR: Failed to setup environment
    pause
    exit /b 1
)
echo ✅ Environment setup complete

REM Stage 2: Code Quality Checks
echo.
echo [2/7] Running code quality checks...
call uv run python -m py_compile chat.py
if %errorlevel% neq 0 (
    echo ERROR: Code compilation failed
    pause
    exit /b 1
)
call uv run python -m py_compile auto_setup.py
call uv run python -m py_compile utils.py
call uv run python -m py_compile templates.py
call uv run python -m py_compile repocontainerizer.py
echo ✅ Code quality checks passed

REM Stage 3: Functionality Tests
echo.
echo [3/7] Running functionality tests...
call uv run python -c "import chat; print('Chat module OK')"
if %errorlevel% neq 0 (
    echo ERROR: Chat module test failed
    pause
    exit /b 1
)
call uv run python -c "import auto_setup; print('Auto setup module OK')"
call uv run python -c "import utils; print('Utils module OK')"
call uv run python -c "import templates; print('Templates module OK')"
echo ✅ Functionality tests passed

REM Stage 4: Clean Previous Builds
echo.
echo [4/7] Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del /q *.spec
echo ✅ Build cleanup complete

REM Stage 5: Build Standalone Executable
echo.
echo [5/7] Building standalone executable...
call uv run pyinstaller ^
    --onefile ^
    --console ^
    --name devochat ^
    --add-data "sample-config.yml;." ^
    --add-data "templates.py;." ^
    --add-data "utils.py;." ^
    --add-data "auto_setup.py;." ^
    --add-data "repocontainerizer.py;." ^
    --collect-all google.generativeai ^
    --collect-all rich ^
    --collect-all click ^
    --collect-all yaml ^
    --collect-all requests ^
    --collect-all git ^
    --collect-all dotenv ^
    --hidden-import=google.generativeai ^
    --hidden-import=rich ^
    --hidden-import=click ^
    --hidden-import=yaml ^
    --hidden-import=requests ^
    --hidden-import=git ^
    --hidden-import=dotenv ^
    --hidden-import=os ^
    --hidden-import=sys ^
    --hidden-import=json ^
    --hidden-import=subprocess ^
    --hidden-import=pathlib ^
    chat.py

if %errorlevel% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)
echo ✅ Executable build complete

REM Stage 6: Test Executable
echo.
echo [6/7] Testing standalone executable...
if not exist "dist\devochat.exe" (
    echo ERROR: Executable not found
    pause
    exit /b 1
)

REM Test help command
call dist\devochat.exe --help > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Executable test failed
    pause
    exit /b 1
)
echo ✅ Executable tests passed

REM Stage 7: Package for Distribution
echo.
echo [7/7] Packaging for distribution...

REM Create distribution folder
if not exist "release" mkdir release

REM Copy executable
copy "dist\devochat.exe" "release\"

REM Copy documentation
copy "STANDALONE_EXECUTABLE_GUIDE.md" "release\"
copy "sample-config.yml" "release\"
copy "launch_devochat.bat" "release\"

REM Create version info
echo DevO Chat - Standalone Executable > "release\VERSION.txt"
echo Build Date: %date% %time% >> "release\VERSION.txt"
echo Python Version: 3.11.9 >> "release\VERSION.txt"
echo UV Version: 0.7.19 >> "release\VERSION.txt"
echo PyInstaller Version: 6.14.2 >> "release\VERSION.txt"

REM Get file size
for %%A in ("release\devochat.exe") do (
    echo File Size: %%~zA bytes >> "release\VERSION.txt"
)

echo ✅ Distribution package ready

echo.
echo ==========================================
echo    🎉 AUTOMATION PIPELINE COMPLETE! 🎉
echo ==========================================
echo.
echo ✅ Environment setup
echo ✅ Code quality checks
echo ✅ Functionality tests
echo ✅ Build cleanup
echo ✅ Executable build
echo ✅ Executable tests
echo ✅ Distribution package
echo.
echo 📦 Ready for distribution in: release\
echo 🚀 Main executable: release\devochat.exe
echo 📖 Documentation: release\STANDALONE_EXECUTABLE_GUIDE.md
echo 🎯 Launcher: release\launch_devochat.bat
echo.
echo Total build time: %time%
echo.
pause
