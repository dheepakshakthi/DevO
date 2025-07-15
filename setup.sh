#!/bin/bash
echo "Installing RepoContainerizer..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed or not in PATH"
    exit 1
fi

# Install required packages
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Warning: Git is not installed or not in PATH"
    echo "Please install Git for repository cloning functionality"
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "Warning: Docker is not installed or not in PATH"
    echo "Please install Docker for container validation functionality"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To use RepoContainerizer, set your Gemini API key:"
echo "export GEMINI_API_KEY=your_api_key_here"
echo ""
echo "Then run:"
echo "python3 repo_containerizer.py --help"
echo ""
