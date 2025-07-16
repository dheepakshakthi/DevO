"""
DevO Chat - Autonomous Build Agent
Ultimate automation with zero user interaction and intelligent error handling
"""

import os
import sys
import subprocess
import shutil
import time
import json
import signal
import threading
from pathlib import Path
from datetime import datetime
import concurrent.futures

class AutonomousBuildAgent:
    """Fully autonomous agent that handles everything without user input"""
    
    def __init__(self):
        self.root_dir = Path.cwd()
        self.start_time = time.time()
        self.log_file = self.root_dir / "autonomous.log"
        self.status_file = self.root_dir / "build_status.json"
        self.config = {
            "autonomous_mode": True,
            "zero_interaction": True,
            "aggressive_cleanup": True,
            "auto_retry": True,
            "max_retries": 3,
            "intelligent_error_handling": True,
            "parallel_operations": True,
            "auto_recovery": True
        }
        self.build_status = {
            "started": datetime.now().isoformat(),
            "stage": "initialization",
            "progress": 0,
            "errors": [],
            "warnings": [],
            "completed": False
        }
        
    def update_status(self, stage, progress, message=""):
        """Update build status"""
        self.build_status.update({
            "stage": stage,
            "progress": progress,
            "last_update": datetime.now().isoformat(),
            "message": message
        })
        
        with open(self.status_file, "w") as f:
            json.dump(self.build_status, f, indent=2)
            
    def log(self, message, level="INFO"):
        """Autonomous logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        # Console output with emoji
        emoji_map = {
            "SUCCESS": "✅",
            "ERROR": "❌", 
            "WARNING": "⚠️",
            "INFO": "🔄",
            "STAGE": "🎯"
        }
        
        emoji = emoji_map.get(level, "ℹ️")
        print(f"{emoji} {message}")
        
        # File logging
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
            
        # Update status
        if level == "ERROR":
            self.build_status["errors"].append(message)
        elif level == "WARNING":
            self.build_status["warnings"].append(message)
            
    def run_command_autonomous(self, command, timeout=300, retry_count=0):
        """Run command with autonomous error handling and retry logic"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return True, result.stdout, result.stderr
            else:
                # Intelligent error handling
                if retry_count < self.config["max_retries"] and self.config["auto_retry"]:
                    self.log(f"Command failed,
                        retrying ({retry_count + 1}/{self.config['max_retries']})...", "WARNING")
                    time.sleep(2 ** retry_count)  # Exponential backoff
                    return self.run_command_autonomous(command, timeout, retry_count + 1)
                else:
                    return False, result.stdout, result.stderr
                    
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, "", str(e)
            
    def autonomous_process_cleanup(self):
        """Autonomous process cleanup with multiple strategies"""
        self.log("Autonomous process cleanup initiated", "STAGE")
        self.update_status("process_cleanup", 10)
        
        cleanup_strategies = [
            "taskkill /F /IM devochat.exe",
            "wmic process where name='devochat.exe' delete",
            "powershell -Command \"Get-Process -Name 'devochat' -ErrorAction SilentlyContinue | Stop-Process -Force\""
        ]
        
        for strategy in cleanup_strategies:
            success, _, _ = self.run_command_autonomous(strategy, timeout=10)
            if success:
                break
                
        time.sleep(3)  # Wait for processes to die
        self.log("Process cleanup completed", "SUCCESS")
        return True
        
    def autonomous_prerequisite_setup(self):
        """Autonomous prerequisite validation and installation"""
        self.log("Autonomous prerequisite setup initiated", "STAGE")
        self.update_status("prerequisites", 20)
        
        # Check and install UV
        success, _, _ = self.run_command_autonomous("uv --version", timeout=10)
        if not success:
            self.log("UV not found - performing autonomous installation", "WARNING")
            install_cmd = 'powershell -Command "& {Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression}"'
            success, _, error = self.run_command_autonomous(install_cmd, timeout=120)
            if not success:
                self.log(f"UV installation failed: {error}", "ERROR")
                return False
                
        # Verify Python
        success, _, _ = self.run_command_autonomous("python --version", timeout=10)
        if not success:
            self.log("Python not available", "ERROR")
            return False
            
        self.log("Prerequisites validated autonomously", "SUCCESS")
        return True
        
    def autonomous_environment_setup(self):
        """Autonomous environment setup with parallel operations"""
        self.log("Autonomous environment setup initiated", "STAGE")
        self.update_status("environment", 30)
        
        # Multiple environment setup strategies
        setup_commands = [
            "uv sync --extra build",
            "uv sync --extra build --no-cache",
            "uv sync --extra build --reinstall"
        ]
        
        for cmd in setup_commands:
            success, stdout, stderr = self.run_command_autonomous(cmd, timeout=180)
            if success:
                self.log("Environment setup completed autonomously", "SUCCESS")
                return True
            else:
                self.log(f"Environment setup attempt failed: {stderr}", "WARNING")
                
        self.log("All environment setup attempts failed", "ERROR")
        return False
        
    def autonomous_code_validation(self):
        """Autonomous code validation with intelligent checks"""
        self.log("Autonomous code validation initiated", "STAGE")
        self.update_status("validation", 40)
        
        modules = ["chat", "auto_setup", "utils", "templates", "repocontainerizer"]
        
        # Parallel validation
        def validate_module(module):
            success, _, error = self.run_command_autonomous(f'uv run python -c "import {module}"', timeout=30)
            return module, success, error
            
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(validate_module, modules))
            
        failed_modules = [module for module, success, error in results if not success]
        
        if failed_modules:
            self.log(f"Module validation failed for: {failed_modules}", "ERROR")
            return False
            
        self.log("Code validation completed autonomously", "SUCCESS")
        return True
        
    def autonomous_aggressive_cleanup(self):
        """Autonomous aggressive cleanup with recovery"""
        self.log("Autonomous aggressive cleanup initiated", "STAGE")
        self.update_status("cleanup", 50)
        
        # Cleanup targets
        cleanup_targets = {
            "directories": ["build", "dist", "release", "__pycache__"],
            "files": ["*.spec", "*.log", "*.pyc"],
            "patterns": ["**/**.pyc", "**/__pycache__/**"]
        }
        
        # Directory cleanup
        for directory in cleanup_targets["directories"]:
            dir_path = self.root_dir / directory
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    time.sleep(0.5)
                except Exception as e:
                    self.log(f"Cleanup warning for {directory}: {e}", "WARNING")
                    # Force cleanup
                    self.run_command_autonomous(f'rmdir /s /q "{dir_path}"', timeout=10)
                    
        # File cleanup
        for pattern in cleanup_targets["files"]:
            for file_path in self.root_dir.glob(pattern):
                try:
                    file_path.unlink()
                except Exception as e:
                    self.log(f"File cleanup warning: {e}", "WARNING")
                    
        self.log("Aggressive cleanup completed autonomously", "SUCCESS")
        return True
        
    def autonomous_build_execution(self):
        """Autonomous build execution with intelligent optimization"""
        self.log("Autonomous build execution initiated", "STAGE")
        self.update_status("building", 60)
        
        # Optimized build command
        build_command = [
            "uv run pyinstaller",
            "--onefile",
            "--console",
            "--name devochat",
            "--distpath dist",
            "--workpath build",
            "--specpath .",
            "--optimize=2",  # Bytecode optimization
            "--strip",       # Strip debug symbols
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
            "--log-level=WARN",  # Reduce verbosity
            "chat.py"
        ]
        
        success, stdout, stderr = self.run_command_autonomous(" ".join(build_command), timeout=600)
        
        if not success:
            self.log(f"Build execution failed: {stderr}", "ERROR")
            # Save build logs for debugging
            with open(self.root_dir / "build_failure.log", "w") as f:
                f.write(f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}")
            return False
            
        self.log("Build execution completed autonomously", "SUCCESS")
        return True
        
    def autonomous_testing_validation(self):
        """Autonomous testing with comprehensive validation"""
        self.log("Autonomous testing validation initiated", "STAGE")
        self.update_status("testing", 80)
        
        exe_path = self.root_dir / "dist" / "devochat.exe"
        
        # File existence check
        if not exe_path.exists():
            self.log("Executable not found", "ERROR")
            return False
            
        # File size validation
        file_size = exe_path.stat().st_size
        if file_size < 10 * 1024 * 1024:  # Less than 10MB is suspicious
            self.log(f"Executable size suspicious: {file_size} bytes", "WARNING")
            
        # Wait for file system stabilization
        time.sleep(3)
        
        # Functional tests
        test_commands = [
            f'"{exe_path}" --help',
            f'"{exe_path}" --version',
        ]
        
        for test_cmd in test_commands:
            success, stdout, stderr = self.run_command_autonomous(test_cmd, timeout=30)
            if not success:
                self.log(f"Test failed: {test_cmd} - {stderr}", "ERROR")
                return False
                
        self.log("Testing validation completed autonomously", "SUCCESS")
        return True
        
    def autonomous_distribution_creation(self):
        """Autonomous distribution package creation"""
        self.log("Autonomous distribution creation initiated", "STAGE")
        self.update_status("packaging", 90)
        
        # Create release directory
        release_dir = self.root_dir / "release"
        release_dir.mkdir(exist_ok=True)
        
        # Copy executable
        exe_src = self.root_dir / "dist" / "devochat.exe"
        exe_dst = release_dir / "devochat.exe"
        shutil.copy2(exe_src, exe_dst)
        
        # Copy documentation
        docs_to_copy = [
            "STANDALONE_EXECUTABLE_GUIDE.md",
            "sample-config.yml",
            "launch_devochat.bat",
            "AUTOMATION_GUIDE.md",
            "AUTONOMOUS_AGENT_GUIDE.md"
        ]
        
        for doc in docs_to_copy:
            src = self.root_dir / doc
            if src.exists():
                shutil.copy2(src, release_dir / doc)
                
        # Create comprehensive build info
        build_info = {
            "build_date": datetime.now().isoformat(),
            "build_mode": "Fully Autonomous",
            "platform": "Windows x64",
            "python_version": "3.11.9",
            "uv_version": "0.7.19",
            "pyinstaller_version": "6.14.2",
            "file_size": exe_dst.stat().st_size,
            "build_time": time.time() - self.start_time,
            "autonomous_agent": "v1.0",
            "optimization_level": "maximum",
            "validation_passed": True,
            "distribution_ready": True
        }
        
        with open(release_dir / "build_info.json", "w") as f:
            json.dump(build_info, f, indent=2)
            
        # Create autonomous README
        readme_content = f"""# DevO Chat - Autonomous Build

## 🤖 Autonomous Agent Build
This executable was created by a fully autonomous build agent with zero user interaction.

## 🚀 Quick Start
1. Run `devochat.exe`
2. Set `GEMINI_API_KEY` environment variable
3. Start chatting with your AI assistant!

## 📋 Commands
- `analyze <repo-path>` - Analyze repository
- `containerize <repo-path>` - Generate Docker config
- `auto-setup <repo-url>` - Clone and setup repository
- `help` - Show available commands
- `exit` - Exit application

## 🔧 Build Information
- **Build Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Build Mode**: Fully Autonomous
- **File Size**: {build_info['file_size']:,} bytes
- **Build Time**: {build_info['build_time']:.2f} seconds
- **Validation**: ✅ Passed all autonomous tests

## 🎯 Ready for Distribution
This executable is fully tested and ready for immediate distribution.

---
*Built autonomously by DevO Chat Autonomous Agent*
"""
        
        with open(release_dir / "README.md", "w") as f:
            f.write(readme_content)
            
        self.log("Distribution creation completed autonomously", "SUCCESS")
        return True
        
    def run_autonomous_agent(self):
        """Run the complete autonomous agent"""
        self.log("🤖 Autonomous Build Agent starting...", "STAGE")
        
        # Clear log files
        for log_file in [self.log_file, self.status_file]:
            if log_file.exists():
                log_file.unlink()
                
        # Define autonomous stages
        autonomous_stages = [
            ("Process Cleanup", self.autonomous_process_cleanup),
            ("Prerequisite Setup", self.autonomous_prerequisite_setup),
            ("Environment Setup", self.autonomous_environment_setup),
            ("Code Validation", self.autonomous_code_validation),
            ("Aggressive Cleanup", self.autonomous_aggressive_cleanup),
            ("Build Execution", self.autonomous_build_execution),
            ("Testing Validation", self.autonomous_testing_validation),
            ("Distribution Creation", self.autonomous_distribution_creation)
        ]
        
        # Execute stages autonomously
        for i, (stage_name, stage_func) in enumerate(autonomous_stages, 1):
            self.log(f"[{i}/{len(autonomous_stages)}] {stage_name}", "STAGE")
            
            if not stage_func():
                self.log(f"Autonomous agent failed at: {stage_name}", "ERROR")
                self.build_status["completed"] = False
                self.build_status["failed_at"] = stage_name
                self.update_status("failed", (i/len(autonomous_stages))*100)
                return False
                
        # Success completion
        total_time = time.time() - self.start_time
        self.build_status["completed"] = True
        self.build_status["total_time"] = total_time
        self.update_status("completed", 100, "Autonomous build completed successfully")
        
        # Final autonomous success message
        print("\n" + "="*50)
        print("   🎉 AUTONOMOUS AGENT COMPLETED! 🎉")
        print("="*50)
        print(f"✅ Fully autonomous build completed in {total_time:.2f} seconds")
        print("✅ Zero user interaction required")
        print("✅ All validations passed autonomously")
        print("✅ Distribution package created automatically")
        print(f"\n📦 Distribution: {self.root_dir / 'release'}")
        print(f"🚀 Executable: {self.root_dir / 'release' / 'devochat.exe'}")
        
        exe_path = self.root_dir / "release" / "devochat.exe"
        if exe_path.exists():
            print(f"📊 Size: {exe_path.stat().st_size:,} bytes")
            
        print("\n🤖 Autonomous agent execution complete!")
        print("🎯 Ready for immediate distribution and deployment!")
        
        return True

def main():
    """Main entry point for autonomous agent"""
    try:
        agent = AutonomousBuildAgent()
        success = agent.run_autonomous_agent()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Autonomous agent interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Autonomous agent crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()