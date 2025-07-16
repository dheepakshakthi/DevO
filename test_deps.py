#!/usr/bin/env python3
"""Simple test to check if dependencies are available"""

import sys

try:
    import click
    print("✅ Click imported successfully")
except ImportError as e:
    print(f"❌ Click import failed: {e}")

try:
    import rich
    print("✅ Rich imported successfully")
except ImportError as e:
    print(f"❌ Rich import failed: {e}")

try:
    import yaml
    print("✅ PyYAML imported successfully")
except ImportError as e:
    print(f"❌ PyYAML import failed: {e}")

try:
    import google.genai as genai
    print("✅ Google Genai imported successfully")
except ImportError as e:
    print(f"❌ Google Genai import failed: {e}")

print("Python executable:", sys.executable)
print("Python version:", sys.version)
