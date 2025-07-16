@echo off
REM DevO Chat Standalone Executable Launcher
REM Launches the standalone executable with proper configuration

echo.
echo ========================================
echo   DevO Chat - Standalone Executable
echo ========================================
echo.

REM Check if executable exists
if not exist "devochat.exe" (
    echo ERROR: devochat.exe not found!
    echo Please build the executable first using build_standalone.bat
    pause
    exit /b 1
)

REM Check for API key
if "%GEMINI_API_KEY%"=="" (
    echo WARNING: GEMINI_API_KEY environment variable not set
    echo You can:
    echo 1. Set environment variable: set GEMINI_API_KEY=your_key_here
    echo 2. Create .env file with: GEMINI_API_KEY=your_key_here
    echo 3. Use --api-key parameter: devochat.exe --api-key your_key_here
    echo.
)

echo Starting DevO Chat...
echo Repository: Current directory
echo.

REM Launch the executable
devochat.exe --repo-path . %*

echo.
echo DevO Chat session ended.
pause
