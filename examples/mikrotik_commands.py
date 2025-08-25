#!/usr/bin/env python3
"""
Comprehensive examples of using the enhanced Mikrotik Command API
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
JWT_TOKEN = "your_jwt_token_here"  # Replace with actual token
ROUTER_ID = 1  # Replace with actual router ID

def execute_command(command, method='GET', params=None, data=None):
    """Helper function to execute commands"""
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "command": command,
        "method": method
    }
    
    if params:
        payload["params"] = params
    if data:
        payload["data"] = data
    
    print(f"\n{'='*60}")
    print(f"Executing: {method} {command}")
    if params:
        print(f"Params: {params}")
    if data:
        print(f"Data: {data}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/routers/{ROUTER_ID}/execute-command/",
            headers=headers,
            json=payload
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS")
            print(f"Result: {json.dumps(result['result'], indent=2)}")
            return result
        else:
            error = response.json()
            print("❌ FAILED")
            print(f"Error: {error['error']}")
            return None
            
    except Exception as e:
        print(f"❌ REQUEST FAILED: {e}")
        return None

def example_hotspot_operations():
    """Example hotspot operations"""
    print("\n🔥 HOTSPOT OPERATIONS")
    
    # 1. Get all hotspots
    execute_command("ip/hotspot", "GET")
    
    # 2. Get specific hotspot
    execute_command("ip/hotspot", "GET", {"?name": "hotspot1"})
    
    # 3. Create new hotspot
    execute_command("ip/hotspot/add", "POST", data={
        "name": "hotspot1",
        "address-pool": "pool1",
        "profile": "default"
    })
    
    # 4. Update hotspot
    execute_command("ip/hotspot/set", "PUT", data={
        ".id": "*1",
        "profile": "premium"
    })
    
    # 5. Delete hotspot
    execute_command("ip/hotspot/remove", "DELETE", data={
        ".id": "*1"
    })

def example_network_operations():
    """Example network operations"""
    print("\n🌐 NETWORK OPERATIONS")
    
    # 1. Get IP addresses
    execute_command("ip/address", "GET")
    
    # 2. Add IP address
    execute_command("ip/address/add", "POST", data={
        "address": "192.168.1.100/24",
        "interface": "ether1"
    })
    
    # 3. Get interfaces
    execute_command("interface", "GET")
    
    # 4. Get DHCP server
    execute_command("ip/dhcp-server", "GET")

def example_system_operations():
    """Example system operations"""
    print("\n⚙️ SYSTEM OPERATIONS")
    
    # 1. Get system resource info
    execute_command("system/resource", "GET")
    
    # 2. Get system identity
    execute_command("system/identity", "GET")
    
    # 3. Get system clock
    execute_command("system/clock", "GET")
    
    # 4. Get system note
    execute_command("system/note", "GET")

def example_firewall_operations():
    """Example firewall operations"""
    print("\n🔥 FIREWALL OPERATIONS")
    
    # 1. Get firewall rules
    execute_command("ip/firewall/filter", "GET")
    
    # 2. Get firewall NAT rules
    execute_command("ip/firewall/nat", "GET")
    
    # 3. Add firewall rule
    execute_command("ip/firewall/filter/add", "POST", data={
        "chain": "input",
        "protocol": "tcp",
        "dst-port": "80",
        "action": "accept",
        "comment": "Allow HTTP"
    })

def example_user_operations():
    """Example user operations"""
    print("\n👤 USER OPERATIONS")
    
    # 1. Get hotspot users
    execute_command("ip/hotspot/user", "GET")
    
    # 2. Add hotspot user
    execute_command("ip/hotspot/user/add", "POST", data={
        "username": "testuser",
        "password": "testpass",
        "profile": "default"
    })
    
    # 3. Get user profiles
    execute_command("ip/hotspot/user/profile", "GET")

def example_advanced_queries():
    """Example advanced queries with parameters"""
    print("\n🔍 ADVANCED QUERIES")
    
    # 1. Get specific items by ID
    execute_command("ip/hotspot", "GET", {"?.id": "*1"})
    
    # 2. Get items with multiple filters
    execute_command("ip/hotspot/user", "GET", {
        "?profile": "default",
        "?limit": "10"
    })
    
    # 3. Get items with custom fields
    execute_command("system/resource", "GET", {
        "?cpu-load": ">10"
    })

def main():
    """Main function to run all examples"""
    print("🚀 Mikrotik Enhanced Command API Examples")
    print("=" * 60)
    
    if JWT_TOKEN == "your_jwt_token_here":
        print("❌ Please set a valid JWT_TOKEN in the script")
        print("You can get one by calling /users/login/ endpoint")
        return
    
    try:
        # Run examples
        example_system_operations()
        example_network_operations()
        example_hotspot_operations()
        example_firewall_operations()
        example_user_operations()
        example_advanced_queries()
        
        print("\n" + "="*60)
        print("✅ All examples completed!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Examples failed: {e}")

if __name__ == "__main__":
    main()
