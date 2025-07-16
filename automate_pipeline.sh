#!/bin/bash
# DevO Chat - Cross-Platform Automation Script
# Works on Linux, macOS, and Windows (Git Bash)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "[${timestamp}] ${BLUE}ℹ️  ${message}${NC}"
            ;;
        "SUCCESS")
            echo -e "[${timestamp}] ${GREEN}✅ ${message}${NC}"
            ;;
        "ERROR")
            echo -e "[${timestamp}] ${RED}❌ ${message}${NC}"
            ;;
        "WARNING")
            echo -e "[${timestamp}] ${YELLOW}⚠️  ${message}${NC}"
            ;;
    esac
}

# Check prerequisites
check_prerequisites() {
    log "INFO" "Checking prerequisites..."
    
    # Check UV
    if ! command -v uv &> /dev/null; then
        log "ERROR" "UV package manager not found!"
        log "INFO" "Install from: https://docs.astral.sh/uv/"
        exit 1
    fi
    
    # Check Python
    if ! command -v python &> /dev/null; then
        log "ERROR" "Python not found!"
        exit 1
    fi
    
    log "SUCCESS" "Prerequisites check passed"
}

# Setup environment
setup_environment() {
    log "INFO" "Setting up environment..."
    
    if ! uv sync --extra build; then
        log "ERROR" "Failed to setup environment"
        exit 1
    fi
    
    log "SUCCESS" "Environment setup complete"
}

# Run quality checks
run_quality_checks() {
    log "INFO" "Running code quality checks..."
    
    local files=("chat.py" "auto_setup.py" "utils.py" "templates.py" "repocontainerizer.py")
    
    for file in "${files[@]}"; do
        if ! uv run python -m py_compile "$file"; then
            log "ERROR" "Code quality check failed for $file"
            exit 1
        fi
    done
    
    log "SUCCESS" "Code quality checks passed"
}

# Run functionality tests
run_functionality_tests() {
    log "INFO" "Running functionality tests..."
    
    local tests=(
        "import chat"
        "import auto_setup"
        "import utils"
        "import templates"
        "import repocontainerizer"
    )
    
    for test in "${tests[@]}"; do
        if ! uv run python -c "$test"; then
            log "ERROR" "Functionality test failed: $test"
            exit 1
        fi
    done
    
    log "SUCCESS" "Functionality tests passed"
}

# Clean build
clean_build() {
    log "INFO" "Cleaning previous builds..."
    
    rm -rf build dist *.spec
    
    log "SUCCESS" "Build cleanup complete"
}

# Build executable
build_executable() {
    log "INFO" "Building standalone executable..."
    
    local build_cmd=(
        "uv run pyinstaller"
        "--onefile"
        "--console"
        "--name devochat"
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
        "chat.py"
    )
    
    if ! "${build_cmd[@]}"; then
        log "ERROR" "Build failed"
        exit 1
    fi
    
    log "SUCCESS" "Executable build complete"
}

# Test executable
test_executable() {
    log "INFO" "Testing standalone executable..."
    
    local exe_name="devochat"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        exe_name="devochat.exe"
    fi
    
    if [[ ! -f "dist/$exe_name" ]]; then
        log "ERROR" "Executable not found: dist/$exe_name"
        exit 1
    fi
    
    if ! "./dist/$exe_name" --help > /dev/null 2>&1; then
        log "ERROR" "Executable test failed"
        exit 1
    fi
    
    log "SUCCESS" "Executable tests passed"
}

# Create distribution package
create_distribution_package() {
    log "INFO" "Creating distribution package..."
    
    # Create release directory
    rm -rf release
    mkdir -p release
    
    # Determine executable name
    local exe_name="devochat"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        exe_name="devochat.exe"
    fi
    
    # Copy files
    cp "dist/$exe_name" release/
    cp STANDALONE_EXECUTABLE_GUIDE.md release/ 2>/dev/null || true
    cp sample-config.yml release/ 2>/dev/null || true
    cp launch_devochat.bat release/ 2>/dev/null || true
    
    # Create version info
    cat > release/BUILD_INFO.txt << EOF
DevO Chat - Standalone Executable
Build Date: $(date)
Platform: $(uname -s)
Architecture: $(uname -m)
File Size: $(stat -c%s "release/$exe_name" 2>/dev/null || stat -f%z "release/$exe_name") bytes
Python Version: $(python --version)
UV Version: $(uv --version)
EOF
    
    # Create README
    cat > release/README.md << EOF
# DevO Chat - Standalone Release

## Quick Start
1. Run \`$exe_name\` or use launcher script
2. Set your Gemini API key as environment variable: \`GEMINI_API_KEY\`
3. Start chatting with the AI assistant!

## Build Information
- Build Date: $(date)
- Platform: $(uname -s) $(uname -m)
- File Size: $(stat -c%s "release/$exe_name" 2>/dev/null || stat -f%z "release/$exe_name") bytes

## Features
✅ Unified chat interface for all development tasks
✅ Repository analysis with AI suggestions  
✅ Auto setup (clone repos + install dependencies)
✅ Containerization (Docker file generation)
✅ AI-powered code suggestions using Gemini
✅ Dependency management and error fixing
✅ Session management (save/load conversations)
✅ Rich terminal UI with progress indicators

Ready for distribution! 🚀
EOF
    
    log "SUCCESS" "Distribution package created"
}

# Main pipeline
run_full_pipeline() {
    local start_time=$(date +%s)
    
    log "INFO" "🚀 Starting DevO Chat Automation Pipeline"
    
    local stages=(
        "Prerequisites Check:check_prerequisites"
        "Environment Setup:setup_environment"
        "Code Quality Checks:run_quality_checks"
        "Functionality Tests:run_functionality_tests"
        "Build Cleanup:clean_build"
        "Executable Build:build_executable"
        "Executable Tests:test_executable"
        "Distribution Package:create_distribution_package"
    )
    
    local total_stages=${#stages[@]}
    local current_stage=1
    
    for stage in "${stages[@]}"; do
        local stage_name="${stage%%:*}"
        local stage_func="${stage##*:}"
        
        log "INFO" "[$current_stage/$total_stages] $stage_name"
        
        if ! $stage_func; then
            log "ERROR" "Pipeline failed at: $stage_name"
            exit 1
        fi
        
        ((current_stage++))
    done
    
    local end_time=$(date +%s)
    local total_time=$((end_time - start_time))
    
    log "SUCCESS" "🎉 Pipeline completed successfully in ${total_time}s!"
    log "INFO" "📦 Distribution ready in: $(pwd)/release"
}

# Handle command line arguments
case "${1:-full}" in
    "full")
        run_full_pipeline
        ;;
    "build")
        check_prerequisites
        setup_environment
        clean_build
        build_executable
        test_executable
        ;;
    "test")
        check_prerequisites
        setup_environment
        run_quality_checks
        run_functionality_tests
        ;;
    "clean")
        clean_build
        ;;
    "package")
        create_distribution_package
        ;;
    *)
        echo "Usage: $0 [full|build|test|clean|package]"
        echo "  full    - Run complete pipeline (default)"
        echo "  build   - Build executable only"
        echo "  test    - Run tests only"
        echo "  clean   - Clean build artifacts"
        echo "  package - Create distribution package"
        exit 1
        ;;
esac
