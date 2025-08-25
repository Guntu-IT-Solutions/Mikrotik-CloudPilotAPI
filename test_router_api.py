#!/usr/bin/env python3
"""
Test script for the Mikrotik Router API
This script demonstrates how to use the Router API endpoints
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"

# Choose your authentication method:

# Method 1: JWT Token (recommended for authenticated users)
JWT_TOKEN = "your_jwt_token_here"  # Replace with your actual JWT token

# Method 2: Dual API Keys (for unauthenticated access)
PUBLIC_API_KEY = "your_public_api_key_here"  # Replace with your actual public API key
PRIVATE_API_KEY = "your_private_api_key_here"  # Replace with your actual private API key

def test_router_api():
    """Test the Router API endpoints"""
    
    # Choose authentication method
    if JWT_TOKEN != "your_jwt_token_here":
        # Use JWT authentication
        headers = {
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json"
        }
        print("🔐 Using JWT Token authentication")
    else:
        # Use dual API key authentication
        headers = {
            "X-API-Key": PUBLIC_API_KEY,
            "X-Private-Key": PRIVATE_API_KEY,
            "Content-Type": "application/json"
        }
        print("🔑 Using Dual API Key authentication")
    
    print("🚀 Testing Mikrotik Router API")
    print("=" * 50)
    
    # Test 1: List routers
    print("\n1. Listing routers...")
    try:
        response = requests.get(f"{BASE_URL}/routers/", headers=headers)
        if response.status_code == 200:
            routers = response.json()
            print(f"✅ Found {len(routers)} routers")
            for router in routers:
                print(f"   - {router['name']} ({router['host']}) - Status: {'🟢 Online' if router['is_online'] else '🔴 Offline'}")
        else:
            print(f"❌ Failed to list routers: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error listing routers: {str(e)}")
    
    # Test 2: Create a test router
    print("\n2. Creating test router...")
    test_router_data = {
        "name": "Test Router",
        "host": "192.168.1.1",
        "port": 80,
        "username": "admin",
        "password": "test123",
        "use_https": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/routers/", 
                               headers=headers, 
                               json=test_router_data)
        if response.status_code == 201:
            router = response.json()
            router_id = router['id']
            print(f"✅ Created test router with ID: {router_id}")
        else:
            print(f"❌ Failed to create router: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating router: {str(e)}")
        return
    
    # Test 3: Test router connection
    print("\n3. Testing router connection...")
    try:
        response = requests.post(f"{BASE_URL}/routers/{router_id}/test-connection/", 
                               headers=headers)
        if response.status_code == 200:
            result = response.json()
            status_emoji = "🟢" if result['is_online'] else "🔴"
            print(f"{status_emoji} Connection test completed: {'Online' if result['is_online'] else 'Offline'}")
        else:
            print(f"❌ Failed to test connection: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing connection: {str(e)}")
    
    # Test 4: Execute a command
    print("\n4. Executing test command...")
    try:
        command_data = {
            "command": "system/resource"
        }
        response = requests.post(f"{BASE_URL}/routers/{router_id}/execute-command/", 
                               headers=headers, 
                               json=command_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Command executed successfully")
            print(f"   Result: {result.get('result', 'No result data')}")
        else:
            print(f"❌ Failed to execute command: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error executing command: {str(e)}")
    
    # Test 5: Get device info
    print("\n5. Getting device information...")
    try:
        response = requests.get(f"{BASE_URL}/routers/{router_id}/device-info/", 
                              headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Device info retrieved successfully")
            device_info = result.get('device_info', {})
            if 'identity' in device_info:
                print(f"   Device: {device_info['identity']}")
            if 'version' in device_info:
                print(f"   Version: {device_info['version']}")
        else:
            print(f"❌ Failed to get device info: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting device info: {str(e)}")
    
    # Test 6: Update router
    print("\n6. Updating router...")
    try:
        update_data = {
            "name": "Updated Test Router",
            "port": 8080
        }
        response = requests.put(f"{BASE_URL}/routers/{router_id}/", 
                              headers=headers, 
                              json=update_data)
        if response.status_code == 200:
            router = response.json()
            print(f"✅ Router updated successfully")
            print(f"   New name: {router['name']}")
            print(f"   New port: {router['port']}")
        else:
            print(f"❌ Failed to update router: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error updating router: {str(e)}")
    
    # Test 7: Get specific router
    print("\n7. Getting specific router...")
    try:
        response = requests.get(f"{BASE_URL}/routers/{router_id}/", headers=headers)
        if response.status_code == 200:
            router = response.json()
            print(f"✅ Retrieved router: {router['name']} ({router['host']}:{router['port']})")
        else:
            print(f"❌ Failed to get router: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting router: {str(e)}")
    
    # Test 8: Delete router
    print("\n8. Deleting test router...")
    try:
        response = requests.delete(f"{BASE_URL}/routers/{router_id}/", headers=headers)
        if response.status_code == 204:
            print(f"✅ Router deleted successfully")
        else:
            print(f"❌ Failed to delete router: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error deleting router: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")

if __name__ == "__main__":
    test_router_api()
