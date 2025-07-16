@echo off
REM DevO Chat - Direct Launcher
REM Bypass virtual environment issues

echo.
echo ========================================
echo   DevO Chat - Direct Launch
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 > nul 2>&1

REM Check for different Python installations
echo Checking Python installations...

REM Use py launcher (recommended for Windows)
where py > nul 2>&1
if %errorlevel% equ 0 (
    echo Found py launcher
    py --version
    set PYTHON_CMD=py
) else (
    echo Py launcher not found, trying python.exe...
    where python.exe > nul 2>&1
    if %errorlevel% equ 0 (
        echo Found python.exe
        python.exe --version
        set PYTHON_CMD=python.exe
    ) else (
        echo ERROR: No Python installation found!
        echo Please install Python from https://python.org
        pause
        exit /b 1
    )
)

REM Try to install basic dependencies
echo.
echo Installing essential dependencies...
%PYTHON_CMD% -m pip install --user rich click requests google-generativeai python-dotenv

if errorlevel 1 (
    echo.
    echo WARNING: Failed to install some dependencies
    echo The system will try to run with available packages
    echo.
)

REM Check for API key
if not defined GEMINI_API_KEY (
    if exist ".env" (
        echo Loading environment from .env file...
    ) else (
        echo.
        echo NOTE: No GEMINI_API_KEY found
        echo For cloud AI, set: set GEMINI_API_KEY=your_key_here
        echo.
    )
)

REM Show options
echo.
echo Choose how to run DevO Chat:
echo.
echo 1. Original chat.py (Gemini API only)
echo 2. Enhanced chat (if available)
echo 3. Test system
echo 4. Exit
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo Starting original chat.py...
    %PYTHON_CMD% chat.py
) else if "%choice%"=="2" (
    if exist "chat_enhanced.py" (
        echo Starting enhanced chat...
        %PYTHON_CMD% chat_enhanced.py
    ) else (
        echo Enhanced chat not available, starting original...
        %PYTHON_CMD% chat.py
    )
) else if "%choice%"=="3" (
    echo Testing system...
    %PYTHON_CMD% -c "print('Python works!'); import sys; print('Version:', sys.version); print('Executable:', sys.executable)"
    echo.
    echo Testing imports...
    %PYTHON_CMD% -c "try:^
    import rich; print('✓ Rich available')^
except:^
    print('✗ Rich not available')"
    %PYTHON_CMD% -c "try:^
    import google.generativeai; print('✓ Gemini API available')^
except:^
    print('✗ Gemini API not available')"
    pause
) else if "%choice%"=="4" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice. Starting original chat...
    %PYTHON_CMD% chat.py
)

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start chat system
    echo Check your Python installation and dependencies
    pause
)

echo.
echo Session ended. Press any key to close...
pause > nul
