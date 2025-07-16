@echo off
echo ====================================================
echo Enhanced DevO Chat - Local LLM Setup for Windows
echo ====================================================
echo.

echo This script will help you set up local LLM support for DevO Chat
echo.

echo Step 1: Installing Python dependencies...
echo.

rem Install basic dependencies first
pip install rich requests click python-dotenv pyyaml gitpython

echo.
echo Step 2: Installing enhanced dependencies...
echo.

rem Ask user about PyTorch installation
echo PyTorch installation options:
echo 1. CPU only (smaller download, slower inference)
echo 2. CUDA (GPU support, faster inference, larger download)
echo.

set /p choice="Choose option (1 or 2): "

if "%choice%"=="2" (
    echo Installing PyTorch with CUDA support...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
) else (
    echo Installing PyTorch CPU version...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
)

echo.
echo Installing Transformers and related packages...
pip install transformers accelerate sentencepiece tokenizers

echo.
echo Step 3: Setting up Ollama (recommended for best performance)...
echo.

echo Please follow these steps to install Ollama:
echo 1. Visit: https://ollama.ai/download
echo 2. Download Ollama for Windows
echo 3. Install and restart this script
echo.

echo Checking if Ollama is already installed...
ollama --version 2>nul
if %errorlevel% equ 0 (
    echo Ollama is installed!
    echo.
    echo Starting Ollama service...
    start /B ollama serve
    
    echo Waiting for Ollama to start...
    timeout /t 5 /nobreak >nul
    
    echo Installing CodeLlama model...
    echo This may take several minutes...
    ollama pull codellama:7b-instruct
    
    echo.
    echo Testing Ollama setup...
    echo {"model":"codellama:7b-instruct","prompt":"Write hello world in Python:","stream":false} > test_prompt.json
    curl -X POST http://localhost:11434/api/generate -d @test_prompt.json -H "Content-Type: application/json"
    del test_prompt.json
) else (
    echo Ollama not found. Please install manually from https://ollama.ai/download
)

echo.
echo Step 4: Testing the setup...
echo.

python -c "
try:
    import torch
    import transformers
    import rich
    print('✅ All dependencies installed successfully!')
    print(f'PyTorch version: {torch.__version__}')
    print(f'Transformers version: {transformers.__version__}')
    print(f'CUDA available: {torch.cuda.is_available()}')
except ImportError as e:
    print(f'❌ Import error: {e}')
"

echo.
echo Setup complete! You can now use Enhanced DevO Chat:
echo.
echo For local LLM only:
echo   python chat_enhanced.py --use-local
echo.
echo For hybrid mode (local + cloud):
echo   python chat_enhanced.py
echo.
echo For local LLM setup script:
echo   python setup_local_llm.py
echo.

pause
