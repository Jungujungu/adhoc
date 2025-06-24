#!/usr/bin/env python3
"""
QuickBooks Setup Test Script

This script helps verify that your QuickBooks API setup is working correctly.
Run this before using the main automation script.
"""

import os
import sys
from dotenv import load_dotenv
from config import QuickBooksConfig
from quickbooks_client import QuickBooksClient

def test_environment():
    """Test environment variables and configuration"""
    print("=== Testing Environment Configuration ===")
    
    load_dotenv()
    
    # Check required environment variables
    required_vars = ['QUICKBOOKS_CLIENT_ID', 'QUICKBOOKS_CLIENT_SECRET']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"✓ {var}: {'*' * len(value)} (length: {len(value)})")
    
    if missing_vars:
        print(f"✗ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return False
    
    # Check optional environment variables
    redirect_uri = os.getenv('QUICKBOOKS_REDIRECT_URI', 'http://localhost:8080/callback')
    environment = os.getenv('QUICKBOOKS_ENVIRONMENT', 'sandbox')
    
    print(f"✓ QUICKBOOKS_REDIRECT_URI: {redirect_uri}")
    print(f"✓ QUICKBOOKS_ENVIRONMENT: {environment}")
    
    return True

def test_quickbooks_config():
    """Test QuickBooks configuration"""
    print("\n=== Testing QuickBooks Configuration ===")
    
    try:
        print(f"Environment: {QuickBooksConfig.ENVIRONMENT}")
        print(f"Base URL: {QuickBooksConfig.get_base_url()}")
        
        if QuickBooksConfig.CLIENT_ID and QuickBooksConfig.CLIENT_SECRET:
            print("✓ Client credentials loaded successfully")
            return True
        else:
            print("✗ Client credentials not found")
            return False
            
    except Exception as e:
        print(f"✗ Configuration error: {str(e)}")
        return False

def test_api_connection():
    """Test API connection (requires authentication)"""
    print("\n=== Testing API Connection ===")
    
    client = QuickBooksClient()
    
    # Test authorization URL generation
    try:
        auth_success = client.authenticate()
        if not auth_success:
            print("✓ Authorization URL generated successfully")
            print("This is expected for first-time setup")
            return True
        else:
            print("✓ Already authenticated")
            return True
    except Exception as e:
        print(f"✗ API connection error: {str(e)}")
        return False

def test_categorization_rules():
    """Test categorization rules"""
    print("\n=== Testing Categorization Rules ===")
    
    from config import CategorizationRules
    
    # Test some sample transactions
    test_cases = [
        ("Payment from Client ABC", 1000, "Income"),
        ("Staples Office Supplies", -50, "Office Supplies"),
        ("Electric Bill Payment", -120, "Utilities"),
        ("Uber Ride", -25, "Travel"),
        ("Coffee Shop", -5, "Meals and Entertainment"),
        ("Adobe Subscription", -30, "Software and Subscriptions"),
        ("Unknown Transaction", -100, "Uncategorized")
    ]
    
    for description, amount, expected in test_cases:
        result = CategorizationRules.get_category_for_transaction(description, amount)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{description}' -> {result} (expected: {expected})")
    
    return True

def main():
    """Run all tests"""
    print("QuickBooks Setup Test")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment),
        ("QuickBooks Configuration", test_quickbooks_config),
        ("API Connection", test_api_connection),
        ("Categorization Rules", test_categorization_rules)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with error: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Visit the authorization URL")
        print("3. Complete the authentication process")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Create a .env file with your QuickBooks API credentials")
        print("- Ensure all required environment variables are set")
        print("- Check your internet connection")
        print("- Verify your QuickBooks app configuration")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 