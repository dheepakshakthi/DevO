#!/usr/bin/env python3
"""
RepoContainerizer Demo Script
Demonstrates all the features of the standalone CLI application
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and display the output"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def main():
    """Run the complete demo"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🎯 RepoContainerizer Demo                 ║
║              Complete Feature Demonstration                  ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Check if we're in the right directory
    if not Path("repocontainerizer.py").exists():
        print("❌ repocontainerizer.py not found in current directory")
        print("Please run this demo from the RepoContainerizer directory")
        sys.exit(1)
    
    print("This demo will showcase all the features of RepoContainerizer")
    input("Press Enter to continue...")
    
    # Demo commands
    demos = [
        ("python repocontainerizer.py version", "Version Information"),
        ("python repocontainerizer.py help", "Help System"),
        ("python repocontainerizer.py config", "Configuration Management"),
        ("python repocontainerizer.py config set default_output_dir ./demo_output",
            "Setting Configuration"),
        ("python repocontainerizer.py config get default_output_dir", "Getting Configuration"),
    ]
    
    for cmd, description in demos:
        if not run_command(cmd, description):
            print(f"❌ Failed to run: {cmd}")
        
        print("\nPress Enter to continue to next demo...")
        input()
    
    print(f"\n{'='*60}")
    print("🎉 Demo Complete!")
    print(f"{'='*60}")
    print("\nRepoContainerizer Features Demonstrated:")
    print("✅ Version information display")
    print("✅ Comprehensive help system")
    print("✅ Configuration management")
    print("✅ Interactive setup capability")
    print("✅ Error handling and user feedback")
    print("✅ Warp-inspired beautiful CLI interface")
    
    print("\n🎯 Next Steps:")
    print("1. Set up your API key: python repocontainerizer.py setup")
    print("2. Containerize a repository: python repocontainerizer.py containerize https://github.com/owner/repo")
    print("3. Or use the Windows interface: repocontainerizer.bat")
    
    print("\n📚 Documentation:")
    print("- README.md - Complete project documentation")
    print("- STANDALONE_GUIDE.md - Detailed usage guide")
    print("- QUICK_START.md - Quick start instructions")
    
    print("\n🔧 Build Options:")
    print("- python build_standalone.py - Create standalone executable")
    print("- repocontainerizer.bat - Windows interactive interface")
    print("- python test_standalone.py - Run test suite")

if __name__ == "__main__":
    main()