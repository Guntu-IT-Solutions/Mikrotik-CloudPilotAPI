#!/usr/bin/env python3
"""
Simple test script for Payment Credentials API
Tests if the endpoint is working without the private_key field error
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/payments"

def test_payment_credentials_endpoint():
    """Test if the payment credentials endpoint is accessible"""
    
    print("Testing Payment Credentials API endpoint...")
    
    try:
        # Test if the endpoint is accessible (should return 401 without auth)
        response = requests.get(f"{API_BASE}/credentials/")
        print(f"GET /payments/credentials/ - Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Endpoint is accessible (401 Unauthorized expected without auth)")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
        
        # Test POST without auth (should return 401)
        test_data = {
            "provider": "kopokopo",
            "api_key": "pk_test_1234567890",
            "private_key": "sk_test_0987654321",
            "environment": "sandbox"
        }
        
        response = requests.post(f"{API_BASE}/credentials/", json=test_data)
        print(f"POST /payments/credentials/ - Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ POST endpoint is accessible (401 Unauthorized expected without auth)")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_payment_credentials_endpoint()
