#!/usr/bin/env python3
"""
Installation script for Amazon Keyword Performance AI Chatbot dependencies.
This script handles the installation of required packages with better error handling.
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command with error handling"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print("✅ Python version is compatible")
    return True

def upgrade_pip():
    """Upgrade pip to latest version"""
    return run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    )

def install_package(package, description=None):
    """Install a single package"""
    if description is None:
        description = f"Installing {package}"
    
    # Try different installation methods
    commands = [
        f"{sys.executable} -m pip install {package}",
        f"{sys.executable} -m pip install {package} --user",
        f"{sys.executable} -m pip install {package} --no-cache-dir"
    ]
    
    for i, command in enumerate(commands):
        if run_command(command, f"{description} (attempt {i+1})"):
            return True
    
    return False

def install_dependencies():
    """Install all required dependencies"""
    print("🚀 Installing Amazon Keyword Performance AI Chatbot Dependencies")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Upgrade pip
    upgrade_pip()
    
    # Core packages that should work on Windows
    core_packages = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("python-dotenv", "Environment variables"),
        ("requests", "HTTP library"),
        ("python-multipart", "File upload support")
    ]
    
    # AI and data processing packages
    ai_packages = [
        ("anthropic", "Claude AI API"),
        ("pandas", "Data manipulation"),
        ("numpy", "Numerical computing")
    ]
    
    # Database package
    db_packages = [
        ("snowflake-connector-python", "Snowflake database connector")
    ]
    
    # Frontend and visualization packages
    frontend_packages = [
        ("streamlit", "Web application framework"),
        ("plotly", "Interactive visualizations")
    ]
    
    all_packages = core_packages + ai_packages + db_packages + frontend_packages
    
    print("\n📦 Installing packages...")
    failed_packages = []
    
    for package, description in all_packages:
        if not install_package(package, description):
            failed_packages.append(package)
    
    # Report results
    print("\n" + "=" * 60)
    if not failed_packages:
        print("🎉 All packages installed successfully!")
        print("\n✅ You can now run the application:")
        print("   1. python start_backend.py")
        print("   2. python start_frontend.py")
        return True
    else:
        print(f"⚠️  Some packages failed to install: {', '.join(failed_packages)}")
        print("\n🔧 Alternative installation methods:")
        print("   1. Try using conda: conda install -c conda-forge <package_name>")
        print("   2. Download pre-compiled wheels from: https://www.lfd.uci.edu/~gohlke/pythonlibs/")
        print("   3. Install Visual Studio Build Tools for Windows")
        return False

def create_env_file():
    """Create .env file from template"""
    if not os.path.exists('.env') and os.path.exists('env_example.txt'):
        print("\n📝 Creating .env file from template...")
        try:
            with open('env_example.txt', 'r') as f:
                content = f.read()
            
            with open('.env', 'w') as f:
                f.write(content)
            
            print("✅ .env file created successfully!")
            print("⚠️  Please edit .env file with your actual credentials")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    return True

def main():
    """Main installation function"""
    print("Amazon Keyword Performance AI Chatbot - Dependency Installer")
    print("=" * 60)
    
    # Install dependencies
    success = install_dependencies()
    
    # Create .env file
    create_env_file()
    
    if success:
        print("\n🎯 Installation Summary:")
        print("✅ Dependencies installed")
        print("✅ Environment file created")
        print("\n🚀 Next steps:")
        print("   1. Edit .env file with your credentials")
        print("   2. Run: python start_backend.py")
        print("   3. Run: python start_frontend.py")
    else:
        print("\n❌ Installation completed with errors")
        print("Please check the error messages above and try alternative installation methods")

if __name__ == "__main__":
    main() 