#!/usr/bin/env python3
"""
Test script for Payment Credentials API endpoints
Tests the encrypted private key functionality for Kopokopo and InstaSend
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/payments"

def print_response(response, title):
    """Print formatted API response"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_payment_credentials():
    """Test the complete payment credentials workflow"""
    
    # Step 1: Register a user (if not exists)
    print("Step 1: Registering user...")
    register_data = {
        "username": "payment_user",
        "email": "payment@example.com",
        "password": "securepass123"
    }
    
    register_response = requests.post(f"{BASE_URL}/users/register/", json=register_data)
    if register_response.status_code == 201:
        print("User registered successfully")
    elif register_response.status_code == 400 and "already exists" in register_response.text:
        print("User already exists, continuing...")
    else:
        print(f"Failed to register user: {register_response.text}")
        return
    
    # Step 2: Login to get JWT token
    print("\nStep 2: Logging in...")
    login_data = {
        "username": "payment_user",
        "password": "securepass123"
    }
    
    login_response = requests.post(f"{BASE_URL}/users/login/", json=login_data)
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    access_token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}
    print("Login successful, JWT token obtained")
    
    # Step 3: Create Kopokopo credentials
    print("\nStep 3: Creating Kopokopo credentials...")
    kopokopo_data = {
        "provider": "kopokopo",
        "api_key": "pk_test_kopokopo_1234567890abcdef",
        "private_key": "sk_test_kopokopo_0987654321fedcba",
        "environment": "sandbox"
    }
    
    kopokopo_response = requests.post(
        f"{API_BASE}/credentials/", 
        json=kopokopo_data, 
        headers=headers
    )
    print_response(kopokopo_response, "Create Kopokopo Credentials")
    
    if kopokopo_response.status_code != 201:
        print("Failed to create Kopokopo credentials")
        return
    
    kopokopo_id = kopokopo_response.json()['id']
    
    # Step 4: Create InstaSend credentials
    print("\nStep 4: Creating InstaSend credentials...")
    instasend_data = {
        "provider": "instasend",
        "api_key": "pk_test_instasend_1234567890abcdef",
        "private_key": "sk_test_instasend_0987654321fedcba",
        "environment": "sandbox"
    }
    
    instasend_response = requests.post(
        f"{API_BASE}/credentials/", 
        json=instasend_data, 
        headers=headers
    )
    print_response(instasend_response, "Create InstaSend Credentials")
    
    if instasend_response.status_code != 201:
        print("Failed to create InstaSend credentials")
        return
    
    instasend_id = instasend_response.json()['id']
    
    # Step 5: List all credentials
    print("\nStep 5: Listing all credentials...")
    list_response = requests.get(f"{API_BASE}/credentials/", headers=headers)
    print_response(list_response, "List All Credentials")
    
    # Step 6: Get credentials by provider
    print("\nStep 6: Getting credentials by provider...")
    kopokopo_provider_response = requests.get(
        f"{API_BASE}/credentials/provider/kopokopo/", 
        headers=headers
    )
    print_response(kopokopo_provider_response, "Get Kopokopo Credentials by Provider")
    
    # Step 7: Verify credentials
    print("\nStep 7: Verifying credentials...")
    verify_data = {"private_key": "sk_test_kopokopo_0987654321fedcba"}
    verify_response = requests.post(
        f"{API_BASE}/credentials/{kopokopo_id}/verify/", 
        json=verify_data, 
        headers=headers
    )
    print_response(verify_response, "Verify Kopokopo Credentials")
    
    # Step 8: Get private key (decrypted)
    print("\nStep 8: Getting decrypted private key...")
    private_key_response = requests.get(
        f"{API_BASE}/credentials/{kopokopo_id}/get-private-key/", 
        headers=headers
    )
    print_response(private_key_response, "Get Decrypted Private Key")
    
    # Step 9: Update private key
    print("\nStep 9: Updating private key...")
    update_data = {"private_key": "sk_test_kopokopo_new_private_key_12345"}
    update_response = requests.post(
        f"{API_BASE}/credentials/{kopokopo_id}/update-private-key/", 
        json=update_data, 
        headers=headers
    )
    print_response(update_response, "Update Private Key")
    
    # Step 10: Toggle credentials status
    print("\nStep 10: Toggling credentials status...")
    toggle_response = requests.post(
        f"{API_BASE}/credentials/{kopokopo_id}/toggle-status/", 
        headers=headers
    )
    print_response(toggle_response, "Toggle Credentials Status")
    
    # Step 11: Test with wrong private key
    print("\nStep 11: Testing with wrong private key...")
    wrong_verify_data = {"private_key": "wrong_private_key_12345"}
    wrong_verify_response = requests.post(
        f"{API_BASE}/credentials/{kopokopo_id}/verify/", 
        json=wrong_verify_data, 
        headers=headers
    )
    print_response(wrong_verify_response, "Verify with Wrong Private Key")
    
    print(f"\n{'='*50}")
    print("Payment Credentials Testing Complete!")
    print(f"{'='*50}")

if __name__ == "__main__":
    try:
        test_payment_credentials()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure Django is running on localhost:8000")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
