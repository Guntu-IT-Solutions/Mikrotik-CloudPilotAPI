import requests
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from django.conf import settings
from .models import Router
from django.utils import timezone
from datetime import datetime
import xml.etree.ElementTree as ET
from .models import Router
from django.contrib.auth.models import User
import requests
import json
from requests.auth import HTTPBasicAuth
import ssl
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

logger = logging.getLogger(__name__)

class MikrotikAPIError(Exception):
    """Custom exception for Mikrotik API errors"""
    pass

class MikrotikAPIClient:
    """Client for interacting with Mikrotik RouterOS API"""
    
    def __init__(self, router):
        self.router = router
        self.base_url = router.base_url
        self.username = router.username
        self.password = router.get_password()
        self.session = requests.Session()
        
        # Disable SSL verification if not using HTTPS
        if not router.use_https:
            self.session.verify = False
        
        # Set up basic auth
        self.session.auth = HTTPBasicAuth(self.username, self.password)
    
    def test_connection(self):
        """Test if we can connect to the router"""
        try:
            response = self.session.get(f"{self.base_url}/system/resource", timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def execute_command(self, command, method='GET', params=None, data=None):
        """Execute a command on the router
        
        Args:
            command (str): Mikrotik command path (e.g., 'ip/hotspot', 'system/resource')
            method (str): HTTP method ('GET', 'POST', 'PUT', 'DELETE')
            params (dict): Query parameters for GET requests
            data (dict): JSON data for POST/PUT requests
        """
        try:
            url = f"{self.base_url}/{command}"
            
            # Handle different HTTP methods
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=10)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, timeout=10)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=10)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported HTTP method: {method}",
                    "status_code": 400
                }
            
            if response.status_code == 200:
                # Handle empty responses (some DELETE operations)
                if response.content:
                    try:
                        response_data = response.json()
                    except:
                        response_data = response.text
                else:
                    response_data = {"message": "Operation completed successfully"}
                
                return {"success": True, "data": response_data}
            else:
                # Parse error response from Mikrotik
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', 'Unknown error')
                    error_detail = error_data.get('detail', '')
                    if error_detail:
                        error_message = f"{error_message}: {error_detail}"
                except:
                    error_message = response.text or f"HTTP {response.status_code}"
                
                return {
                    "success": False, 
                    "error": error_message,
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Command execution failed: {str(e)}",
                "status_code": 500
            }
    
    def get_device_info(self):
        """Get basic device information"""
        try:
            # Get system resource info
            resource_response = self.session.get(f"{self.base_url}/system/resource", timeout=10)
            if resource_response.status_code != 200:
                return {"error": "Failed to get system resource info"}
            
            # Get system identity
            identity_response = self.session.get(f"{self.base_url}/system/identity", timeout=10)
            if identity_response.status_code != 200:
                return {"error": "Failed to get system identity"}
            
            resource_data = resource_response.json()
            identity_data = identity_response.json()
            
            return {
                "identity": identity_data.get('name', 'Unknown'),
                "cpu_load": resource_data.get('cpu-load', 'Unknown'),
                "free_memory": resource_data.get('free-memory', 'Unknown'),
                "total_memory": resource_data.get('total-memory', 'Unknown'),
                "free_hdd_space": resource_data.get('free-hdd-space', 'Unknown'),
                "total_hdd_space": resource_data.get('total-hdd-space', 'Unknown'),
                "version": resource_data.get('version', 'Unknown'),
                "uptime": resource_data.get('uptime', 'Unknown')
            }
        except Exception as e:
            return {"error": f"Failed to get device info: {str(e)}"}
    
    def close(self):
        """Close the session"""
        self.session.close()

class MikrotikAPIManager:
    """Manager class for Mikrotik API operations"""
    
    @staticmethod
    def test_connection(router):
        """Test connection to a specific router"""
        client = MikrotikAPIClient(router)
        try:
            return client.test_connection()
        finally:
            client.close()
    
    @staticmethod
    def execute_command(router, command, method='GET', params=None, data=None):
        """Execute a command on a specific router
        
        Args:
            router: Router instance
            command (str): Mikrotik command path
            method (str): HTTP method ('GET', 'POST', 'PUT', 'DELETE')
            params (dict): Query parameters for GET requests
            data (dict): JSON data for POST/PUT requests
        """
        client = MikrotikAPIClient(router)
        try:
            return client.execute_command(command, method, params, data)
        finally:
            client.close()
    
    @staticmethod
    def get_device_info(router):
        """Get device information for a specific router"""
        client = MikrotikAPIClient(router)
        try:
            return client.get_device_info()
        finally:
            client.close()
    
    @staticmethod
    def get_router_by_id(router_id, user):
        """Get a router by ID for a specific user"""
        try:
            return Router.objects.get(id=router_id, user=user)
        except Router.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_routers(user):
        """Get all routers for a specific user"""
        return Router.objects.filter(user=user)