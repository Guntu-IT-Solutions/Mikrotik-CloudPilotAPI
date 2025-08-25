#!/usr/bin/env python3
"""
Simple Authentication Test Script
Demonstrates the clean authentication system:
1. Login with API keys to get JWT token
2. Use JWT token for all operations
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
PUBLIC_KEY = "your_public_key_here"  # Replace with actual public key
PRIVATE_KEY = "your_private_key_here"  # Replace with actual private key

def test_api_key_login():
    """Test API key login to get JWT token"""
    print("🔑 Testing API Key Login")
    print("=" * 50)
    
    data = {
        "public_key": PUBLIC_KEY,
        "private_key": PRIVATE_KEY
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/users/api-key-login/",
            json=data
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: API key login successful")
            print(f"User ID: {result['user_id']}")
            print(f"Username: {result['username']}")
            print(f"Message: {result['message']}")
            print(f"Access Token: {result['access_token'][:50]}...")
            return result['access_token']
        else:
            error = response.json()
            print("❌ FAILED: API key login failed")
            print(f"Error: {error['error']}")
            return None
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")
        return None

def test_jwt_router_operations(jwt_token):
    """Test router operations using JWT token"""
    print("\n🌐 Testing JWT Router Operations")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }
    
    # Test getting routers
    try:
        response = requests.get(
            f"{BASE_URL}/routers/",
            headers=headers
        )
        
        print(f"Get Routers Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Router access successful")
            print(f"Found {len(result)} routers")
            if result:
                print("Router names:")
                for router in result:
                    print(f"  - {router['name']} ({router['host']})")
                return result[0]['id'] if result else None
        else:
            error = response.json()
            print("❌ FAILED: Router access failed")
            print(f"Error: {error.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")
        return None

def test_jwt_command_execution(jwt_token, router_id):
    """Test command execution using JWT token"""
    print("\n⚡ Testing JWT Command Execution")
    print("=" * 50)
    
    if not router_id:
        print("⚠️ No router ID available for testing")
        return
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    # Test system resource command
    data = {
        "command": "system/resource",
        "method": "GET"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/routers/{router_id}/execute-command/",
            headers=headers,
            json=data
        )
        
        print(f"Command Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Command execution successful")
            print(f"Result: {json.dumps(result['result'], indent=2)}")
        else:
            error = response.json()
            print("❌ FAILED: Command execution failed")
            print(f"Error: {error.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")

def test_jwt_user_operations(jwt_token):
    """Test user operations using JWT token"""
    print("\n👤 Testing JWT User Operations")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }
    
    # Test getting user profile
    try:
        response = requests.get(
            f"{BASE_URL}/users/profile/",
            headers=headers
        )
        
        print(f"Get Profile Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Profile access successful")
            print(f"Bio: {result.get('bio', 'Not set')}")
            print(f"Website: {result.get('website', 'Not set')}")
        else:
            error = response.json()
            print("❌ FAILED: Profile access failed")
            print(f"Error: {error.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")
    
    # Test getting API keys
    try:
        response = requests.get(
            f"{BASE_URL}/users/api-keys/",
            headers=headers
        )
        
        print(f"Get API Keys Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: API keys access successful")
            print(f"Public Key: {result.get('public_key', 'Not found')}")
        else:
            error = response.json()
            print("❌ FAILED: API keys access failed")
            print(f"Error: {error.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")

def test_invalid_jwt():
    """Test that invalid JWT tokens are rejected"""
    print("\n🚫 Testing Invalid JWT Rejection")
    print("=" * 50)
    
    headers = {
        "Authorization": "Bearer invalid_token_here"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/routers/",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ SUCCESS: Invalid JWT properly rejected")
        else:
            print("❌ FAILED: Invalid JWT should have been rejected")
            print(f"Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")

def main():
    """Main test function"""
    print("🚀 Simple Authentication System Test")
    print("=" * 60)
    
    # Check if API keys are set
    if PUBLIC_KEY == "your_public_key_here" or PRIVATE_KEY == "your_private_key_here":
        print("❌ Please set valid PUBLIC_KEY and PRIVATE_KEY in the script")
        print("You can get these from your user account or by calling /users/generate-api-key/")
        return
    
    try:
        # Step 1: Login with API keys
        jwt_token = test_api_key_login()
        
        if not jwt_token:
            print("\n❌ Cannot proceed without JWT token")
            return
        
        # Step 2: Test router operations with JWT
        router_id = test_jwt_router_operations(jwt_token)
        
        # Step 3: Test command execution with JWT
        test_jwt_command_execution(jwt_token, router_id)
        
        # Step 4: Test user operations with JWT
        test_jwt_user_operations(jwt_token)
        
        # Step 5: Test invalid JWT rejection
        test_invalid_jwt()
        
        print("\n" + "=" * 60)
        print("✅ All authentication tests completed!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")

if __name__ == "__main__":
    main()
