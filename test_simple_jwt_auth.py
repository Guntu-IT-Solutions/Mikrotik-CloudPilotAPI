#!/usr/bin/env python3
"""
Simple JWT Authentication Test Script
Demonstrates both login methods:
1. Username/password login
2. API key login (both public and private keys)
Both return JWT tokens for accessing protected endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "your_username_here"  # Replace with actual username
PASSWORD = "your_password_here"  # Replace with actual password
PUBLIC_KEY = "your_public_key_here"  # Replace with actual public key
PRIVATE_KEY = "your_private_key_here"  # Replace with actual private key

def test_username_password_login():
    """Test username/password login to get JWT token"""
    print("🔑 Testing Username/Password Login")
    print("=" * 50)
    
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/users/login/",
            json=data
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Username/password login successful")
            print(f"User ID: {result['user_id']}")
            print(f"Username: {result['username']}")
            print(f"Access Token: {result['access_token'][:50]}...")
            return result['access_token']
        else:
            error = response.json()
            print("❌ FAILED: Username/password login failed")
            print(f"Error: {error['error']}")
            return None
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")
        return None

def test_api_key_login():
    """Test API key login to get JWT token"""
    print("\n🔐 Testing API Key Login")
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

def test_jwt_router_access(jwt_token, method_name):
    """Test router access using JWT token"""
    print(f"\n🌐 Testing JWT Router Access ({method_name})")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/routers/",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Router access successful")
            print(f"Found {len(result)} routers")
            if result:
                print("Router names:")
                for router in result:
                    print(f"  - {router['name']} ({router['host']})")
        else:
            error = response.json()
            print("❌ FAILED: Router access failed")
            print(f"Error: {error.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")

def test_jwt_command_execution(jwt_token, method_name):
    """Test command execution using JWT token"""
    print(f"\n⚡ Testing JWT Command Execution ({method_name})")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    # First, get a router ID
    try:
        response = requests.get(
            f"{BASE_URL}/routers/",
            headers=headers
        )
        
        if response.status_code == 200:
            routers = response.json()
            if routers:
                router_id = routers[0]['id']
                print(f"Using router ID: {router_id}")
                
                # Test system resource command
                data = {
                    "command": "system/resource",
                    "method": "GET"
                }
                
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
            else:
                print("⚠️ No routers found to test with")
        else:
            print("❌ Failed to get routers for testing")
            
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
    print("🚀 Simple JWT Authentication Test")
    print("=" * 60)
    
    # Check if credentials are set
    if (USERNAME == "your_username_here" or PASSWORD == "your_password_here" or
        PUBLIC_KEY == "your_public_key_here" or PRIVATE_KEY == "your_private_key_here"):
        print("❌ Please set valid credentials in the script")
        print("You can get API keys from your user account or by calling /users/generate-api-key/")
        return
    
    try:
        # Test both login methods
        print("Testing both authentication methods...")
        
        # Method 1: Username/Password
        jwt_token_1 = test_username_password_login()
        if jwt_token_1:
            test_jwt_router_access(jwt_token_1, "Username/Password")
            test_jwt_command_execution(jwt_token_1, "Username/Password")
        
        # Method 2: API Keys
        jwt_token_2 = test_api_key_login()
        if jwt_token_2:
            test_jwt_router_access(jwt_token_2, "API Keys")
            test_jwt_command_execution(jwt_token_2, "API Keys")
        
        # Test invalid JWT rejection
        test_invalid_jwt()
        
        print("\n" + "=" * 60)
        print("✅ All authentication tests completed!")
        
        if jwt_token_1 and jwt_token_2:
            print("🎯 Both login methods work and return valid JWT tokens!")
        elif jwt_token_1 or jwt_token_2:
            print("⚠️ One login method works, check the other one")
        else:
            print("❌ No login methods working, check your credentials")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")

if __name__ == "__main__":
    main()
