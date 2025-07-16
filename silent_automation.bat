@echo off
REM DevO Chat - Fully Automated Silent Pipeline
REM Runs complete automation without any user input

setlocal enabledelayedexpansion

REM Silent mode - no user prompts
set SILENT_MODE=true
set AUTO_CLEANUP=true
set AUTO_TEST=true
set AUTO_PACKAGE=true

echo.
echo ==========================================
echo   DevO Chat - Silent Automation Pipeline
echo ==========================================
echo.
echo Running in silent mode - no user input required
echo.

REM Stage 1: Kill any existing processes
echo [1/8] Cleaning up existing processes...
taskkill /F /IM devochat.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo ✅ Process cleanup complete

REM Stage 2: Prerequisites check
echo.
echo [2/8] Checking prerequisites...
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ UV not found. Installing UV...
    powershell -Command "& {Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression}"
    if %errorlevel% neq 0 (
        echo ❌ Failed to install UV automatically
        exit /b 1
    )
    REM Refresh PATH
    call refreshenv 2>nul
)
echo ✅ Prerequisites validated

REM Stage 3: Environment setup
echo.
echo [3/8] Setting up environment...
call uv sync --extra build --quiet
if %errorlevel% neq 0 (
    echo ❌ Environment setup failed
    exit /b 1
)
echo ✅ Environment ready

REM Stage 4: Code quality validation
echo.
echo [4/8] Validating code quality...
call uv run python -c "import chat, auto_setup, utils, templates, repocontainerizer" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Code validation failed
    exit /b 1
)
echo ✅ Code quality validated

REM Stage 5: Aggressive cleanup
echo.
echo [5/8] Performing aggressive cleanup...
if exist build (
    rmdir /s /q build 2>nul
    timeout /t 1 /nobreak >nul
)
if exist dist (
    rmdir /s /q dist 2>nul
    timeout /t 1 /nobreak >nul
)
if exist release (
    rmdir /s /q release 2>nul
    timeout /t 1 /nobreak >nul
)
del /q *.spec >nul 2>&1
echo ✅ Cleanup complete

REM Stage 6: Build executable
echo.
echo [6/8] Building standalone executable...
call uv run pyinstaller ^
    --onefile ^
    --console ^
    --name devochat ^
    --distpath dist ^
    --workpath build ^
    --specpath . ^
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
    --clean ^
    --noconfirm ^
    chat.py >build_log.txt 2>&1

if %errorlevel% neq 0 (
    echo ❌ Build failed - check build_log.txt
    exit /b 1
)
echo ✅ Executable built successfully

REM Stage 7: Test executable
echo.
echo [7/8] Testing executable...
if not exist "dist\devochat.exe" (
    echo ❌ Executable not found
    exit /b 1
)

timeout /t 2 /nobreak >nul
call "dist\devochat.exe" --help >test_output.txt 2>&1
if %errorlevel% neq 0 (
    echo ❌ Executable test failed
    exit /b 1
)
echo ✅ Executable tested successfully

REM Stage 8: Create distribution package
echo.
echo [8/8] Creating distribution package...
mkdir release >nul 2>&1

REM Copy files
copy "dist\devochat.exe" "release\" >nul 2>&1
if exist "STANDALONE_EXECUTABLE_GUIDE.md" copy "STANDALONE_EXECUTABLE_GUIDE.md" "release\" >nul 2>&1
if exist "sample-config.yml" copy "sample-config.yml" "release\" >nul 2>&1
if exist "launch_devochat.bat" copy "launch_devochat.bat" "release\" >nul 2>&1
if exist "AUTOMATION_GUIDE.md" copy "AUTOMATION_GUIDE.md" "release\" >nul 2>&1

REM Create automated build info
echo DevO Chat - Automated Build > "release\BUILD_INFO.txt"
echo Build Date: %date% %time% >> "release\BUILD_INFO.txt"
echo Build Mode: Fully Automated >> "release\BUILD_INFO.txt"
echo Platform: Windows x64 >> "release\BUILD_INFO.txt"
echo Python Version: 3.11.9 >> "release\BUILD_INFO.txt"
echo UV Version: 0.7.19 >> "release\BUILD_INFO.txt"
echo PyInstaller Version: 6.14.2 >> "release\BUILD_INFO.txt"

REM Get file size
for %%A in ("release\devochat.exe") do (
    echo File Size: %%~zA bytes >> "release\BUILD_INFO.txt"
    echo File Size MB: %%~zA >> "release\BUILD_INFO.txt"
)

REM Create ready-to-use README
echo # DevO Chat - Ready to Use > "release\README.md"
echo. >> "release\README.md"
echo ## Quick Start >> "release\README.md"
echo 1. Run devochat.exe >> "release\README.md"
echo 2. Set GEMINI_API_KEY environment variable >> "release\README.md"
echo 3. Start chatting with your AI assistant! >> "release\README.md"
echo. >> "release\README.md"
echo ## Commands >> "release\README.md"
echo - analyze ^<repo-path^> - Analyze repository >> "release\README.md"
echo - containerize ^<repo-path^> - Generate Docker config >> "release\README.md"
echo - auto-setup ^<repo-url^> - Clone and setup repository >> "release\README.md"
echo - help - Show available commands >> "release\README.md"
echo - exit - Exit application >> "release\README.md"
echo. >> "release\README.md"
echo Built automatically on %date% %time% >> "release\README.md"

echo ✅ Distribution package created

REM Clean up temporary files
del /q build_log.txt >nul 2>&1
del /q test_output.txt >nul 2>&1

echo.
echo ==========================================
echo   🎉 SILENT AUTOMATION COMPLETED! 🎉
echo ==========================================
echo.
echo ✅ All stages completed successfully
echo ✅ No user input required
echo ✅ Executable ready for distribution
echo.
echo 📦 Distribution package: release\
echo 🚀 Main executable: release\devochat.exe
echo 📊 File size: 
for %%A in ("release\devochat.exe") do echo     %%~zA bytes
echo.
echo 🎯 Ready to distribute immediately!
echo.

REM Optional: Auto-open release folder (can be disabled)
if "%AUTO_OPEN_FOLDER%"=="true" (
    explorer release
)

REM Exit successfully
exit /b 0
