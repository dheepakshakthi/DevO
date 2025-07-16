@echo off
echo DevO Chat - Direct Launch
echo ===========================

cd /d "C:\DevO-Hackfinity"

REM Find Python executable
set PYTHON_EXE=
for %%i in (py python3 python) do (
    where %%i >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_EXE=%%i
        goto found_python
    )
)

echo Python not found in PATH
pause
exit /b 1

:found_python
echo Using Python: %PYTHON_EXE%

REM Check Python version
%PYTHON_EXE% --version

REM Try to install dependencies
echo Installing dependencies...
%PYTHON_EXE% -m pip install --user rich pyyaml requests google-genai python-dotenv

REM If that fails, try without --user
if errorlevel 1 (
    echo Trying without --user flag...
    %PYTHON_EXE% -m pip install rich pyyaml requests google-genai python-dotenv
)

echo.
echo Launching Enhanced DevO Chat...
echo.
%PYTHON_EXE% chat_enhanced.py --interactive

if errorlevel 1 (
    echo.
    echo Error running chat. Press any key to exit...
    pause >nul
)
