#!/usr/bin/env python3
"""
Test script to verify the Amazon Keyword Performance AI Chatbot installation.
This script tests all components to ensure they're working correctly.
"""

import sys
import os
import importlib

def test_import(module_name, description):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {description} - OK")
        return True
    except ImportError as e:
        print(f"❌ {description} - FAILED: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n🔧 Testing Configuration...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            'SNOWFLAKE_ACCOUNT',
            'SNOWFLAKE_USER', 
            'SNOWFLAKE_PASSWORD',
            'SNOWFLAKE_DATABASE',
            'ANTHROPIC_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
            print("   Please edit your .env file with the correct values")
            return False
        else:
            print("✅ Configuration - All environment variables found")
            return True
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_snowflake_connection():
    """Test Snowflake connection"""
    print("\n❄️  Testing Snowflake Connection...")
    
    try:
        import snowflake.connector
        from config import Config
        
        # Test connection
        conn = snowflake.connector.connect(
            account=Config.SNOWFLAKE_ACCOUNT,
            user=Config.SNOWFLAKE_USER,
            password=Config.SNOWFLAKE_PASSWORD,
            warehouse=Config.SNOWFLAKE_WAREHOUSE,
            database=Config.SNOWFLAKE_DATABASE,
            schema=Config.SNOWFLAKE_SCHEMA
        )
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ Snowflake Connection - OK (Version: {version})")
        return True
        
    except Exception as e:
        print(f"❌ Snowflake Connection - FAILED: {e}")
        return False

def test_claude_api():
    """Test Claude API connection"""
    print("\n🤖 Testing Claude API...")
    
    try:
        import anthropic
        from config import Config
        
        # Test API call
        client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=Config.CLAUDE_MODEL,
            max_tokens=50,
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        print("✅ Claude API - OK")
        return True
        
    except Exception as e:
        print(f"❌ Claude API - FAILED: {e}")
        return False

def test_data_processing():
    """Test data processing libraries"""
    print("\n📊 Testing Data Processing...")
    
    try:
        import pandas as pd
        import numpy as np
        
        # Test basic operations
        df = pd.DataFrame({'test': [1, 2, 3]})
        result = df['test'].sum()
        
        if result == 6:
            print("✅ Data Processing - OK")
            return True
        else:
            print("❌ Data Processing - FAILED: Basic operations not working")
            return False
            
    except Exception as e:
        print(f"❌ Data Processing - FAILED: {e}")
        return False

def test_web_framework():
    """Test web framework"""
    print("\n🌐 Testing Web Framework...")
    
    try:
        import fastapi
        import uvicorn
        
        print("✅ Web Framework - OK")
        return True
        
    except Exception as e:
        print(f"❌ Web Framework - FAILED: {e}")
        return False

def test_frontend():
    """Test frontend libraries"""
    print("\n🎨 Testing Frontend...")
    
    try:
        import streamlit
        import plotly.express as px
        
        print("✅ Frontend - OK")
        return True
        
    except Exception as e:
        print(f"❌ Frontend - FAILED: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Amazon Keyword Performance AI Chatbot - Installation Test")
    print("=" * 60)
    
    # Test basic imports
    print("\n📦 Testing Package Imports...")
    
    imports = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("anthropic", "Anthropic"),
        ("snowflake.connector", "Snowflake Connector"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("streamlit", "Streamlit"),
        ("plotly", "Plotly"),
        ("python-dotenv", "Python-dotenv"),
        ("requests", "Requests")
    ]
    
    import_results = []
    for module, description in imports:
        result = test_import(module, description)
        import_results.append(result)
    
    # Test configuration
    config_ok = test_configuration()
    
    # Test connections (only if config is OK)
    snowflake_ok = False
    claude_ok = False
    
    if config_ok:
        snowflake_ok = test_snowflake_connection()
        claude_ok = test_claude_api()
    else:
        print("\n⚠️  Skipping connection tests due to configuration issues")
    
    # Test other components
    data_ok = test_data_processing()
    web_ok = test_web_framework()
    frontend_ok = test_frontend()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    
    all_imports_ok = all(import_results)
    print(f"   Package Imports: {'✅ PASS' if all_imports_ok else '❌ FAIL'}")
    print(f"   Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"   Snowflake Connection: {'✅ PASS' if snowflake_ok else '❌ FAIL'}")
    print(f"   Claude API: {'✅ PASS' if claude_ok else '❌ FAIL'}")
    print(f"   Data Processing: {'✅ PASS' if data_ok else '❌ FAIL'}")
    print(f"   Web Framework: {'✅ PASS' if web_ok else '❌ FAIL'}")
    print(f"   Frontend: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    
    overall_success = all_imports_ok and config_ok and snowflake_ok and claude_ok and data_ok and web_ok and frontend_ok
    
    print("\n" + "=" * 60)
    if overall_success:
        print("🎉 All tests passed! Your installation is ready.")
        print("\n🚀 You can now run the application:")
        print("   1. python start_backend.py")
        print("   2. python start_frontend.py")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print("\n🔧 Common solutions:")
        print("   - Run: python install_dependencies.py")
        print("   - Check your .env file configuration")
        print("   - Verify your Snowflake and Claude API credentials")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 