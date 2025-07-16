#!/bin/bash
# DevO Chat - Silent Automation Agent (Cross-Platform)
# Fully automated pipeline with zero user interaction

set -e

# Silent mode configuration
SILENT_MODE=true
AUTO_CLEANUP=true
AUTO_TEST=true
AUTO_PACKAGE=true
AGGRESSIVE_CLEANUP=true
KILL_EXISTING_PROCESSES=true

# Colors for output (can be disabled in silent mode)
if [ "$SILENT_MODE" = true ]; then
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
else
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
fi

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%H:%M:%S')
    
    case $level in
        "SUCCESS")
            echo -e "[${timestamp}] ${GREEN}✅ ${message}${NC}"
            ;;
        "ERROR")
            echo -e "[${timestamp}] ${RED}❌ ${message}${NC}"
            ;;
        "WARNING")
            echo -e "[${timestamp}] ${YELLOW}⚠️  ${message}${NC}"
            ;;
        *)
            echo -e "[${timestamp}] ${BLUE}ℹ️  ${message}${NC}"
            ;;
    esac
    
    # Log to file
    echo "[${timestamp}] ${level}: ${message}" >> automation.log
}

# Kill existing processes
kill_existing_processes() {
    if [ "$KILL_EXISTING_PROCESSES" = true ]; then
        log "INFO" "Killing existing processes..."
        
        # Kill by process name
        pkill -f devochat 2>/dev/null || true
        
        # Windows-specific
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
            taskkill //F //IM devochat.exe 2>/dev/null || true
        fi
        
        # Wait for processes to die
        sleep 2
        
        log "SUCCESS" "Process cleanup completed"
    fi
}

# Validate prerequisites
validate_prerequisites() {
    log "INFO" "Validating prerequisites..."
    
    # Check UV
    if ! command -v uv &> /dev/null; then
        log "WARNING" "UV not found, attempting auto-install..."
        
        # Auto-install UV
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
            # Windows
            powershell -Command "& {Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression}" || {
                log "ERROR" "Failed to auto-install UV"
                exit 1
            }
        else
            # Unix-like systems
            curl -LsSf https://astral.sh/uv/install.sh | sh || {
                log "ERROR" "Failed to auto-install UV"
                exit 1
            }
        fi
    fi
    
    # Check Python
    if ! command -v python &> /dev/null; then
        log "ERROR" "Python not found"
        exit 1
    fi
    
    log "SUCCESS" "Prerequisites validated"
}

# Setup environment
setup_environment() {
    log "INFO" "Setting up environment..."
    
    if ! uv sync --extra build --quiet; then
        log "ERROR" "Environment setup failed"
        exit 1
    fi
    
    log "SUCCESS" "Environment setup completed"
}

# Validate code quality
validate_code_quality() {
    log "INFO" "Validating code quality..."
    
    local modules=("chat" "auto_setup" "utils" "templates" "repocontainerizer")
    
    for module in "${modules[@]}"; do
        if ! uv run python -c "import $module" &>/dev/null; then
            log "ERROR" "Module $module validation failed"
            exit 1
        fi
    done
    
    log "SUCCESS" "Code quality validation completed"
}

# Aggressive cleanup
aggressive_cleanup() {
    if [ "$AGGRESSIVE_CLEANUP" = true ]; then
        log "INFO" "Performing aggressive cleanup..."
        
        # Remove directories
        rm -rf build dist release __pycache__ 2>/dev/null || true
        
        # Remove files
        rm -f *.spec *.log 2>/dev/null || true
        
        # Wait for file system
        sleep 1
        
        log "SUCCESS" "Aggressive cleanup completed"
    fi
}

# Build executable
build_executable() {
    log "INFO" "Building standalone executable..."
    
    # Determine executable extension
    local exe_ext=""
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        exe_ext=".exe"
    fi
    
    # Build command
    local build_cmd=(
        "uv run pyinstaller"
        "--onefile"
        "--console"
        "--name devochat"
        "--distpath dist"
        "--workpath build"
        "--specpath ."
        "--add-data sample-config.yml:."
        "--add-data templates.py:."
        "--add-data utils.py:."
        "--add-data auto_setup.py:."
        "--add-data repocontainerizer.py:."
        "--collect-all google.generativeai"
        "--collect-all rich"
        "--collect-all click"
        "--collect-all yaml"
        "--collect-all requests"
        "--collect-all git"
        "--collect-all dotenv"
        "--hidden-import=google.generativeai"
        "--hidden-import=rich"
        "--hidden-import=click"
        "--hidden-import=yaml"
        "--hidden-import=requests"
        "--hidden-import=git"
        "--hidden-import=dotenv"
        "--hidden-import=os"
        "--hidden-import=sys"
        "--hidden-import=json"
        "--hidden-import=subprocess"
        "--hidden-import=pathlib"
        "--clean"
        "--noconfirm"
        "chat.py"
    )
    
    # Execute build
    if ! "${build_cmd[@]}" > build.log 2>&1; then
        log "ERROR" "Build failed - check build.log"
        exit 1
    fi
    
    log "SUCCESS" "Executable build completed"
}

# Test executable
test_executable() {
    if [ "$AUTO_TEST" = true ]; then
        log "INFO" "Testing executable..."
        
        # Determine executable name
        local exe_name="devochat"
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
            exe_name="devochat.exe"
        fi
        
        # Check if executable exists
        if [[ ! -f "dist/$exe_name" ]]; then
            log "ERROR" "Executable not found: dist/$exe_name"
            exit 1
        fi
        
        # Wait for file system
        sleep 2
        
        # Test executable
        if ! "./dist/$exe_name" --help > /dev/null 2>&1; then
            log "ERROR" "Executable test failed"
            exit 1
        fi
        
        log "SUCCESS" "Executable testing completed"
    fi
}

# Create distribution package
create_distribution_package() {
    if [ "$AUTO_PACKAGE" = true ]; then
        log "INFO" "Creating distribution package..."
        
        # Create release directory
        mkdir -p release
        
        # Determine executable name
        local exe_name="devochat"
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
            exe_name="devochat.exe"
        fi
        
        # Copy executable
        cp "dist/$exe_name" release/
        
        # Copy documentation
        local docs=("STANDALONE_EXECUTABLE_GUIDE.md" "sample-config.yml" "launch_devochat.bat" "AUTOMATION_GUIDE.md")
        for doc in "${docs[@]}"; do
            if [[ -f "$doc" ]]; then
                cp "$doc" release/
            fi
        done
        
        # Create build info
        cat > release/BUILD_INFO.txt << EOF
DevO Chat - Automated Build
Build Date: $(date)
Build Mode: Fully Automated Silent
Platform: $(uname -s) $(uname -m)
Python Version: $(python --version)
UV Version: $(uv --version)
File Size: $(stat -c%s "release/$exe_name" 2>/dev/null || stat -f%z "release/$exe_name") bytes
EOF
        
        # Create README
        cat > release/README.md << EOF
# DevO Chat - Ready to Use

## Quick Start
1. Run $exe_name
2. Set GEMINI_API_KEY environment variable
3. Start chatting with your AI assistant!

## Commands
- analyze <repo-path> - Analyze repository
- containerize <repo-path> - Generate Docker config
- auto-setup <repo-url> - Clone and setup repository
- help - Show available commands
- exit - Exit application

Built automatically on $(date)
File size: $(stat -c%s "release/$exe_name" 2>/dev/null || stat -f%z "release/$exe_name") bytes
EOF
        
        log "SUCCESS" "Distribution package created"
    fi
}

# Main silent automation
run_silent_automation() {
    local start_time=$(date +%s)
    
    # Clear log file
    > automation.log
    
    log "INFO" "🚀 Starting silent automation agent..."
    
    echo "========================================"
    echo "  DevO Chat - Silent Automation Agent"
    echo "========================================"
    echo "Running in silent mode - no user input required"
    echo ""
    
    # Run stages
    local stages=(
        "Process Cleanup:kill_existing_processes"
        "Prerequisites Validation:validate_prerequisites"
        "Environment Setup:setup_environment"
        "Code Quality Validation:validate_code_quality"
        "Aggressive Cleanup:aggressive_cleanup"
        "Executable Build:build_executable"
        "Executable Testing:test_executable"
        "Distribution Package:create_distribution_package"
    )
    
    local total_stages=${#stages[@]}
    local current_stage=1
    
    for stage in "${stages[@]}"; do
        local stage_name="${stage%%:*}"
        local stage_func="${stage##*:}"
        
        log "INFO" "[$current_stage/$total_stages] $stage_name"
        
        if ! $stage_func; then
            log "ERROR" "Silent automation failed at: $stage_name"
            exit 1
        fi
        
        ((current_stage++))
    done
    
    local end_time=$(date +%s)
    local total_time=$((end_time - start_time))
    
    # Success message
    echo ""
    echo "========================================"
    echo "   🎉 SILENT AUTOMATION COMPLETED! 🎉"
    echo "========================================"
    echo "✅ All stages completed in ${total_time}s"
    echo "✅ No user input required"
    echo "✅ Executable ready for distribution"
    echo ""
    echo "📦 Distribution package: $(pwd)/release"
    echo "🚀 Main executable: $(pwd)/release/devochat*"
    echo "📊 File size: $(stat -c%s "release/devochat"* 2>/dev/null || stat -f%z "release/devochat"*) bytes"
    echo ""
    echo "🎯 Ready to distribute immediately!"
    echo ""
    
    log "SUCCESS" "Silent automation completed successfully in ${total_time}s"
}

# Run the automation
run_silent_automation
