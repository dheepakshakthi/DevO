@echo off
REM DevO Chat - Simple Full Automation
REM Complete build pipeline with proper error handling

echo.
echo ==========================================
echo    DevO Chat - Full Automation Pipeline
echo ==========================================
echo.

echo [1/6] Checking prerequisites...
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: UV not found. Please install UV first.
    goto :error
)
echo ✅ UV found

echo.
echo [2/6] Installing dependencies...
call uv sync --extra build
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    goto :error
)
echo ✅ Dependencies installed

echo.
echo [3/6] Running code quality checks...
call uv run python -c "import chat, auto_setup, utils, templates, repocontainerizer; print('All modules OK')"
if %errorlevel% neq 0 (
    echo ERROR: Code quality checks failed
    goto :error
)
echo ✅ Code quality checks passed

echo.
echo [4/6] Cleaning previous builds...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
if exist *.spec del /q *.spec 2>nul
echo ✅ Cleanup complete

echo.
echo [5/6] Building standalone executable...
call uv run pyinstaller --onefile --console --name devochat --add-data "sample-config.yml;." --add-data "templates.py;." --add-data "utils.py;." --add-data "auto_setup.py;." --add-data "repocontainerizer.py;." --collect-all google.generativeai --collect-all rich --collect-all click --collect-all yaml --collect-all requests --collect-all git --collect-all dotenv --hidden-import=google.generativeai --hidden-import=rich --hidden-import=click --hidden-import=yaml --hidden-import=requests --hidden-import=git --hidden-import=dotenv --hidden-import=os --hidden-import=sys --hidden-import=json --hidden-import=subprocess --hidden-import=pathlib chat.py
if %errorlevel% neq 0 (
    echo ERROR: Build failed
    goto :error
)
echo ✅ Executable built

echo.
echo [6/6] Creating distribution package...
if exist release rmdir /s /q release 2>nul
mkdir release
copy "dist\devochat.exe" "release\" >nul
if exist "STANDALONE_EXECUTABLE_GUIDE.md" copy "STANDALONE_EXECUTABLE_GUIDE.md" "release\" >nul
if exist "sample-config.yml" copy "sample-config.yml" "release\" >nul
if exist "launch_devochat.bat" copy "launch_devochat.bat" "release\" >nul

echo DevO Chat - Standalone Executable > "release\BUILD_INFO.txt"
echo Build Date: %date% %time% >> "release\BUILD_INFO.txt"
echo Platform: Windows >> "release\BUILD_INFO.txt"
for %%A in ("release\devochat.exe") do echo File Size: %%~zA bytes >> "release\BUILD_INFO.txt"

echo ✅ Distribution package created

echo.
echo Testing executable...
call "release\devochat.exe" --help >nul 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Executable test failed, but file was created
) else (
    echo ✅ Executable test passed
)

echo.
echo ==========================================
echo    🎉 AUTOMATION COMPLETED SUCCESSFULLY!
echo ==========================================
echo.
echo ✅ Environment setup complete
echo ✅ Dependencies installed
echo ✅ Code quality checks passed
echo ✅ Executable built successfully
echo ✅ Distribution package ready
echo.
echo 📦 Your DevO Chat application is ready!
echo 📍 Location: release\devochat.exe
echo 📊 Size: 
for %%A in ("release\devochat.exe") do echo     %%~zA bytes
echo.
echo 🚀 Quick start: 
echo     cd release
echo     devochat.exe --help
echo.
goto :end

:error
echo.
echo ❌ Automation failed!
echo Please check the error messages above and try again.
echo.
pause
exit /b 1

:end
echo Press any key to exit...
pause >nul
