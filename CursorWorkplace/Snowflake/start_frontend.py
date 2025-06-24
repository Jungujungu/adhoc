#!/usr/bin/env python3
"""
Start script for the Amazon Keyword Performance AI Chatbot frontend.
"""

import sys
import os
import subprocess
import time
import requests

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit',
        'requests',
        'pandas',
        'plotly'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def check_backend():
    """Check if backend server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass
    
    print("⚠️  Backend server is not running!")
    print("Please start the backend server first:")
    print("python start_backend.py")
    print("\nOr manually:")
    print("cd api && python main.py")
    return False

def start_frontend():
    """Start the Streamlit frontend"""
    try:
        print("🚀 Starting Amazon Keyword Performance AI Chatbot Frontend...")
        print("=" * 60)
        
        # Check dependencies
        if not check_dependencies():
            return False
        
        # Check backend
        if not check_backend():
            return False
        
        # Change to frontend directory
        frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
        if not os.path.exists(frontend_dir):
            print(f"❌ Frontend directory not found: {frontend_dir}")
            return False
        
        os.chdir(frontend_dir)
        
        # Start the frontend
        print("✅ Dependencies and backend verified")
        print("🌐 Starting Streamlit app on http://localhost:8501")
        print("=" * 60)
        print("Press Ctrl+C to stop the app")
        print("=" * 60)
        
        # Run Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped by user")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_frontend() 