"""
DevO Chat - Development Automation Tools
Provides automation utilities for development workflow
"""

import os
import sys
import json
import subprocess
import shutil
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class AutomationManager:
    """Manages various automation tasks for DevO Chat"""
    
    def __init__(self):
        self.root_dir = Path.cwd()
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load automation configuration"""
        config_file = self.root_dir / "automation_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return self.get_default_config()
        
    def get_default_config(self) -> Dict:
        """Get default automation configuration"""
        return {
            "build": {
                "clean_before_build": True,
                "run_tests": True,
                "create_distribution": True
            },
            "testing": {
                "run_code_quality": True,
                "run_functionality_tests": True,
                "run_integration_tests": False
            },
            "deployment": {
                "create_release_package": True,
                "upload_to_github": False,
                "notify_on_completion": False
            }
        }
        
    def save_config(self):
        """Save current configuration"""
        config_file = self.root_dir / "automation_config.json"
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def execute_command(self, command: str, description: str = "") -> Tuple[bool, str]:
        """Execute shell command with error handling"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
            
    def validate_environment(self) -> bool:
        """Validate that all required tools are available"""
        required_tools = ["uv", "python", "git"]
        
        for tool in required_tools:
            success, _ = self.execute_command(f"{tool} --version")
            if not success:
                print(f"❌ {tool} not found")
                return False
                
        print("✅ All required tools available")
        return True
        
    def setup_development_environment(self) -> bool:
        """Setup development environment"""
        print("🔧 Setting up development environment...")
        
        # Install dependencies
        success, output = self.execute_command("uv sync --extra build --extra dev")
        if not success:
            print(f"❌ Failed to install dependencies: {output}")
            return False
            
        # Install pre-commit hooks if available
        if (self.root_dir / ".pre-commit-config.yaml").exists():
            success, _ = self.execute_command("uv run pre-commit install")
            if success:
                print("✅ Pre-commit hooks installed")
                
        print("✅ Development environment ready")
        return True
        
    def run_automated_tests(self) -> bool:
        """Run comprehensive automated tests"""
        print("🧪 Running automated tests...")
        
        test_results = []
        
        # Code quality tests
        if self.config["testing"]["run_code_quality"]:
            files = ["chat.py", "auto_setup.py", "utils.py", "templates.py", "repocontainerizer.py"]
            for file in files:
                success, output = self.execute_command(f"uv run python -m py_compile {file}")
                test_results.append((f"Compile {file}", success, output))
                
        # Functionality tests
        if self.config["testing"]["run_functionality_tests"]:
            modules = ["chat", "auto_setup", "utils", "templates", "repocontainerizer"]
            for module in modules:
                success, output = self.execute_command(f'uv run python -c "import {module}"')
                test_results.append((f"Import {module}", success, output))
                
        # Integration tests
        if self.config["testing"]["run_integration_tests"]:
            if (self.root_dir / "test_integration.py").exists():
                success, output = self.execute_command("uv run python test_integration.py")
                test_results.append(("Integration tests", success, output))
                
        # Report results
        passed = sum(1 for _, success, _ in test_results if success)
        total = len(test_results)
        
        print(f"📊 Test Results: {passed}/{total} passed")
        
        for test_name, success, output in test_results:
            status = "✅" if success else "❌"
            print(f"{status} {test_name}")
            if not success and output:
                print(f"   Error: {output[:100]}...")
                
        return passed == total
        
    def build_application(self) -> bool:
        """Build the application"""
        print("🏗️  Building application...")
        
        # Clean previous builds
        if self.config["build"]["clean_before_build"]:
            for dir_name in ["build", "dist"]:
                dir_path = self.root_dir / dir_name
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                    
        # Build executable
        build_command = [
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
        
        success, output = self.execute_command(" ".join(build_command))
        if not success:
            print(f"❌ Build failed: {output}")
            return False
            
        # Test executable
        exe_path = self.root_dir / "dist" / "devochat.exe"
        if not exe_path.exists():
            print("❌ Executable not found")
            return False
            
        success, _ = self.execute_command(f'"{exe_path}" --help')
        if not success:
            print("❌ Executable test failed")
            return False
            
        print("✅ Application built successfully")
        return True
        
    def create_release_package(self) -> bool:
        """Create distribution package"""
        print("📦 Creating release package...")
        
        release_dir = self.root_dir / "release"
        if release_dir.exists():
            shutil.rmtree(release_dir)
        release_dir.mkdir()
        
        # Copy files
        files_to_copy = [
            ("dist/devochat.exe", "devochat.exe"),
            ("STANDALONE_EXECUTABLE_GUIDE.md", "STANDALONE_EXECUTABLE_GUIDE.md"),
            ("sample-config.yml", "sample-config.yml"),
            ("launch_devochat.bat", "launch_devochat.bat")
        ]
        
        for src, dst in files_to_copy:
            src_path = self.root_dir / src
            if src_path.exists():
                shutil.copy2(src_path, release_dir / dst)
                
        # Create build info
        exe_path = release_dir / "devochat.exe"
        build_info = {
            "build_date": datetime.now().isoformat(),
            "version": "1.0.0",
            "platform": "Windows",
            "file_size": exe_path.stat().st_size if exe_path.exists() else 0,
            "python_version": "3.11.9",
            "uv_version": "0.7.19",
            "pyinstaller_version": "6.14.2"
        }
        
        with open(release_dir / "build_info.json", 'w') as f:
            json.dump(build_info, f, indent=2)
            
        print("✅ Release package created")
        return True
        
    def run_full_automation(self) -> bool:
        """Run complete automation pipeline"""
        print("🚀 Starting full automation pipeline...")
        start_time = time.time()
        
        steps = [
            ("Environment Validation", self.validate_environment),
            ("Development Setup", self.setup_development_environment),
            ("Automated Tests", self.run_automated_tests),
            ("Application Build", self.build_application),
            ("Release Package", self.create_release_package)
        ]
        
        for i, (step_name, step_func) in enumerate(steps, 1):
            print(f"\n[{i}/{len(steps)}] {step_name}")
            if not step_func():
                print(f"❌ Pipeline failed at: {step_name}")
                return False
                
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n🎉 Automation pipeline completed in {duration:.2f} seconds!")
        print(f"📦 Release package ready in: {self.root_dir / 'release'}")
        return True

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DevO Chat Automation Manager")
    parser.add_argument("action", choices=["full", "build", "test", "setup", "package"], 
                       help="Action to perform")
    parser.add_argument("--config", help="Path to configuration file")
    
    args = parser.parse_args()
    
    manager = AutomationManager()
    
    if args.config:
        with open(args.config, 'r') as f:
            manager.config = json.load(f)
            
    if args.action == "full":
        success = manager.run_full_automation()
    elif args.action == "build":
        success = manager.build_application()
    elif args.action == "test":
        success = manager.run_automated_tests()
    elif args.action == "setup":
        success = manager.setup_development_environment()
    elif args.action == "package":
        success = manager.create_release_package()
    else:
        print("Unknown action")
        success = False
        
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
