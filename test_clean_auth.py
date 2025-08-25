#!/usr/bin/env python3
"""
Authentication Test Script
Demonstrates the new standard authentication system:
1. Direct API key authentication
2. Dual key authentication
3. API key → JWT token flow
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "your_api_key_here"  # Replace with actual API key
PUBLIC_KEY = "your_public_key_here"  # Replace with actual public key
PRIVATE_KEY = "your_private_key_here"  # Replace with actual private key

def test_direct_api_key_auth():
    """Test direct API key authentication"""
    print("🔑 Testing Direct API Key Authentication")
    print("=" * 50)
    
    headers = {
        "X-API-Key": API_KEY
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/routers/",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Direct API key authentication successful")
            print(f"Found {len(result)} routers")
            if result:
                print("Router names:")
                for router in result:
                    print(f"  - {router['name']} ({router['host']})")
        else:
            error = response.json()
            print("❌ FAILED: Direct API key authentication failed")
            print(f"Error: {error.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")

def test_dual_key_auth():
    """Test dual key authentication"""
    print("\n🔐 Testing Dual Key Authentication")
    print("=" * 50)
    
    headers = {
        "X-API-Key": PUBLIC_KEY,
        "X-Private-Key": PRIVATE_KEY
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/routers/",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Dual key authentication successful")
            print(f"Found {len(result)} routers")
            if result:
                print("Router names:")
                for router in result:
                    print(f"  - {router['name']} ({router['host']})")
        else:
            error = response.json()
            print("❌ FAILED: Dual key authentication failed")
            print(f"Error: {error.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")

def test_api_key_to_jwt_flow():
    """Test API key → JWT token flow"""
    print("\n🔄 Testing API Key → JWT Token Flow")
    print("=" * 50)
    
    # Step 1: Login with API keys to get JWT
    data = {
        "public_key": PUBLIC_KEY,
        "private_key": PRIVATE_KEY
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/users/api-key-login/",
            json=data
        )
        
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: API key login successful")
            jwt_token = result['access_token']
            print(f"JWT Token: {jwt_token[:50]}...")
            
            # Step 2: Use JWT token for router operations
            headers = {
                "Authorization": f"Bearer {jwt_token}"
            }
            
            response = requests.get(
                f"{BASE_URL}/routers/",
                headers=headers
            )
            
            print(f"Router Access Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS: JWT token router access successful")
                print(f"Found {len(result)} routers")
            else:
                error = response.json()
                print("❌ FAILED: JWT token router access failed")
                print(f"Error: {error.get('error', 'Unknown error')}")
                
        else:
            error = response.json()
            print("❌ FAILED: API key login failed")
            print(f"Error: {error['error']}")
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")

def test_command_execution_with_api_key():
    """Test command execution using direct API key authentication"""
    print("\n⚡ Testing Command Execution with API Key")
    print("=" * 50)
    
    headers = {
        "X-API-Key": API_KEY,
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

def test_invalid_authentication():
    """Test that invalid authentication is properly rejected"""
    print("\n🚫 Testing Invalid Authentication Rejection")
    print("=" * 50)
    
    # Test invalid API key
    headers = {
        "X-API-Key": "invalid_key_here"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/routers/",
            headers=headers
        )
        
        print(f"Invalid API Key Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ SUCCESS: Invalid API key properly rejected")
        else:
            print("❌ FAILED: Invalid API key should have been rejected")
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")
    
    # Test missing authentication
    try:
        response = requests.get(f"{BASE_URL}/routers/")
        
        print(f"No Auth Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ SUCCESS: Missing authentication properly rejected")
        else:
            print("❌ FAILED: Missing authentication should have been rejected")
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")

def main():
    """Main test function"""
    print("🚀 Clean Authentication System Test")
    print("=" * 60)
    
    # Check if credentials are set
    if (API_KEY == "your_api_key_here" or 
        PUBLIC_KEY == "your_public_key_here" or 
        PRIVATE_KEY == "your_private_key_here"):
        print("❌ Please set valid credentials in the script")
        print("You can get these from your user account or by calling /users/generate-api-key/")
        return
    
    try:
        # Test all authentication methods
        test_direct_api_key_auth()
        test_dual_key_auth()
        test_api_key_to_jwt_flow()
        test_command_execution_with_api_key()
        test_invalid_authentication()
        
        print("\n" + "=" * 60)
        print("✅ All authentication tests completed!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")

if __name__ == "__main__":
    main()
