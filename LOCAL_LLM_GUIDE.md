# Enhanced DevO Chat - Local LLM Integration Guide

## Overview

Enhanced DevO Chat now supports local Large Language Models (LLMs) like CodeLlama 7B, providing:

- 🔒 **Privacy-focused**: All processing happens locally
- ⚡ **No timeout errors**: Direct model control
- 🤖 **Automation features**: Code generation, fixing, optimization
- 💰 **Cost-effective**: No API fees
- 🌐 **Offline capable**: Works without internet

## Quick Start

### Option 1: Automatic Setup (Recommended)

```bash
# Run the setup script
python setup_local_llm.py

# Or use the Windows batch file
setup_local_llm.bat
```

### Option 2: Manual Setup

1. **Install Dependencies**
   ```bash
   pip install torch transformers accelerate sentencepiece tokenizers
   ```

2. **Install Ollama (Recommended)**
   - Windows: Download from https://ollama.ai/download
   - macOS/Linux: `curl -fsSL https://ollama.ai/install.sh | sh`

3. **Download CodeLlama Model**
   ```bash
   ollama serve  # Start Ollama service
   ollama pull codellama:7b-instruct
   ```

## Usage

### Basic Usage

```bash
# Use local LLM only
python chat_enhanced.py --use-local

# Use specific local model
python chat_enhanced.py --use-local --local-model codellama

# Hybrid mode (local + cloud fallback)
python chat_enhanced.py

# With custom repository
python chat_enhanced.py --repo-path /path/to/your/project --use-local
```

### Enhanced Commands

The enhanced chat includes new automation commands:

#### Code Generation
```
generate a REST API for user management
generate unit tests for this function
generate a Docker setup for Flask app
```

#### Code Fixing
```
fix ImportError: module not found
fix this timeout error in my requests code
fix SQL injection vulnerability
```

#### Code Optimization
```
optimize performance
optimize readability
optimize memory usage
optimize maintainability
```

#### AI Management
```
switch ai          # Switch between local and cloud AI
models            # List available models
context           # Show repository info
help              # Show all commands
```

## Architecture

### Local LLM Providers

1. **Ollama** (Recommended)
   - Better performance
   - Easier model management
   - Lower memory usage
   - Faster startup

2. **Transformers** (Fallback)
   - Direct PyTorch integration
   - More model options
   - Higher memory usage
   - Slower startup

### Supported Models

| Model | Size | Use Case | Ollama Name | Transformers Name |
|-------|------|----------|-------------|-------------------|
| CodeLlama 7B | ~3.8GB | Code tasks | `codellama:7b-instruct` | `codellama/CodeLlama-7b-Instruct-hf` |
| Llama2 7B | ~3.8GB | General chat | `llama2:7b-chat` | `meta-llama/Llama-2-7b-chat-hf` |
| Mistral 7B | ~4.1GB | Efficient general | `mistral:7b-instruct` | `mistralai/Mistral-7B-Instruct-v0.1` |

## Configuration

### Local LLM Config (`local_llm_config.json`)

```json
{
  "preferred_provider": "ollama",
  "models": {
    "codellama": {
      "ollama_name": "codellama:7b-instruct",
      "transformers_name": "codellama/CodeLlama-7b-Instruct-hf",
      "description": "Code-focused LLM for programming tasks"
    }
  },
  "generation_params": {
    "temperature": 0.7,
    "max_tokens": 1024,
    "timeout": 300
  }
}
```

### Environment Variables

```bash
# Optional: For hybrid mode
export GEMINI_API_KEY=your_api_key_here

# Optional: Default repository path
export DEFAULT_REPO_PATH=/path/to/default/repo

# Optional: Enable debug mode
export DEBUG=true
```

## System Requirements

### Minimum Requirements
- **RAM**: 8GB (4GB for model + 4GB for system)
- **Storage**: 5GB free space
- **CPU**: Multi-core processor (4+ cores recommended)
- **OS**: Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+)

### Recommended Requirements
- **RAM**: 16GB+ (for better performance)
- **GPU**: NVIDIA GPU with 6GB+ VRAM (optional, for faster inference)
- **Storage**: SSD with 10GB+ free space
- **CPU**: 8+ cores for better parallel processing

### GPU Support

For NVIDIA GPU acceleration:

```bash
# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU support
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## Performance Tips

### Optimize Inference Speed

1. **Use GPU**: Install CUDA-enabled PyTorch
2. **Use Ollama**: Better optimized than Transformers
3. **Reduce Context**: Limit conversation history
4. **Adjust Parameters**: Lower `max_tokens` for faster responses

### Optimize Memory Usage

1. **Use 7B Models**: Instead of larger models
2. **Close Other Applications**: Free up RAM
3. **Use Ollama**: More memory efficient
4. **Adjust Batch Size**: For Transformers usage

### Optimize Storage

1. **Use Model Quantization**: Smaller model files
2. **Share Models**: Ollama shares models between projects
3. **Clean Cache**: Remove unused Transformers models

## Troubleshooting

### Common Issues

#### 1. Model Download Fails
```
❌ Failed to download model: Connection timeout
```
**Solutions:**
- Check internet connection
- Try smaller model first
- Use different mirror/source
- Resume download if supported

#### 2. Out of Memory Error
```
❌ CUDA out of memory / RuntimeError: out of memory
```
**Solutions:**
- Reduce `max_tokens` parameter
- Use CPU instead of GPU
- Close other applications
- Use smaller model (7B instead of 13B)

#### 3. Ollama Service Won't Start
```
❌ Failed to start Ollama service
```
**Solutions:**
- Check if port 11434 is free
- Run `ollama serve` manually
- Restart computer
- Reinstall Ollama

#### 4. Slow Inference
```
⚠️ Generation taking too long
```
**Solutions:**
- Use GPU acceleration
- Switch to Ollama
- Reduce context length
- Use smaller model

#### 5. Import Errors
```
❌ Import "torch" could not be resolved
```
**Solutions:**
- Install dependencies: `pip install torch transformers`
- Check virtual environment
- Reinstall packages
- Update pip: `pip install --upgrade pip`

### Debug Mode

Enable debug logging:

```bash
export DEBUG=true
python chat_enhanced.py --use-local
```

### Manual Testing

Test individual components:

```python
# Test local LLM
python -c "
from local_llm import LocalLLMManager
llm = LocalLLMManager()
llm.setup_model('codellama')
print(llm.generate('Write hello world in Python:'))
"

# Test automation
python automation_demo.py
```

## Integration Examples

### Custom Scripts

```python
from local_llm import LocalLLMManager, AutomationManager

# Initialize
llm = LocalLLMManager()
llm.setup_model("codellama")
automation = AutomationManager(llm)

# Generate code
code = automation.generate_code("Create a REST API endpoint", "python")
print(code)

# Fix code
fixed = automation.fix_code_issues(buggy_code, "ImportError")
print(fixed)

# Optimize code
optimized = automation.optimize_code(slow_code, "performance")
print(optimized)
```

### IDE Integration

Use with VS Code, PyCharm, or other IDEs:

```python
# Save as code_assistant.py
import sys
from local_llm import LocalLLMManager

def assist_with_code(task, language="python"):
    llm = LocalLLMManager()
    llm.setup_model("codellama")
    return llm.generate(f"Task: {task}\nLanguage: {language}\nCode:")

if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "Write a hello world function"
    print(assist_with_code(task))
```

## Advanced Features

### Custom Model Integration

Add new models to config:

```json
{
  "models": {
    "custom_model": {
      "ollama_name": "custom:latest",
      "transformers_name": "organization/model-name",
      "description": "Custom model description"
    }
  }
}
```

### Batch Processing

Process multiple files:

```python
from pathlib import Path
from local_llm import LocalLLMManager, AutomationManager

llm = LocalLLMManager()
llm.setup_model("codellama")
automation = AutomationManager(llm)

# Process all Python files
for py_file in Path(".").rglob("*.py"):
    with open(py_file) as f:
        code = f.read()
    
    # Analyze and suggest improvements
    suggestions = automation.optimize_code(code, "readability")
    print(f"Suggestions for {py_file}:")
    print(suggestions)
    print("-" * 50)
```

### API Server

Create a local API server:

```python
from flask import Flask, request, jsonify
from local_llm import LocalLLMManager

app = Flask(__name__)
llm = LocalLLMManager()
llm.setup_model("codellama")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt", "")
    response = llm.generate(prompt)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="localhost", port=8000)
```

## Security Considerations

### Data Privacy
- All processing happens locally
- No data sent to external servers
- Models stored on your machine

### Model Safety
- Use official models from trusted sources
- Verify model checksums when possible
- Be cautious with custom/modified models

### Network Security
- Ollama runs on localhost by default
- Firewall may need configuration
- Consider VPN for remote access

## Future Enhancements

### Planned Features
- [ ] Model fine-tuning interface
- [ ] Multi-modal support (code + images)
- [ ] Distributed inference across multiple machines
- [ ] Integration with more local LLM providers
- [ ] Advanced code analysis pipelines
- [ ] Real-time collaboration features

### Community Contributions
- Submit issues and feature requests on GitHub
- Contribute new model integrations
- Share optimization techniques
- Help with documentation

## Support

### Getting Help
1. Check this documentation
2. Run the automation demo: `python automation_demo.py`
3. Use debug mode: `DEBUG=true python chat_enhanced.py --use-local`
4. Check system requirements
5. Visit the project repository for issues

### Performance Monitoring
- Monitor RAM usage during inference
- Track model loading times
- Measure response latency
- Check GPU utilization (if applicable)

---

**Happy coding with your private AI assistant! 🤖**
