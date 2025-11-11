#!/usr/bin/env python3
"""
AML Intelligence System - Startup Script
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    directories = ["temp_uploads", "logs", "static"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✓ Directories created")

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting AML Intelligence System...")
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        # Set PYTHONPATH to include src directory
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd())
        
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "src.api:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], env=env)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

def main():
    """Main startup function"""
    print("=" * 60)
    print("🛡️  AML Intelligence System")
    print("   Financial AI Hackathon Championship 2025")
    print("=" * 60)
    
    check_python_version()
    
    # Check if dependencies need to be installed
    try:
        import fastapi
        import uvicorn
        print("✓ Dependencies already installed")
    except ImportError:
        install_dependencies()
    
    create_directories()
    start_server()

if __name__ == "__main__":
    main()