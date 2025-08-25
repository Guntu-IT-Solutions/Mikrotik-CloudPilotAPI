#!/usr/bin/env python3
"""
Test script to verify error handling for invalid Mikrotik commands
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
JWT_TOKEN = "your_jwt_token_here"  # Replace with actual token
ROUTER_ID = 1  # Replace with actual router ID

def test_invalid_command():
    """Test sending an invalid command to verify error handling"""
    
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test with invalid command
    data = {
        "command": "invalid/command"
    }
    
    print("Testing invalid command...")
    print(f"Command: {data['command']}")
    print(f"URL: {BASE_URL}/routers/{ROUTER_ID}/execute-command/")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/routers/{ROUTER_ID}/execute-command/",
            headers=headers,
            json=data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 400:
            print("✅ SUCCESS: Got expected 400 status code")
            try:
                error_data = response.json()
                print(f"Error Response: {json.dumps(error_data, indent=2)}")
                
                # Verify error structure
                if 'error' in error_data and 'status_code' in error_data:
                    print("✅ SUCCESS: Error response has correct structure")
                else:
                    print("❌ FAIL: Error response missing required fields")
                    
            except json.JSONDecodeError:
                print("❌ FAIL: Response is not valid JSON")
                
        elif response.status_code == 200:
            print("❌ FAIL: Got 200 status code for invalid command")
            print(f"Response: {response.text}")
        else:
            print(f"❌ FAIL: Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ FAIL: Request failed: {e}")

def test_valid_command():
    """Test sending a valid command to verify success handling"""
    
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test with valid command
    data = {
        "command": "system/resource"
    }
    
    print("\n" + "="*50)
    print("Testing valid command...")
    print(f"Command: {data['command']}")
    print(f"URL: {BASE_URL}/routers/{ROUTER_ID}/execute-command/")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/routers/{ROUTER_ID}/execute-command/",
            headers=headers,
            json=data
        )
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            print("✅ SUCCESS: Got expected 200 status code")
            try:
                result_data = response.json()
                print(f"Success Response: {json.dumps(result_data, indent=2)}")
                
                # Verify success structure
                if 'result' in result_data and 'message' in result_data:
                    print("✅ SUCCESS: Success response has correct structure")
                else:
                    print("❌ FAIL: Success response missing required fields")
                    
            except json.JSONDecodeError:
                print("❌ FAIL: Response is not valid JSON")
                
        else:
            print(f"❌ FAIL: Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ FAIL: Request failed: {e}")

if __name__ == "__main__":
    print("Mikrotik API Error Handling Test")
    print("="*50)
    
    # Check if JWT token is set
    if JWT_TOKEN == "your_jwt_token_here":
        print("❌ Please set a valid JWT_TOKEN in the script")
        print("You can get one by calling /users/login/ endpoint")
        exit(1)
    
    test_invalid_command()
    test_valid_command()
    
    print("\n" + "="*50)
    print("Test completed!")
