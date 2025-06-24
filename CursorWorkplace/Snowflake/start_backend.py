#!/usr/bin/env python3
"""
Start script for the Amazon Keyword Performance AI Chatbot backend server.
"""

import sys
import os
import subprocess
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'), 
        ('anthropic', 'anthropic'),
        ('snowflake-connector-python', 'snowflake.connector'),
        ('pandas', 'pandas'),
        ('python-dotenv', 'dotenv')
    ]
    
    missing_packages = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please copy env_example.txt to .env and configure your credentials:")
        print("cp env_example.txt .env")
        return False
    return True

def start_server():
    """Start the FastAPI server"""
    try:
        print("🚀 Starting Amazon Keyword Performance AI Chatbot Backend...")
        print("=" * 60)
        
        # Check dependencies
        if not check_dependencies():
            return False
        
        # Check environment file
        if not check_env_file():
            return False
        
        # Check if api directory exists
        api_dir = os.path.join(os.path.dirname(__file__), 'api')
        if not os.path.exists(api_dir):
            print(f"❌ API directory not found: {api_dir}")
            return False
        
        # Start the server from root directory using -m flag
        print("✅ Dependencies and configuration verified")
        print("🌐 Starting server on http://localhost:8000")
        print("📚 API documentation will be available at http://localhost:8000/docs")
        print("=" * 60)
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Run the server using -m flag from root directory
        subprocess.run([sys.executable, "-m", "api.main"])
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_server() 