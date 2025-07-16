REM DevO Chat - Ultimate Silent Agent
REM One command to rule them all - zero user interaction

@echo off
setlocal enabledelayedexpansion

REM Ultimate silent mode
set SILENT=true
set AUTO_EVERYTHING=true
set NO_PROMPTS=true
set AGGRESSIVE=true

echo.
echo ==========================================
echo   DevO Chat - Ultimate Silent Agent
echo ==========================================
echo.
echo 🤖 Running in full autonomous mode...
echo 🔄 Zero user interaction required
echo 📦 Will create complete distribution package
echo.

REM Kill everything silently
taskkill /F /IM devochat.exe >nul 2>&1
timeout /t 1 /nobreak >nul

REM Check prerequisites and auto-install if needed
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo 🔧 Auto-installing UV...
    powershell -Command "& {Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression}" >nul 2>&1
)

REM Run the comprehensive Python automation
echo 🚀 Executing autonomous automation agent...
echo.
call uv run python silent_automation.py

REM Check if automation was successful
if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo   🎉 AUTONOMOUS AGENT COMPLETED! 🎉
    echo ==========================================
    echo.
    echo ✅ Fully automated - no user input needed
    echo ✅ Complete distribution package created
    echo ✅ Executable tested and validated
    echo ✅ Ready for immediate distribution
    echo.
    echo 📦 Location: release\devochat.exe
    echo 🚀 Just run it and go!
    echo.
    
    REM Show file size
    for %%A in ("release\devochat.exe") do (
        echo 📊 Size: %%~zA bytes
    )
    
    echo.
    echo 🎯 Your AI agent is ready!
    
) else (
    echo.
    echo ❌ Autonomous agent encountered an issue
    echo Check automation.log for details
)

echo.
echo Autonomous agent execution complete.
