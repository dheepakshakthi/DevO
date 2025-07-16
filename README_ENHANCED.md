# 🚀 Enhanced DevO Chat - AI Development Assistant

A powerful unified chat interface that combines **Gemini API** with **Local LLM** support for code generation, debugging, and automation with GPU acceleration and memory management.

## ✨ Features

### 🤖 **Dual AI Support**
- **☁️ Cloud AI**: Gemini 2.0 Flash for fast responses
- **🧠 Local AI**: CodeLlama, Mistral, Llama2 with offline privacy
- **🔄 Hybrid Mode**: Switch between providers seamlessly

### 🔧 **Automation Capabilities**
- **Code Generation**: `generate a REST API for user management`
- **Code Fixing**: `fix this ImportError: module not found`
- **Code Optimization**: `optimize for performance`
- **Auto Setup**: `setup https://github.com/user/repo.git`

### 🚀 **Performance & GPU Support**
- **GPU Acceleration**: CUDA support for local models
- **Memory Management**: Intelligent model loading/unloading
- **Timeout Prevention**: No more hanging requests
- **Model Caching**: Fast subsequent loads

### 📁 **Repository Intelligence**
- **Auto Analysis**: Detects language, framework, dependencies
- **Context Awareness**: AI understands your project structure
- **Smart Suggestions**: Relevant to your tech stack

## 🛠️ Quick Start

### 1. **Automated Setup (Recommended)**

```bash
# Clone or navigate to your DevO-Hackfinity directory
cd DevO-Hackfinity

# Run the enhanced setup
python setup_enhanced.py
```

This will:
- ✅ Check system requirements
- 🐍 Create virtual environment
- 📦 Install all dependencies
- 🚀 Setup GPU support (if available)
- 📁 Create model directories
- ⚙️ Generate configuration
- 🧪 Test installation

### 2. **Manual Setup**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements_unified.txt

# Copy environment template
copy env_example.txt .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. **Set API Key** (for cloud AI)

```bash
# Method 1: Environment variable
set GEMINI_API_KEY=your_api_key_here

# Method 2: .env file
echo GEMINI_API_KEY=your_api_key_here > .env

# Method 3: Pass as parameter
python chat_enhanced.py --api-key your_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

## 🎯 How to Run

### **Option 1: Windows Launcher (Easiest)**
```bash
# Basic usage
launch_enhanced_chat.bat

# Use local AI only
launch_enhanced_chat.bat --local

# Specific model
launch_enhanced_chat.bat --local --model mistral

# Different repository
launch_enhanced_chat.bat --repo C:\path\to\your\project
```

### **Option 2: Direct Python**
```bash
# Default (uses Gemini if API key available, otherwise local)
python chat_enhanced.py

# Force local AI
python chat_enhanced.py --use-local

# Specific local model
python chat_enhanced.py --use-local --local-model codellama

# Different repository path
python chat_enhanced.py --repo-path /path/to/your/project

# Save/load sessions
python chat_enhanced.py --save-session my_session.json
python chat_enhanced.py --load-session my_session.json
```

### **Option 3: Test First**
```bash
# Test your installation
python test_enhanced.py
```

## 💬 Usage Examples

### **Natural Conversation**
```
You: Analyze my Python code for security issues
DevO: I'll analyze your repository for security vulnerabilities...

You: How can I optimize this database query?
DevO: Looking at your code structure, here are several optimization strategies...
```

### **Automation Commands**
```
You: generate a REST API for user management
DevO: [Generates complete Flask/FastAPI with endpoints, models, validation]

You: fix ImportError: cannot import name 'User' from 'models'
DevO: [Analyzes your code and provides specific fix with explanation]

You: optimize for performance
DevO: [Reviews code and suggests performance improvements]

You: setup https://github.com/fastapi/fastapi
DevO: [Clones repo, analyzes structure, sets up dependencies, creates Docker]
```

### **AI Management**
```
You: switch ai
DevO: Switched to Local LLM (codellama)

You: models
DevO: [Shows all available models and their status]

You: context
DevO: [Shows current repository analysis and project info]
```

## 🔧 Configuration

### **GPU Setup**
The system automatically detects and configures GPU support:

```bash
# Check GPU status
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Force GPU installation
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### **Local Models**
Place your GGML models in the `models/` directory:
```
models/
├── ggml/
│   ├── llama-2-7b-chat.ggmlv3.q8_0.bin
│   ├── codellama-7b-instruct.q4_0.gguf
│   └── mistral-7b-instruct-v0.1.q4_0.gguf
├── transformers/  # HuggingFace cache
└── ollama/        # Ollama models
```

### **Configuration File**
Edit `enhanced_config.json` for advanced settings:
```json
{
  "ai_providers": {
    "gemini": {"enabled": true},
    "local_llm": {"preferred_provider": "ollama"}
  },
  "gpu_settings": {
    "auto_detect": true,
    "device_map": "auto",
    "load_in_8bit": false
  },
  "memory_management": {
    "max_memory_usage": "auto",
    "enable_model_offloading": true
  }
}
```

## 📋 Requirements

### **System Requirements**
- **OS**: Windows 10+, Linux, macOS
- **Python**: 3.8+
- **RAM**: 4GB+ (8GB+ recommended for local AI)
- **Storage**: 5GB+ (for models)
- **GPU**: Optional CUDA GPU for acceleration

### **Dependencies**
```
Core:
- rich>=13.0.0          # Beautiful terminal output
- click>=8.0.0          # Command line interface
- python-dotenv>=1.0.0  # Environment variables
- requests>=2.28.0      # HTTP requests

Cloud AI:
- google-generativeai>=0.3.0  # Gemini API

Local AI:
- torch>=2.0.0          # PyTorch for models
- transformers>=4.35.0  # HuggingFace transformers
- accelerate>=0.25.0    # Model acceleration

Optional:
- llama-cpp-python>=0.2.0    # GGML model support
- psutil>=5.9.0              # System monitoring
- GPUtil>=1.4.0              # GPU monitoring
```

## 🛠️ Troubleshooting

### **Common Issues**

#### **1. Import Errors**
```bash
# Install missing dependencies
pip install -r requirements_unified.txt

# Verify installation
python test_enhanced.py
```

#### **2. GPU Not Detected**
```bash
# Check CUDA installation
nvidia-smi

# Install CUDA PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### **3. Local Models Not Loading**
```bash
# Check model path
ls models/
ls models/ggml/

# Verify model format (.bin, .gguf files)
# Download from: https://huggingface.co/models?library=ggml
```

#### **4. Gemini API Errors**
```bash
# Verify API key
echo $GEMINI_API_KEY

# Test API access
python -c "import google.generativeai as genai; genai.configure(api_key='your_key'); print('API OK')"
```

#### **5. Memory Issues**
```bash
# Monitor memory usage
python -c "import psutil; print(f'RAM: {psutil.virtual_memory().percent}%')"

# Enable model offloading in config
# Edit enhanced_config.json -> memory_management.enable_model_offloading: true
```

### **Getting Help**
```bash
# Show help
python chat_enhanced.py --help
launch_enhanced_chat.bat --help

# Test system
python test_enhanced.py

# Debug mode
python chat_enhanced.py --repo-path . --use-local --local-model codellama
```

## 🎯 Advanced Usage

### **Custom Models**
Add your own models to the configuration:
```json
{
  "models": {
    "my_custom_model": {
      "ollama_name": "my_model:latest",
      "transformers_name": "username/model-name-hf",
      "ggml_name": "my_model.q4_0.gguf",
      "description": "My custom fine-tuned model"
    }
  }
}
```

### **Session Management**
```bash
# Save important conversations
python chat_enhanced.py --save-session project_discussion.json

# Resume later
python chat_enhanced.py --load-session project_discussion.json

# Multiple projects
python chat_enhanced.py --repo-path /project1 --save-session project1.json
python chat_enhanced.py --repo-path /project2 --save-session project2.json
```

### **Automation Scripts**
Create automation scripts for common tasks:
```python
from chat_enhanced import EnhancedDevOChatSession

# Automated code review
session = EnhancedDevOChatSession(use_local=True)
response = session._get_ai_response("Review this code for security issues: " + code)
```

## 🏗️ Architecture

```
Enhanced DevO Chat
├── 🤖 AI Providers
│   ├── Gemini API (Cloud)
│   ├── Ollama (Local)
│   ├── Transformers (Local)
│   └── GGML/llama-cpp (Local)
├── 🔧 Automation Engine
│   ├── Code Generation
│   ├── Code Fixing  
│   ├── Code Optimization
│   └── Repository Setup
├── 📁 Context Manager
│   ├── Repository Analysis
│   ├── File Detection
│   ├── Dependency Extraction
│   └── Framework Detection
├── 💾 Memory Manager
│   ├── Model Loading/Unloading
│   ├── GPU Memory Optimization
│   ├── Cache Management
│   └── Session Persistence
└── 🖥️ User Interface
    ├── Rich Terminal UI
    ├── Command Line Interface
    ├── Interactive Chat
    └── Progress Indicators
```

## 📈 Performance Tips

### **For Best Performance:**
1. **Use GPU**: Install CUDA drivers and GPU PyTorch
2. **SSD Storage**: Store models on fast SSD
3. **Adequate RAM**: 8GB+ for smooth local AI
4. **Model Size**: Start with 7B models, scale up as needed
5. **Ollama**: Use Ollama for best local performance

### **Memory Optimization:**
```json
{
  "memory_management": {
    "max_memory_usage": "6GB",
    "enable_model_offloading": true,
    "cache_models": false
  },
  "gpu_settings": {
    "load_in_8bit": true,
    "device_map": "auto"
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for transformers architecture
- **Google** for Gemini API
- **HuggingFace** for transformers library
- **Ollama** for local model serving
- **Rich** for beautiful terminal UI

---

**🚀 Happy Coding with Enhanced DevO Chat!** 

For questions or support, open an issue or start a discussion.
