import requests
import json

def test_chat_api():
    # Test 1: Basic query
    url = "http://localhost:8000/chat"
    headers = {"Content-Type": "application/json"}
    
    print("=== Test 1: Basic Query ===")
    data = {"message": "Show me top 5 keywords by purchases"}
    
    try:
        print("Testing basic query...")
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Basic query successful!")
            print(f"Response length: {len(result.get('response', ''))} characters")
        else:
            print(f"❌ Basic query failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception in basic query: {e}")
    
    # Test 2: CTR query
    print("\n=== Test 2: CTR Query ===")
    data = {"message": "Show me keywords with highest CTR (click through rate)"}
    
    try:
        print("Testing CTR query...")
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ CTR query successful!")
            print(f"SQL generated: {result.get('sql_query', 'N/A')}")
            if result.get('data'):
                print(f"Data returned: {len(result['data'])} rows")
        else:
            print(f"❌ CTR query failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception in CTR query: {e}")

if __name__ == "__main__":
    test_chat_api() 