# Router API Documentation

This document provides comprehensive information about the Router API endpoints for managing Mikrotik routers.

## Overview

The Router API provides secure, user-specific router management capabilities. All data is stored in a single database with proper user isolation through filtering:

- **Router CRUD Operations**: Create, read, update, and delete routers
- **Connection Testing**: Verify router connectivity and update status
- **Command Execution**: Execute custom commands on Mikrotik devices
- **Device Information**: Retrieve comprehensive device details
- **Package Management**: View available WiFi packages for each router
- **User Isolation**: Users can only access their own routers

## Authentication

All router endpoints require authentication using JWT tokens obtained through login:

### JWT Token Authentication
```http
Authorization: Bearer <your_jwt_token>
```

**How to get JWT tokens:**
1. **Username/Password**: `POST /users/login/`
2. **API Keys**: `POST /users/api-key-login/` (requires both public and private keys)

**Security Note**: JWT tokens provide secure, time-limited access to your routers and commands. Choose your preferred login method - both return the same JWT tokens.

## Database Structure

### Router Model
```python
class Router(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routers')
    name = models.CharField(max_length=100)
    host = models.CharField(max_length=255)  # IP or domain
    port = models.PositiveIntegerField(default=80)
    username = models.CharField(max_length=50)
    encrypted_password = models.BinaryField()
    use_https = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    last_checked = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Single Database Architecture
All data is stored in the default `db.sqlite3` database. User isolation is achieved through proper filtering in queries, ensuring users can only access their own data.

## API Endpoints

### Router Management

#### List/Create Routers
```http
GET/POST /routers/
```

**GET**: List all routers for the authenticated user
**POST**: Create a new router

**POST Request Body:**
```json
{
    "name": "Office Router",
    "host": "192.168.1.1",
    "port": 80,
    "username": "admin",
    "password": "your_password",
    "use_https": false
}
```

**Response:**
```json
{
    "id": 1,
    "name": "Office Router",
    "host": "192.168.1.1",
    "port": 80,
    "username": "admin",
    "use_https": false,
    "is_online": false,
    "last_checked": null,
    "created_at": "2025-08-13T13:19:26Z",
    "updated_at": "2025-08-13T13:19:26Z"
}
```

#### Router Details
```http
GET/PUT/DELETE /routers/{id}/
```

**GET**: Get router details
**PUT**: Update router configuration
**DELETE**: Remove router

**PUT Request Body:**
```json
{
    "name": "Updated Router Name",
    "host": "192.168.1.10",
    "port": 443,
    "username": "admin",
    "password": "new_password",
    "use_https": true
}
```

**PUT Response:**
```json
{
    "id": 1,
    "name": "Updated Router Name",
    "host": "192.168.1.10",
    "port": 443,
    "username": "admin",
    "use_https": true,
    "is_online": false,
    "last_checked": null,
    "created_at": "2025-08-13T13:19:26Z",
    "updated_at": "2025-08-13T21:45:00Z"
}
```

**DELETE Response:**
```json
{
    "message": "Router \"Test Router\" has been successfully deleted"
}
```

### Router Operations

#### Test Connection
```http
POST /routers/{id}/test-connection/
```

Test router connectivity and update online status.

**Response:**
```json
{
    "router_id": 1,
    "is_online": true,
    "message": "Connection test completed"
}
```

#### Execute Command
```http
POST /routers/{id}/execute-command/
```

Execute custom commands on the Mikrotik router with support for different HTTP methods, query parameters, and request data.

**Request Body:**
```json
{
    "command": "ip/hotspot",
    "method": "GET",
    "params": {
        "?name": "hotspot1"
    }
}
```

**Enhanced Request Body (with data):**
```json
{
    "command": "ip/hotspot/add",
    "method": "POST",
    "data": {
        "name": "hotspot1",
        "address-pool": "pool1",
        "profile": "default"
    }
}
```

**Success Response:**
```json
{
    "router_id": 1,
    "command": "ip/hotspot",
    "method": "GET",
    "result": [
        {
            ".id": "*1",
            "name": "hotspot1",
            "address-pool": "pool1",
            "profile": "default"
        }
    ],
    "message": "Command executed successfully"
}
```

**Error Response:**
```json
{
    "router_id": 1,
    "command": "invalid/command",
    "method": "GET",
    "error": "Bad Request: no such command or directory (invalid)",
    "status_code": 400
}
```

**Supported HTTP Methods:**
- **GET**: Retrieve information (e.g., `ip/hotspot`, `system/resource`)
- **POST**: Create new items (e.g., `ip/hotspot/add`, `ip/address/add`)
- **PUT**: Update existing items (e.g., `ip/hotspot/set`)
- **DELETE**: Remove items (e.g., `ip/hotspot/remove`)

**Parameters:**
- `command` (required): Mikrotik command path
- `method` (optional): HTTP method (default: GET)
- `params` (optional): Query parameters for GET requests
- `data` (optional): JSON data for POST/PUT requests

#### Get Device Info
```http
GET /routers/{id}/device-info/
```

Retrieve comprehensive device information.

**Response:**
```json
{
    "router_id": 1,
    "device_info": {
        "identity": "MikroTik Router",
        "cpu_load": "5%",
        "free_memory": "52428800",
        "total_memory": "134217728",
        "free_hdd_space": "1073741824",
        "total_hdd_space": "2147483648",
        "version": "6.49.7",
        "uptime": "2d 15:30:45"
    },
    "message": "Device information retrieved successfully"
}
```

#### Get Router Packages
```http
GET /routers/{id}/packages/
```

Retrieve all active packages available for a specific router.

**Response:**
```json
{
    "router_id": 1,
    "router_name": "Office Router",
    "packages": [
        {
            "id": 1,
            "name": "Basic Hourly",
            "package_type": "hourly",
            "package_type_display": "Hourly Package",
            "duration_hours": 1,
            "duration_display": "1 hour",
            "price": "2.50",
            "currency": "KES",
            "download_speed_mbps": 10,
            "upload_speed_mbps": 5,
            "download_speed_display": "10 Mbps",
            "upload_speed_display": "5 Mbps",
            "speed_display": "10 Mbps / 5 Mbps",
            "description": "Basic internet access for 1 hour",
            "is_active": true
        },
        {
            "id": 2,
            "name": "Premium Monthly",
            "package_type": "monthly",
            "package_type_display": "Monthly Package",
            "duration_hours": 720,
            "duration_display": "1 month",
            "price": "150.00",
            "currency": "KES",
            "download_speed_mbps": 100,
            "upload_speed_mbps": 50,
            "download_speed_display": "100 Mbps",
            "upload_speed_display": "50 Mbps",
            "speed_display": "100 Mbps / 50 Mbps",
            "description": "High-speed internet for 1 month",
            "is_active": true
        }
    ],
    "message": "Found 2 active packages for Office Router"
}
```

## Package Model Structure

### Package Fields
```python
class Package(models.Model):
    name = models.CharField(max_length=100)                    # Package name
    router = models.ForeignKey(Router)                        # Associated router
    package_type = models.CharField(choices=PACKAGE_TYPES)    # hourly/monthly
    duration_hours = models.PositiveIntegerField()            # Duration in hours
    price = models.DecimalField()                             # Price in KES
    download_speed_mbps = models.PositiveIntegerField()       # Download speed limit
    upload_speed_mbps = models.PositiveIntegerField()         # Upload speed limit
    description = models.TextField()                          # Package description
    is_active = models.BooleanField()                         # Package availability
    created_at = models.DateTimeField()                       # Creation timestamp
    updated_at = models.DateTimeField()                       # Update timestamp
```

### Package Types
- **Hourly Packages**: Short-term access (1-24 hours)
- **Monthly Packages**: Long-term access (30 days = 720 hours)

### Speed Limits
- **Download Speed**: Maximum download bandwidth in Mbps
- **Upload Speed**: Maximum upload bandwidth in Mbps
- **Combined Display**: Shows both speeds as "Download / Upload"

### Package Validation
- Package names must be unique per router
- Prices must be greater than 0.01
- Duration must be specified in hours
- Both download and upload speeds are required

## Usage Examples

### Create a Router

=== "cURL"
    ```bash
    curl -X POST http://localhost:8000/routers/ \
      -H "Authorization: Bearer <your_jwt_token>" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "Home Router",
        "host": "192.168.1.1",
        "username": "admin",
        "password": "password123"
      }'
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>",
        "Content-Type": "application/json"
    }

    data = {
        "name": "Home Router",
        "host": "192.168.1.1",
        "username": "admin",
        "password": "password123"
    }

    response = requests.post(
        "http://localhost:8000/routers/",
        headers=headers,
        json=data
    )

    print(response.json())
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/routers/', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer <your_jwt_token>',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: 'Home Router',
            host: '192.168.1.1',
            username: 'admin',
            password: 'password123'
        })
    });

    const result = await response.json();
    console.log(result);
    ```

### Update Router Details

=== "cURL"
    ```bash
    curl -X PUT http://localhost:8000/routers/1/ \
      -H "Authorization: Bearer <your_jwt_token>" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "Updated Router Name",
        "port": 443,
        "use_https": true
      }'
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>",
        "Content-Type": "application/json"
    }

    data = {
        "name": "Updated Router Name",
        "port": 443,
        "use_https": True
    }

    response = requests.put(
        "http://localhost:8000/routers/1/",
        headers=headers,
        json=data
    )

    print(response.json())
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/routers/1/', {
        method: 'PUT',
        headers: {
            'Authorization': 'Bearer <your_jwt_token>',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: 'Updated Router Name',
            port: 443,
            use_https: true
        })
    });

    const result = await response.json();
    console.log(result);
    ```

### List Routers

=== "cURL"
    ```bash
    curl -X GET http://localhost:8000/routers/ \
      -H "Authorization: Bearer <your_jwt_token>"
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>"
    }

    response = requests.get(
        "http://localhost:8000/routers/",
        headers=headers
    )

    routers = response.json()
    print(f"Found {len(routers)} routers")
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/routers/', {
        headers: {
            'Authorization': 'Bearer <your_jwt_token>'
        }
    });

    const routers = await response.json();
    console.log(`Found ${routers.length} routers`);
    ```

### Test Router Connection

=== "cURL"
    ```bash
    curl -X POST http://localhost:8000/routers/1/test-connection/ \
      -H "Authorization: Bearer <your_jwt_token>"
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>"
    }

    response = requests.post(
        "http://localhost:8000/routers/1/test-connection/",
        headers=headers
    )

    result = response.json()
    print(f"Connection status: {result['is_online']}")
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/routers/1/test-connection/', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer <your_jwt_token>'
        }
    });

    const result = await response.json();
    console.log(`Connection status: ${result.is_online}`);
    ```

### Get Device Information

=== "cURL"
    ```bash
    curl -X GET http://localhost:8000/routers/1/device-info/ \
      -H "Authorization: Bearer <your_jwt_token>"
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>"
    }

    response = requests.get(
        "http://localhost:8000/routers/1/device-info/",
        headers=headers
    )

    device_info = response.json()
    print(f"Device: {device_info['device_info']['identity']}")
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/routers/1/device-info/', {
        headers: {
            'Authorization': 'Bearer <your_jwt_token>'
        }
    });

    const device_info = await response.json();
    console.log(`Device: ${device_info.device_info.identity}`);
    ```

### Get Router Packages

=== "cURL"
    ```bash
    curl -X GET http://localhost:8000/routers/1/packages/ \
      -H "Authorization: Bearer <your_jwt_token>"
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>"
    }

    response = requests.get(
        "http://localhost:8000/routers/1/packages/",
        headers=headers
    )

    packages = response.json()
    print(f"Found {len(packages['packages'])} packages for {packages['router_name']}")
    
    for package in packages['packages']:
        print(f"- {package['name']}: {package['speed_display']} for {package['duration_display']} at {package['price']} {package['currency']}")
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/routers/1/packages/', {
        headers: {
            'Authorization': 'Bearer <your_jwt_token>'
        }
    });

    const packages = await response.json();
    console.log(`Found ${packages.packages.length} packages for ${packages.router_name}`);
    
    packages.packages.forEach(package => {
        console.log(`- ${package.name}: ${package.speed_display} for ${package.duration_display} at ${package.price} ${package.currency}`);
    });
    ```

### Execute Custom Commands

=== "cURL"
    ```bash
    # Get hotspot information
    curl -X POST http://localhost:8000/routers/1/execute-command/ \
      -H "Authorization: Bearer <your_jwt_token>" \
      -H "Content-Type: application/json" \
      -d '{
        "command": "ip/hotspot",
        "method": "GET"
      }'
    
    # Get specific hotspot with query parameters
    curl -X POST http://localhost:8000/routers/1/execute-command/ \
      -H "Authorization: Bearer <your_jwt_token>" \
      -H "Content-Type: application/json" \
      -d '{
        "command": "ip/hotspot",
        "method": "GET",
        "params": {
          "?name": "hotspot1"
        }
      }'
    
    # Create new hotspot
    curl -X POST http://localhost:8000/routers/1/execute-command/ \
      -H "Authorization: Bearer <your_jwt_token>" \
      -H "Content-Type: application/json" \
      -d '{
        "command": "ip/hotspot/add",
        "method": "POST",
        "data": {
          "name": "hotspot1",
          "address-pool": "pool1",
          "profile": "default"
        }
      }'
    
    # Command that will fail
    curl -X POST http://localhost:8000/routers/1/execute-command/ \
      -H "Authorization: Bearer <your_jwt_token>" \
      -H "Content-Type: application/json" \
      -d '{
        "command": "invalid/command",
        "method": "GET"
      }'
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>",
        "Content-Type": "application/json"
    }

    # Get hotspot information
    data = {
        "command": "ip/hotspot",
        "method": "GET"
    }

    response = requests.post(
        "http://localhost:8000/routers/1/execute-command/",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        result = response.json()
        print(f"Hotspot info: {result['result']}")
    else:
        error = response.json()
        print(f"Command failed: {error['error']}")
    
    # Create new hotspot
    create_data = {
        "command": "ip/hotspot/add",
        "method": "POST",
        "data": {
            "name": "hotspot1",
            "address-pool": "pool1",
            "profile": "default"
        }
    }

    response = requests.post(
        "http://localhost:8000/routers/1/execute-command/",
        headers=headers,
        json=create_data
    )

    if response.status_code == 200:
        result = response.json()
        print(f"Hotspot created: {result['result']}")
    else:
        error = response.json()
        print(f"Creation failed: {error['error']}")
    ```

=== "JavaScript"
    ```javascript
    // Get hotspot information
    const response = await fetch('http://localhost:8000/routers/1/execute-command/', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer <your_jwt_token>',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            command: 'ip/hotspot',
            method: 'GET'
        })
    });

    if (response.ok) {
        const result = await response.json();
        console.log(`Hotspot info: ${result.result}`);
    } else {
        const error = await response.json();
        console.log(`Command failed: ${error.error}`);
    }
    
    // Create new hotspot
    const createResponse = await fetch('http://localhost:8000/routers/1/execute-command/', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer <your_jwt_token>',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            command: 'ip/hotspot/add',
            method: 'POST',
            data: {
                name: 'hotspot1',
                address_pool: 'pool1',
                profile: 'default'
            }
        })
    });

    if (createResponse.ok) {
        const result = await createResponse.json();
        console.log(`Hotspot created: ${result.result}`);
    } else {
        const error = await createResponse.json();
        console.log(`Creation failed: ${error.error}`);
    }
    ```

**Note**: When a command fails on the Mikrotik router, the API returns a 400 status code with detailed error information from the router.

### Delete Router

=== "cURL"
    ```bash
    curl -X DELETE http://localhost:8000/routers/1/ \
      -H "Authorization: Bearer <your_jwt_token>"
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>"
    }

    response = requests.delete(
        "http://localhost:8000/routers/1/",
        headers=headers
    )

    result = response.json()
    print(f"Delete message: {result['message']}")
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/routers/1/', {
        method: 'DELETE',
        headers: {
            'Authorization': 'Bearer <your_jwt_token>'
        }
    });

    const result = await response.json();
    console.log(`Delete message: ${result.message}`);
    ```

## Error Handling

The API provides comprehensive error handling with appropriate HTTP status codes:

### 400 Bad Request
Invalid input data or malformed requests.

### 401 Unauthorized
Missing or invalid authentication credentials.

### 404 Not Found
Router not found or access denied.

### 500 Internal Server Error
Server or Mikrotik API errors.

**Error Response Format:**
```json
{
    "error": "Detailed error description"
}
```

## Security Considerations

1. **Encryption Key**: Keep the encryption key secure and never commit it to version control
2. **User Isolation**: Each user's data is isolated through proper database filtering
3. **Password Security**: Router passwords are encrypted at rest
4. **Authentication**: All endpoints require valid JWT tokens or dual API keys
5. **Input Validation**: All inputs are validated and sanitized

## Troubleshooting

### Common Issues

1. **Connection Failed**: Check router IP, credentials, and network connectivity
2. **Encryption Error**: Ensure ENCRYPTION_KEY is properly set in settings
3. **Permission Denied**: Check JWT token validity and user authentication
4. **Router Not Found**: Verify router ID and user ownership

### Debug Mode
Enable Django debug mode in `settings.py` for detailed error information during development.

## Performance Notes

- **Single Database**: Efficient single database connection
- **Proper Filtering**: User data isolation through optimized queries
- **Connection Pooling**: Efficient Mikrotik API connection management
- **Caching**: Consider implementing caching for frequently accessed data

## Support

For additional help:

1. Check Django logs for detailed error messages
2. Verify router connectivity manually
3. Ensure all dependencies are installed
4. Check database configuration and migrations
5. Review the [API Reference](api-reference.md) for endpoint details


# Package API

This document provides comprehensive information about the Package API endpoints for managing WiFi internet packages.

## Overview

The Package API provides secure access to package information and management capabilities. All endpoints require authentication and provide user-specific data access:

- **Package Retrieval**: Get available packages for specific routers
- **Package Information**: Detailed package data with speed limits and pricing
- **Router Association**: Packages are linked to specific routers
- **User Isolation**: Users can only access packages for their own routers

## Authentication

All package endpoints require authentication using JWT tokens obtained through login:

### JWT Token Authentication
```http
Authorization: Bearer <your_jwt_token>
```

**How to get JWT tokens:**
1. **Username/Password**: `POST /users/login/`
2. **API Keys**: `POST /users/api-key-login/` (requires both public and private keys)

## API Endpoints

### Get Router Packages

#### Endpoint
```http
GET /routers/{id}/packages/
```

#### Description
Retrieve all active packages available for a specific router. This endpoint returns comprehensive package information including speed limits, pricing, and duration details.

#### Path Parameters
- `id` (integer, required): Router ID to get packages for

#### Request Headers
```http
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

#### Response Format

**Success Response (200 OK):**
```json
{
    "router_id": 1,
    "router_name": "Office Router",
    "packages": [
        {
            "id": 1,
            "name": "Basic Hourly",
            "package_type": "hourly",
            "package_type_display": "Hourly Package",
            "duration_hours": 1,
            "duration_display": "1 hour",
            "price": "2.50",
            "currency": "KES",
            "download_speed_mbps": 10,
            "upload_speed_mbps": 5,
            "download_speed_display": "10 Mbps",
            "upload_speed_display": "5 Mbps",
            "speed_display": "10 Mbps / 5 Mbps",
            "description": "Basic internet access for 1 hour",
            "is_active": true
        }
    ],
    "message": "Found 1 active packages for Office Router"
}
```

## Usage Examples

### Get Packages for a Router

=== "cURL"
    ```bash
    curl -X GET http://localhost:8000/routers/1/packages/ \
      -H "Authorization: Bearer <your_jwt_token>"
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>"
    }

    response = requests.get(
        "http://localhost:8000/routers/1/packages/",
        headers=headers
    )

    if response.status_code == 200:
        packages = response.json()
        print(f"Found {len(packages['packages'])} packages for {packages['router_name']}")
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/routers/1/packages/', {
        headers: {
            'Authorization': 'Bearer <your_jwt_token>'
        }
    });

    if (response.ok) {
        const packages = await response.json();
        console.log(`Found ${packages.packages.length} packages for ${packages.router_name}`);
    }
    ```

## Error Handling

### HTTP Status Codes

| Status | Description | Common Causes |
|--------|-------------|---------------|
| **200 OK** | Request successful | Valid request with packages found |
| **401 Unauthorized** | Authentication required | Missing or invalid JWT token |
| **404 Not Found** | Router not found | Invalid router ID or access denied |

### Error Response Format
```json
{
    "error": "Detailed error description"
}
```

## Security Features

### Access Control
- **JWT Authentication**: Secure token-based authentication
- **User Isolation**: Users can only access their own router packages
- **Router Validation**: Verifies router ownership before package access

## Related Documentation

- **[Package Management](packages.md)**: Comprehensive package management guide
- **[Router API](router-api.md)**: Router management and operations
- **[Authentication](authentication.md)**: JWT authentication system
- **[API Reference](api-reference.md)**: Complete API endpoint reference
