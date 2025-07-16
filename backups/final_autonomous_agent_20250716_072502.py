"""
DevO Chat - Final Autonomous Agent
Ultimate automation without external dependencies
"""

import os
import sys
import subprocess
import shutil
import time
import json
import threading
from pathlib import Path
from datetime import datetime

class FinalAutonomousAgent:
    """Final autonomous agent - no external dependencies"""
    
    def __init__(self):
        self.root_dir = Path.cwd()
        self.start_time = time.time()
        self.log_file = self.root_dir / "final_autonomous.log"
        
    def log(self, message, level="INFO"):
        """Simple logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        emoji_map = {
            "SUCCESS": "✅",
            "ERROR": "❌", 
            "WARNING": "⚠️",
            "INFO": "🔄",
            "STAGE": "🎯"
        }
        
        emoji = emoji_map.get(level, "ℹ️")
        print(f"{emoji} {message}")
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {level}: {message}\n")
            
    def run_cmd(self, command, timeout=300):
        """Run command with timeout"""
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
            return False, "", "Timeout"
        except Exception as e:
            return False, "", str(e)
            
    def stage_cleanup(self):
        """Stage 1: Cleanup"""
        self.log("Stage 1: Process and file cleanup", "STAGE")
        
        # Kill processes
        cleanup_commands = [
            "taskkill /F /IM devochat.exe",
            "taskkill /F /IM python.exe"
        ]
        
        for cmd in cleanup_commands:
            self.run_cmd(cmd, 10)
            
        time.sleep(2)
        
        # Remove directories
        for dir_name in ["build", "dist", "release"]:
            dir_path = self.root_dir / dir_name
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                except:
                    pass
                    
        # Remove files
        for pattern in ["*.spec", "*.log"]:
            for file_path in self.root_dir.glob(pattern):
                try:
                    file_path.unlink()
                except:
                    pass
                    
        self.log("Cleanup completed", "SUCCESS")
        return True
        
    def stage_prerequisites(self):
        """Stage 2: Prerequisites"""
        self.log("Stage 2: Prerequisites validation", "STAGE")
        
        # Check UV
        success, _, _ = self.run_cmd("uv --version", 10)
        if not success:
            self.log("Installing UV...", "WARNING")
            install_cmd = 'powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"'
            success, _, _ = self.run_cmd(install_cmd, 120)
            if not success:
                self.log("UV installation failed", "ERROR")
                return False
                
        self.log("Prerequisites validated", "SUCCESS")
        return True
        
    def stage_environment(self):
        """Stage 3: Environment setup"""
        self.log("Stage 3: Environment setup", "STAGE")
        
        success, _, stderr = self.run_cmd("uv sync --extra build", 180)
        if not success:
            self.log(f"Environment setup failed: {stderr}", "ERROR")
            return False
            
        self.log("Environment setup completed", "SUCCESS")
        return True
        
    def stage_validation(self):
        """Stage 4: Code validation"""
        self.log("Stage 4: Code validation", "STAGE")
        
        modules = ["chat", "auto_setup", "utils", "templates", "repocontainerizer"]
        
        for module in modules:
            success, _, _ = self.run_cmd(f'uv run python -c "import {module}"', 30)
            if not success:
                self.log(f"Module {module} failed validation", "ERROR")
                return False
                
        self.log("Code validation completed", "SUCCESS")
        return True
        
    def stage_build(self):
        """Stage 5: Build executable"""
        self.log("Stage 5: Building executable", "STAGE")
        
        build_cmd = [
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
            "--clean",
            "--noconfirm",
            "chat.py"
        ]
        
        success, _, stderr = self.run_cmd(" ".join(build_cmd), 600)
        if not success:
            self.log(f"Build failed: {stderr}", "ERROR")
            return False
            
        self.log("Build completed", "SUCCESS")
        return True
        
    def stage_testing(self):
        """Stage 6: Test executable"""
        self.log("Stage 6: Testing executable", "STAGE")
        
        exe_path = self.root_dir / "dist" / "devochat.exe"
        if not exe_path.exists():
            self.log("Executable not found", "ERROR")
            return False
            
        time.sleep(2)
        
        success, _, _ = self.run_cmd(f'"{exe_path}" --help', 30)
        if not success:
            self.log("Executable test failed", "ERROR")
            return False
            
        self.log("Testing completed", "SUCCESS")
        return True
        
    def stage_packaging(self):
        """Stage 7: Create distribution package"""
        self.log("Stage 7: Creating distribution package", "STAGE")
        
        # Create release directory
        release_dir = self.root_dir / "release"
        release_dir.mkdir(exist_ok=True)
        
        # Copy executable
        exe_src = self.root_dir / "dist" / "devochat.exe"
        exe_dst = release_dir / "devochat.exe"
        shutil.copy2(exe_src, exe_dst)
        
        # Copy documentation
        docs = ["STANDALONE_EXECUTABLE_GUIDE.md", "sample-config.yml", "launch_devochat.bat"]
        for doc in docs:
            src = self.root_dir / doc
            if src.exists():
                shutil.copy2(src, release_dir / doc)
                
        # Create build info
        build_info = {
            "build_date": datetime.now().isoformat(),
            "build_mode": "Final Autonomous Agent",
            "file_size": exe_dst.stat().st_size,
            "build_time": time.time() - self.start_time
        }
        
        with open(release_dir / "build_info.json", "w") as f:
            json.dump(build_info, f, indent=2)
            
        # Create README
        readme = f"""# DevO Chat - Final Autonomous Build

## Quick Start
1. Run devochat.exe
2. Set GEMINI_API_KEY environment variable
3. Start chatting!

## Build Info
- Built: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Size: {build_info['file_size']:,} bytes
- Mode: Final Autonomous Agent

## Commands
- analyze <repo> - Analyze repository
- containerize <repo> - Generate Docker config
- auto-setup <url> - Clone and setup repository
- help - Show commands
- exit - Exit

Ready to use!
"""
        
        with open(release_dir / "README.md", "w") as f:
            f.write(readme)
            
        self.log("Distribution package created", "SUCCESS")
        return True
        
    def run_final_autonomous_agent(self):
        """Run the final autonomous agent"""
        self.log("🤖 Final Autonomous Agent starting...", "STAGE")
        
        # Clear log
        if self.log_file.exists():
            self.log_file.unlink()
            
        stages = [
            ("Cleanup", self.stage_cleanup),
            ("Prerequisites", self.stage_prerequisites),
            ("Environment", self.stage_environment),
            ("Validation", self.stage_validation),
            ("Build", self.stage_build),
            ("Testing", self.stage_testing),
            ("Packaging", self.stage_packaging)
        ]
        
        print("\n" + "="*50)
        print("   🤖 FINAL AUTONOMOUS AGENT")
        print("="*50)
        print("🔄 Running fully autonomous build...")
        print("📦 Zero user interaction required")
        print("")
        
        for i, (stage_name, stage_func) in enumerate(stages, 1):
            print(f"[{i}/{len(stages)}] {stage_name}...")
            
            if not stage_func():
                print(f"\n❌ Failed at stage: {stage_name}")
                return False
                
        total_time = time.time() - self.start_time
        
        print("\n" + "="*50)
        print("   🎉 AUTONOMOUS BUILD COMPLETED!")
        print("="*50)
        print(f"✅ Completed in {total_time:.2f} seconds")
        print("✅ Zero user interaction")
        print("✅ Ready for distribution")
        print("")
        print(f"📦 Package: {self.root_dir / 'release'}")
        print(f"🚀 Executable: {self.root_dir / 'release' / 'devochat.exe'}")
        
        exe_path = self.root_dir / "release" / "devochat.exe"
        if exe_path.exists():
            print(f"📊 Size: {exe_path.stat().st_size:,} bytes")
            
        print("\n🎯 Your autonomous agent is complete!")
        return True

def main():
    """Main entry point"""
    try:
        agent = FinalAutonomousAgent()
        success = agent.run_final_autonomous_agent()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Autonomous agent error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
