#!/usr/bin/env python3
"""
Example usage of RepoContainerizer
"""

import os
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Example usage of RepoContainerizer"""
    
    # Set the API key (replace with your actual API key)
    api_key = "AIzaSyAwxg1aGIsvBSb17SAE-lFTz_Bh-lIDvrI"
    
    print("🚀 RepoContainerizer Example")
    print("=" * 50)
    
    try:
        from repo_containerizer import RepoContainerizer
        
        # Initialize the containerizer
        containerizer = RepoContainerizer(api_key)
        
        # Example repository URL (you can change this)
        repo_url = "https://github.com/pallets/flask"
        
        print(f"📦 Analyzing repository: {repo_url}")
        
        # Step 1: Clone repository
        repo_path = containerizer.clone_repository(repo_url)
        
        # Step 2: Analyze repository structure
        print("📊 Analyzing repository structure...")
        structure = containerizer.analyze_repository_structure(repo_path)
        
        # Step 3: Read important files
        print("📖 Reading important files...")
        file_contents = containerizer.read_important_files(repo_path, structure)
        
        # Step 4: Analyze with LLM
        print("🤖 Analyzing with AI...")
        analysis = containerizer.analyze_with_llm(repo_url, structure, file_contents)
        
        # Step 5: Generate output files
        print("📝 Generating containerization files...")
        output_dir = "./example_output"
        output_files = containerizer.create_output_files(analysis, output_dir)
        
        # Display results
        print("\n" + "=" * 50)
        print("✅ Containerization Complete!")
        print("=" * 50)
        
        print(f"📊 Analysis Results:")
        print(f"   Primary Language: {analysis.primary_language}")
        print(f"   Framework: {analysis.framework}")
        print(f"   Package Manager: {analysis.package_manager}")
        print(f"   Database: {analysis.database}")
        print(f"   Port: {analysis.port}")
        
        print(f"\n📄 Generated Files:")
        for file_path in output_files:
            print(f"   {file_path}")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Navigate to output directory: cd {output_dir}")
        print(f"   2. Build the container: docker build -t my-app .")
        print(f"   3. Run the container: docker run -p {analysis.port}:8080 my-app")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure you have set the GEMINI_API_KEY environment variable")
        print("2. Check that all dependencies are installed: pip install -r requirements.txt")
        print("3. Ensure you have an internet connection for repository cloning")
        
    finally:
        # Clean up
        if 'containerizer' in locals():
            containerizer.cleanup()

if __name__ == "__main__":
    main()
