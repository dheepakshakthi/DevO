REM DevO Chat - One-Click Full Automation
REM Ultimate automation script that handles everything

@echo off
setlocal enabledelayedexpansion

echo.
echo ==========================================
echo    DevO Chat - ONE-CLICK AUTOMATION
echo ==========================================
echo.

REM Check if automation preference exists
if exist "automation_preference.txt" (
    set /p AUTO_MODE=<automation_preference.txt
) else (
    set AUTO_MODE=ask
)

if "%AUTO_MODE%"=="auto" (
    set CHOICE=Y
    echo Running in automatic mode...
) else (
    echo This will run the complete automation pipeline:
    echo.
    echo ✅ Environment validation and setup
    echo ✅ Code quality checks and testing
    echo ✅ Standalone executable build
    echo ✅ Distribution package creation
    echo ✅ Documentation generation
    echo.
    set /p CHOICE=Do you want to continue? [Y/N]: 
)

if /i "%CHOICE%"=="Y" (
    echo.
    echo 🚀 Starting complete automation...
    echo.
    
    REM Run Python automation manager
    uv run python automation_manager.py full
    
    if %errorlevel% equ 0 (
        echo.
        echo ==========================================
        echo    🎉 AUTOMATION COMPLETED SUCCESSFULLY!
        echo ==========================================
        echo.
        echo ✅ Your DevO Chat application is ready!
        echo 📦 Find your executable in: release\devochat.exe
        echo 📖 Documentation: release\STANDALONE_EXECUTABLE_GUIDE.md
        echo 🚀 Quick start: run release\devochat.exe
        echo.
        
        REM Ask to save preference
        if "%AUTO_MODE%"=="ask" (
            set /p SAVE_PREF=Save this as automatic mode for future runs? [Y/N]: 
            if /i "!SAVE_PREF!"=="Y" (
                echo auto > automation_preference.txt
                echo ✅ Preference saved. Future runs will be automatic.
            )
        )
        
        REM Ask to test immediately
        set /p TEST_NOW=Test the executable now? [Y/N]: 
        if /i "!TEST_NOW!"=="Y" (
            echo.
            echo Testing executable...
            release\devochat.exe --help
            echo.
            echo ✅ Executable test completed!
        )
        
        REM Ask to open release folder
        set /p OPEN_FOLDER=Open release folder? [Y/N]: 
        if /i "!OPEN_FOLDER!"=="Y" (
            explorer release
        )
        
    ) else (
        echo.
        echo ❌ Automation failed!
        echo Please check the error messages above.
        echo.
    )
) else (
    echo.
    echo Automation cancelled.
    echo.
)

echo.
echo Press any key to exit...
pause >nul
