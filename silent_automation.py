#!/usr/bin/env python3
"""
DevO Chat - Silent Automation Agent
Fully automated pipeline with zero user interaction
"""

import os
import sys
import subprocess
import shutil
import time
import json
import signal
import psutil
from pathlib import Path
from datetime import datetime

class SilentAutomationAgent:
    """Fully automated agent that handles everything silently"""
    
    def __init__(self):
        self.root_dir = Path.cwd()
        self.start_time = time.time()
        self.log_file = self.root_dir / "automation.log"
        self.config = {
            "auto_cleanup": True,
            "auto_test": True,
            "auto_package": True,
            "aggressive_cleanup": True,
            "kill_existing_processes": True,
            "create_distribution": True,
            "silent_mode": True
        }
        
    def log(self, message, level="INFO"):
        """Log to both console and file"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        # Console output
        if level == "SUCCESS":
            print(f"✅ {message}")
        elif level == "ERROR":
            print(f"❌ {message}")
        elif level == "WARNING":
            print(f"⚠️  {message}")
        else:
            print(f"ℹ️  {message}")
            
        # File output
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
            
    def run_command_silent(self, command, timeout=300):
        """Run command silently with timeout"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
            
    def kill_existing_processes(self):
        """Kill any existing DevO Chat processes"""
        if not self.config["kill_existing_processes"]:
            return True
            
        self.log("Killing existing processes...")
        
        try:
            # Kill by process name
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and 'devochat' in proc.info['name'].lower():
                    try:
                        proc.terminate()
                        proc.wait(timeout=3)
                    except:
                        try:
                            proc.kill()
                        except:
                            self.log(f"Exception occurred: {e}", "ERROR")
                            
            # Additional cleanup
            success, _, _ = self.run_command_silent("taskkill /F /IM devochat.exe", timeout=10)
            
            # Wait for processes to die
            time.sleep(2)
            
            self.log("Process cleanup completed", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Process cleanup warning: {e}", "WARNING")
            return True  # Continue anyway
            
    def validate_prerequisites(self):
        """Validate and auto-install prerequisites"""
        self.log("Validating prerequisites...")
        
        # Check UV
        success, _, _ = self.run_command_silent("uv --version")
        if not success:
            self.log("UV not found, attempting auto-install...")
            install_cmd = 'powershell -Command "& {Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression}"'
            success, _, error = self.run_command_silent(install_cmd, timeout=120)
            if not success:
                self.log(f"Failed to auto-install UV: {error}", "ERROR")
                return False
                
        # Check Python
        success, _, _ = self.run_command_silent("python --version")
        if not success:
            self.log("Python not found", "ERROR")
            return False
            
        self.log("Prerequisites validated", "SUCCESS")
        return True
        
    def setup_environment(self):
        """Setup environment silently"""
        self.log("Setting up environment...")
        
        success, stdout, stderr = self.run_command_silent("uv sync --extra build", timeout=180)
        if not success:
            self.log(f"Environment setup failed: {stderr}", "ERROR")
            return False
            
        self.log("Environment setup completed", "SUCCESS")
        return True
        
    def validate_code_quality(self):
        """Validate code quality silently"""
        self.log("Validating code quality...")
        
        modules = ["chat", "auto_setup", "utils", "templates", "repocontainerizer"]
        
        for module in modules:
            success, _, error = self.run_command_silent(f'uv run python -c "import {module}"')
            if not success:
                self.log(f"Module {module} validation failed: {error}", "ERROR")
                return False
                
        self.log("Code quality validation completed", "SUCCESS")
        return True
        
    def aggressive_cleanup(self):
        """Perform aggressive cleanup"""
        if not self.config["aggressive_cleanup"]:
            return True
            
        self.log("Performing aggressive cleanup...")
        
        # Directories to clean
        dirs_to_clean = ["build", "dist", "release", "__pycache__"]
        
        for dir_name in dirs_to_clean:
            dir_path = self.root_dir / dir_name
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    time.sleep(0.5)  # Wait for file system
                except Exception as e:
                    self.log(f"Cleanup warning for {dir_name}: {e}", "WARNING")
                    
        # Files to clean
        files_to_clean = list(self.root_dir.glob("*.spec"))
        files_to_clean.extend(list(self.root_dir.glob("*.log")))
        
        for file_path in files_to_clean:
            try:
                file_path.unlink()
            except Exception as e:
                self.log(f"Cleanup warning for {file_path}: {e}", "WARNING")
                
        self.log("Aggressive cleanup completed", "SUCCESS")
        return True
        
    def build_executable(self):
        """Build executable silently"""
        self.log("Building standalone executable...")
        
        build_command = [
            "uv run pyinstaller",
            "--onefile",
            "--console",
            "--name devochat",
            "--distpath dist",
            "--workpath build",
            "--specpath .",
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
            "--clean",
            "--noconfirm",
            "chat.py"
        ]
        
        success, stdout, stderr = self.run_command_silent(" ".join(build_command), timeout=600)
        if not success:
            self.log(f"Build failed: {stderr}", "ERROR")
            # Log build details
            with open(self.root_dir / "build_error.log", "w") as f:
                f.write(f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}")
            return False
            
        self.log("Executable build completed", "SUCCESS")
        return True
        
    def test_executable(self):
        """Test executable silently"""
        if not self.config["auto_test"]:
            return True
            
        self.log("Testing executable...")
        
        exe_path = self.root_dir / "dist" / "devochat.exe"
        if not exe_path.exists():
            self.log("Executable not found", "ERROR")
            return False
            
        # Wait for file system
        time.sleep(2)
        
        success, stdout, stderr = self.run_command_silent(f'"{exe_path}" --help', timeout=30)
        if not success:
            self.log(f"Executable test failed: {stderr}", "ERROR")
            return False
            
        self.log("Executable testing completed", "SUCCESS")
        return True
        
    def create_distribution_package(self):
        """Create distribution package silently"""
        if not self.config["create_distribution"]:
            return True
            
        self.log("Creating distribution package...")
        
        # Create release directory
        release_dir = self.root_dir / "release"
        release_dir.mkdir(exist_ok=True)
        
        # Copy executable
        exe_src = self.root_dir / "dist" / "devochat.exe"
        exe_dst = release_dir / "devochat.exe"
        
        if exe_src.exists():
            shutil.copy2(exe_src, exe_dst)
        else:
            self.log("Executable not found for packaging", "ERROR")
            return False
            
        # Copy documentation
        docs_to_copy = [
            "STANDALONE_EXECUTABLE_GUIDE.md",
            "sample-config.yml",
            "launch_devochat.bat",
            "AUTOMATION_GUIDE.md"
        ]
        
        for doc in docs_to_copy:
            src = self.root_dir / doc
            if src.exists():
                shutil.copy2(src, release_dir / doc)
                
        # Create build info
        build_info = {
            "build_date": datetime.now().isoformat(),
            "build_mode": "Fully Automated",
            "platform": "Windows x64",
            "python_version": "3.11.9",
            "uv_version": "0.7.19",
            "pyinstaller_version": "6.14.2",
            "file_size": exe_dst.stat().st_size,
            "build_time": time.time() - self.start_time
        }
        
        with open(release_dir / "build_info.json", "w") as f:
            json.dump(build_info, f, indent=2)
            
        # Create simple README
        readme_content = f"""# DevO Chat - Ready to Use

## Quick Start
1. Run devochat.exe
2. Set GEMINI_API_KEY environment variable
3. Start chatting with your AI assistant!

## Commands
- analyze <repo-path> - Analyze repository
- containerize <repo-path> - Generate Docker config
- auto-setup <repo-url> - Clone and setup repository
- help - Show available commands
- exit - Exit application

Built automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
File size: {build_info['file_size']:,} bytes
Build time: {build_info['build_time']:.2f} seconds
"""
        
        with open(release_dir / "README.md", "w") as f:
            f.write(readme_content)
            
        self.log("Distribution package created", "SUCCESS")
        return True
        
    def run_silent_automation(self):
        """Run complete silent automation"""
        self.log("🚀 Starting silent automation agent...")
        
        # Clear log file
        if self.log_file.exists():
            self.log_file.unlink()
            
        stages = [
            ("Process Cleanup", self.kill_existing_processes),
            ("Prerequisites Validation", self.validate_prerequisites),
            ("Environment Setup", self.setup_environment),
            ("Code Quality Validation", self.validate_code_quality),
            ("Aggressive Cleanup", self.aggressive_cleanup),
            ("Executable Build", self.build_executable),
            ("Executable Testing", self.test_executable),
            ("Distribution Package", self.create_distribution_package)
        ]
        
        for i, (stage_name, stage_func) in enumerate(stages, 1):
            self.log(f"[{i}/{len(stages)}] {stage_name}")
            if not stage_func():
                self.log(f"Silent automation failed at: {stage_name}", "ERROR")
                return False
                
        total_time = time.time() - self.start_time
        
        # Final success message
        print("\n==========================================")
        print("   🎉 SILENT AUTOMATION COMPLETED! 🎉")
        print("==========================================")
        print(f"✅ All stages completed in {total_time:.2f} seconds")
        print("✅ No user input required")
        print("✅ Executable ready for distribution")
        print("\n📦 Distribution package: release/")
        print("🚀 Main executable: release/devochat.exe")
        
        exe_path = self.root_dir / "release" / "devochat.exe"
        if exe_path.exists():
            print(f"📊 File size: {exe_path.stat().st_size:,} bytes")
            
        print("\n🎯 Ready to distribute immediately!")
        
        self.log(f"Silent automation completed successfully in {total_time:.2f} seconds", "SUCCESS")
        return True

def main():
    """Main entry point"""
    agent = SilentAutomationAgent()
    success = agent.run_silent_automation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()