from datetime import datetime
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import time

#!/usr/bin/env python3
"""
DevO Chat - CI/CD Pipeline Automation
Comprehensive automation for build, test, and deployment
"""


class DevOPipeline:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.build_dir = self.root_dir / "build"
        self.dist_dir = self.root_dir / "dist"
        self.release_dir = self.root_dir / "release"
        self.start_time = time.time()
        
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "✅" if level == "SUCCESS" else "❌" if level == "ERROR" else "ℹ️"
        print(f"[{timestamp}] {prefix} {message}")
        
    def run_command(self, command, description=""):
        """Execute command with error handling"""
        if description:
            self.log(f"Running: {description}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}", "ERROR")
            self.log(f"stdout: {e.stdout}", "ERROR")
            self.log(f"stderr: {e.stderr}", "ERROR")
            return False
            
    def check_prerequisites(self):
        """Check if all required tools are available"""
        self.log("Checking prerequisites...")
        
        # Check UV
        if not self.run_command("uv --version", "Checking UV"):
            self.log("UV package manager not found!", "ERROR")
            return False
            
        # Check Python
        if not self.run_command("python --version", "Checking Python"):
            self.log("Python not found!", "ERROR")
            return False
            
        self.log("Prerequisites check passed", "SUCCESS")
        return True
        
    def setup_environment(self):
        """Setup Python environment with all dependencies"""
        self.log("Setting up environment...")
        
        if not self.run_command("uv sync --extra build", "Installing dependencies"):
            return False
            
        self.log("Environment setup complete", "SUCCESS")
        return True
        
    def run_quality_checks(self):
        """Run code quality and syntax checks"""
        self.log("Running code quality checks...")
        
        files_to_check = [
            "chat.py",
            "auto_setup.py", 
            "utils.py",
            "templates.py",
            "repocontainerizer.py"
        ]
        
        for file in files_to_check:
            if not self.run_command(f"uv run python -m py_compile {file}", f"Checking {file}"):
                return False
                
        self.log("Code quality checks passed", "SUCCESS")
        return True
        
    def run_functionality_tests(self):
        """Test module imports and basic functionality"""
        self.log("Running functionality tests...")
        
        tests = [
            ("import chat", "Chat module"),
            ("import auto_setup", "Auto setup module"),
            ("import utils", "Utils module"),
            ("import templates", "Templates module"),
            ("import repocontainerizer", "Containerizer module")
        ]
        
        for test_code, description in tests:
            if not self.run_command(f'uv run python -c "{test_code}"', description):
                return False
                
        self.log("Functionality tests passed", "SUCCESS")
        return True
        
    def clean_build(self):
        """Clean previous build artifacts"""
        self.log("Cleaning previous builds...")
        
        dirs_to_clean = [self.build_dir, self.dist_dir]
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                
        # Clean spec files
        for spec_file in self.root_dir.glob("*.spec"):
            spec_file.unlink()
            
        self.log("Build cleanup complete", "SUCCESS")
        return True
        
    def build_executable(self):
    # TODO: Consider breaking this function into smaller functions
        """Build standalone executable using PyInstaller"""
        self.log("Building standalone executable...")
        
        command = [
            "uv run pyinstaller",
            "--onefile",
            "--console", 
            "--name devochat",
            "--add-data sample-config.yml;.",
            "--add-data templates.py;.",
            "--add-data utils.py;.",
            "--add-data auto_setup.py;.",
            "--add-data repocontainerizer.py;.",
            "--collect-all google.generativeai",
            "--collect-all rich",
            "--collect-all click",
            "--collect-all yaml",
            "--collect-all requests",
            "--collect-all git",
            "--collect-all dotenv",
            "--hidden-import=google.generativeai",
            "--hidden-import=rich",
            "--hidden-import=click",
            "--hidden-import=yaml",
            "--hidden-import=requests",
            "--hidden-import=git",
            "--hidden-import=dotenv",
            "--hidden-import=os",
            "--hidden-import=sys",
            "--hidden-import=json",
            "--hidden-import=subprocess",
            "--hidden-import=pathlib",
            "chat.py"
        ]
        
        if not self.run_command(" ".join(command), "Building executable"):
            return False
            
        self.log("Executable build complete", "SUCCESS")
        return True
        
    def test_executable(self):
        """Test the built executable"""
        self.log("Testing standalone executable...")
        
        exe_path = self.dist_dir / "devochat.exe"
        if not exe_path.exists():
            self.log("Executable not found!", "ERROR")
            return False
            
        # Test help command
        if not self.run_command(f'"{exe_path}" --help', "Testing help command"):
            return False
            
        self.log("Executable tests passed", "SUCCESS")
        return True
        
    def create_distribution_package(self):
        """Create distribution package"""
        self.log("Creating distribution package...")
        
        # Create release directory
        if self.release_dir.exists():
            shutil.rmtree(self.release_dir)
        self.release_dir.mkdir()
        
        # Copy executable
        exe_src = self.dist_dir / "devochat.exe"
        exe_dst = self.release_dir / "devochat.exe"
        shutil.copy2(exe_src, exe_dst)
        
        # Copy documentation and config
        files_to_copy = [
            "STANDALONE_EXECUTABLE_GUIDE.md",
            "sample-config.yml",
            "launch_devochat.bat"
        ]
        
        for file in files_to_copy:
            src = self.root_dir / file
            if src.exists():
                shutil.copy2(src, self.release_dir / file)
                
        # Create version info
        version_info = {
            "build_date": datetime.now().isoformat(),
            "python_version": "3.11.9",
            "uv_version": "0.7.19",
            "pyinstaller_version": "6.14.2",
            "file_size": exe_dst.stat().st_size,
            "build_time": time.time() - self.start_time
        }
        
        with open(self.release_dir / "version.json", "w") as f:
            json.dump(version_info, f, indent=2)
            
        # Create README for release
        readme_content = f"""# DevO Chat - Standalone Release

## Quick Start
1. Run `devochat.exe` or use `launch_devochat.bat`
2. Set your Gemini API key as environment variable: `GEMINI_API_KEY`
3. Start chatting with the AI assistant!

## Build Information
- Build Date: {version_info['build_date']}
- File Size: {version_info['file_size']:,} bytes
- Build Time: {version_info['build_time']:.2f} seconds

## Files Included
- `devochat.exe` - Main executable
- `launch_devochat.bat` - Easy launcher
- `STANDALONE_EXECUTABLE_GUIDE.md` - User guide
- `sample-config.yml` - Configuration template
- `version.json` - Build information

## Features
✅ Unified chat interface for all development tasks
✅ Repository analysis with AI suggestions  
✅ Auto setup (clone repos + install dependencies)
✅ Containerization (Docker file generation)
✅ AI-powered code suggestions using Gemini
✅ Dependency management and error fixing
✅ Session management (save/load conversations)
✅ Rich terminal UI with progress indicators
✅ Windows PowerShell compatibility

Ready for distribution! 🚀
"""
        
        with open(self.release_dir / "README.md", "w") as f:
            f.write(readme_content)
            
        self.log("Distribution package created", "SUCCESS")
        return True
        
    def run_full_pipeline(self):
    # TODO: Consider breaking this function into smaller functions
        """Execute the complete automation pipeline"""
        self.log("🚀 Starting DevO Chat Automation Pipeline")
        
        stages = [
            ("Prerequisites Check", self.check_prerequisites),
            ("Environment Setup", self.setup_environment),
            ("Code Quality Checks", self.run_quality_checks),
            ("Functionality Tests", self.run_functionality_tests),
            ("Build Cleanup", self.clean_build),
            ("Executable Build", self.build_executable),
            ("Executable Tests", self.test_executable),
            ("Distribution Package", self.create_distribution_package)
        ]
        
        for i, (stage_name, stage_func) in enumerate(stages, 1):
            self.log(f"[{i}/{len(stages)}] {stage_name}")
            if not stage_func():
                self.log(f"Pipeline failed at: {stage_name}", "ERROR")
                return False
                
        total_time = time.time() - self.start_time
        self.log(f"🎉 Pipeline completed successfully in {total_time:.2f} seconds!", "SUCCESS")
        self.log(f"📦 Distribution ready in: {self.release_dir}")
        return True

def main():
    """Main entry point"""
    pipeline = DevOPipeline()
    success = pipeline.run_full_pipeline()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()