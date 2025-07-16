# DevO Chat - AI Assistant for Development

## Overview

DevO Chat is an interactive AI assistant that helps developers with code analysis, suggestions, dependency management, and DevOps tasks. It provides a conversational interface to the powerful Gemini LLM for repository analysis and development assistance.

## Features

### 🤖 **AI-Powered Conversations**
- Natural language interface for code analysis
- Context-aware responses based on your repository
- Persistent chat history within sessions
- Intelligent suggestions and explanations

### 📊 **Repository Analysis**
- Automatic language and framework detection
- File structure analysis
- Dependency scanning
- Security analysis
- Performance optimization suggestions

### 🔧 **Code Assistance**
- Code suggestions and improvements
- Bug detection and fixes
- Best practice recommendations
- Security vulnerability identification
- Performance optimization tips

### 🐳 **DevOps Support**
- Docker containerization help
- CI/CD pipeline suggestions
- Infrastructure recommendations
- Deployment strategies
- Configuration management

## Usage

### Starting the Chat

#### Method 1: Via Main CLI
```bash
# Start chat with repository context
uv run python repo_containerizer.py chat --repo-path .

# Start without repository context
uv run python repo_containerizer.py chat

# Save session to file
uv run python repo_containerizer.py chat --save-session
```

#### Method 2: Standalone Application
```bash
# Start standalone chat
uv run python chat.py --repo-path .

# Start without repository context
uv run python chat.py
```

#### Method 3: Convenience Scripts (Windows)
```cmd
# Start chat with current directory as context
.\chat.bat

# Start standalone chat
.\chat-standalone.bat
```

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `analyze` | Analyze current repository for issues | "analyze my Python code for issues" |
| `deps` | Check and suggest dependency fixes | "deps check missing dependencies" |
| `security` | Security analysis and recommendations | "security audit my requirements.txt" |
| `containerize` | Help with Docker containerization | "containerize this Flask app" |
| `suggest <topic>` | Get suggestions on specific topics | "suggest improvements for performance" |
| `explain <concept>` | Explain technical concepts | "explain docker best practices" |
| `fix <issue>` | Get help fixing specific issues | "fix import errors in my code" |
| `optimize` | Repository optimization suggestions | "optimize my code structure" |
| `help` | Show available commands | - |
| `context` | Show current repository context | - |
| `clear` | Clear chat history | - |
| `exit` | Exit the chat | - |

### Example Conversations

#### Code Analysis
```
You: analyze my Python code for security issues

DevO: I'll analyze your Python code for security vulnerabilities...

[Detailed analysis with specific recommendations]
```

#### Dependency Help
```
You: deps check what's missing in my requirements.txt

DevO: Scanning your requirements.txt and imports...

Found several missing dependencies:
- requests (used in app.py line 5)
- flask-cors (used in app.py line 12)
- python-dotenv (used in config.py line 3)

Would you like me to generate an updated requirements.txt?
```

#### Containerization Assistance
```
You: containerize this Flask app for production

DevO: I'll help you containerize your Flask application...

[Step-by-step Docker setup with security best practices]
```

#### Performance Optimization
```
You: suggest performance improvements for my code

DevO: Based on your codebase analysis, here are performance optimizations...

[Specific recommendations with code examples]
```

## Features in Detail

### 🔍 **Context-Aware Analysis**
- Automatically loads repository context when started with `--repo-path`
- Analyzes file structure, languages, and frameworks
- Reads key configuration files (requirements.txt, package.json, etc.)
- Provides relevant suggestions based on detected technologies

### 💬 **Conversational Interface**
- Natural language processing for developer queries
- Maintains conversation context across the session
- Supports follow-up questions and clarifications
- Provides detailed explanations with code examples

### 📝 **Session Management**
- Optional session saving with `--save-session`
- Chat history persistence
- Repository context preservation
- Timestamped conversation records

### 🛡️ **Security Analysis**
- Dependency vulnerability scanning
- Code security best practices
- Configuration security review
- Secrets detection and handling

### ⚡ **Performance Optimization**
- Code efficiency analysis
- Resource usage optimization
- Scalability recommendations
- Performance monitoring suggestions

## Configuration

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key (required)

### API Key Setup
```bash
# Set environment variable
export GEMINI_API_KEY=your_api_key_here

# Or create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

## Advanced Usage

### Batch Commands
```bash
# Run multiple commands in sequence
echo -e "analyze\ndeps\nsecurity\nexit" | uv run python chat.py --repo-path .
```

### Custom Focus Areas
```bash
# Focus on specific aspects
You: analyze my code focusing on security and performance
```

### Integration with CI/CD
```bash
# Generate reports for CI/CD pipeline
uv run python chat.py --repo-path . --save-session < analysis_commands.txt
```

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```
   ❌ API key required. Set GEMINI_API_KEY environment variable
   ```
   **Solution**: Set the `GEMINI_API_KEY` environment variable or create a `.env` file

2. **Repository Context Error**
   ```
   ⚠️ Warning: Could not analyze repository context
   ```
   **Solution**: Ensure the repository path exists and contains readable files

3. **Import Errors**
   ```
   ImportError: cannot import name 'xyz' from 'utils'
   ```
   **Solution**: Run `uv sync` to ensure all dependencies are installed

### Performance Tips

1. **Large Repositories**: The chat analyzes only the first 10 code files to avoid token limits
2. **File Size Limits**: Individual files are truncated to 5000 characters for analysis
3. **Context Optimization**: Only key configuration files are loaded for context

## Examples

### Security Audit
```
You: security audit my web application

DevO: I'll perform a comprehensive security audit of your web application...

🔍 Security Analysis Results:

1. **Dependency Vulnerabilities**
   - Flask 1.1.0 has known security issues (CVE-2021-23385)
   - Recommendation: Update to Flask 2.3.0+

2. **Code Security Issues**
   - app.py line 45: SQL injection vulnerability
   - config.py line 12: Hardcoded secret key
   - auth.py line 78: Missing input validation

3. **Configuration Security**
   - Debug mode enabled in production
   - CORS configured too permissively
   - Missing security headers

Would you like me to provide specific fixes for these issues?
```

### Performance Optimization
```
You: optimize my database queries

DevO: I'll analyze your database queries for optimization opportunities...

🚀 Performance Optimization Recommendations:

1. **Query Optimization**
   - models.py line 23: N+1 query problem detected
   - Recommendation: Use select_related() or prefetch_related()

2. **Indexing**
   - Missing index on frequently queried fields
   - Recommendation: Add database indexes

3. **Caching**
   - No caching strategy implemented
   - Recommendation: Implement Redis caching

Would you like me to show you the specific code changes?
```

## Integration with DevO Tools

The chat interface integrates seamlessly with other DevO tools:

- **Repository Containerization**: Get help with Docker setup
- **Code Suggestions**: Interactive code improvement
- **Dependency Management**: Real-time dependency analysis
- **Security Auditing**: Comprehensive security review
- **Performance Analysis**: Detailed performance optimization

## Next Steps

1. **Try the Chat**: Start with `uv run python chat.py --repo-path .`
2. **Explore Commands**: Type `help` to see all available commands
3. **Save Sessions**: Use `--save-session` to keep conversation history
4. **Integrate with Workflow**: Add chat commands to your development workflow

---

*DevO Chat - Making AI-powered development assistance accessible and conversational!* 🚀
