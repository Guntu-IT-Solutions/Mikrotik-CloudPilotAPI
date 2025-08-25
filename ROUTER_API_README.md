# Mikrotik Router API Documentation

This document describes the comprehensive Router API system for managing Mikrotik routers through the CloudPilot API.

## Overview

The Router API system provides a secure, user-specific way to manage Mikrotik routers. All data is stored in a single database with proper user isolation through filtering:

- Router CRUD operations
- Connection status checking
- Device information retrieval
- Custom command execution
- Interface statistics
- DHCP lease management
- Firewall rule management

## Features

### 🔐 Security
- **User Isolation**: Each user's routers are filtered and isolated through proper database queries
- **Password Encryption**: Router passwords are encrypted using Fernet encryption
- **Authentication Required**: All endpoints require JWT authentication or dual API keys
- **User-Specific Access**: Users can only access their own routers

### 🌐 Router Management
- **Add/Edit/Delete Routers**: Full CRUD operations for router management
- **Connection Testing**: Test router connectivity before saving
- **Status Monitoring**: Track online/offline status and last check time
- **Bulk Operations**: Check status of all user's routers at once

### 📊 Device Information
- **System Resources**: CPU, memory, disk usage
- **Network Interfaces**: Interface status and configuration
- **IP Addresses**: Current IP configuration
- **DHCP Server**: DHCP server status and configuration
- **Wireless Interfaces**: Wireless network information
- **Firewall Rules**: Current firewall configuration

### ⚡ Command Execution
- **Custom Commands**: Execute any Mikrotik API command
- **Smart Method Detection**: Automatically determines HTTP method based on command
- **Parameter Support**: Pass additional parameters to commands
- **Error Handling**: Comprehensive error handling and reporting

## API Endpoints

### Router Management

#### List/Create Routers
```
GET/POST /routers/
```
- **GET**: List all routers for the authenticated user
- **POST**: Create a new router

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

#### Router Details
```
GET/PUT/DELETE /routers/{id}/
```
- **GET**: Get router details
- **PUT**: Update router configuration
- **DELETE**: Remove router

### Router Operations

#### Test Connection
```
POST /routers/{router_id}/test-connection/
```
Test router connection and update status.

#### Execute Command
```
POST /routers/{router_id}/execute-command/
```
**Request Body:**
```json
{
    "command": "system/resource"
}
```

#### Get Device Info
```
GET /routers/{router_id}/device-info/
```
Get comprehensive device information.

## Authentication

Router endpoints support **two authentication methods**:

### Method 1: JWT Token (Recommended for authenticated users)
```
Authorization: Bearer <your_jwt_token>
```

### Method 2: Dual API Keys (For unauthenticated access)
```
X-API-Key: <your_public_key>
X-Private-Key: <your_private_key>
```

**Security**: Both keys must be correct and match for authentication to succeed. This prevents unauthorized access even if one key is compromised.

**Flexibility**: Choose the method that best fits your use case. JWT tokens are ideal for web applications, while dual API keys work well for scripts and external integrations.

**Note**: API keys are user-specific and provide access to only that user's routers and data.

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

## Setup Instructions

### 1. Generate Encryption Key
```bash
python manage.py generate_encryption_key
```

### 2. Update Settings
Copy the generated key to `settings.py`:
```python
ENCRYPTION_KEY = b'your-generated-key-here'
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. User Registration (Automatic Setup)
Users can register through the API endpoint. API keys are automatically created:

```bash
curl -X POST http://localhost:8000/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'
```

**Response includes:**
- User ID
- Auto-generated API key (public and private)

**Note**: All database setup is completed during installation. API keys are automatically created when users register.

### 5. Generate Additional API Keys (Optional)
Users can generate additional API keys through the API:

```bash
# First get a JWT token
curl -X POST http://localhost:8000/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePassword123!"
  }'

# Then generate a new API key
curl -X POST http://localhost:8000/users/generate-api-key/ \
  -H "Authorization: Bearer <jwt_token>"
```

## Usage Examples

### Create a Router

**Using JWT Token:**
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

**Using Dual API Keys:**
```bash
curl -X POST http://localhost:8000/routers/ \
  -H "X-API-Key: <your_public_key>" \
  -H "X-Private-Key: <your_private_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Home Router",
    "host": "192.168.1.1",
    "username": "admin",
    "password": "password123"
  }'
```

### Test Router Connection

**Using JWT Token:**
```bash
curl -X POST http://localhost:8000/routers/1/test-connection/ \
  -H "Authorization: Bearer <your_jwt_token>"
```

**Using Dual API Keys:**
```bash
curl -X POST http://localhost:8000/routers/1/test-connection/ \
  -H "X-API-Key: <your_public_key>" \
  -H "X-Private-Key: <your_private_key>"
```

### Get Device Info

**Using JWT Token:**
```bash
curl -X GET http://localhost:8000/routers/1/device-info/ \
  -H "Authorization: Bearer <your_jwt_token>"
```

**Using Dual API Keys:**
```bash
curl -X GET http://localhost:8000/routers/1/device-info/ \
  -H "X-API-Key: <your_public_key>" \
  -H "X-Private-Key: <your_private_key>"
```

### Execute Custom Command
```bash
curl -X POST http://localhost:8000/routers/1/execute-command/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "ip/address/add",
    "params": {
      "address": "192.168.1.100/24",
      "interface": "ether1"
    }
  }'
```

## Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing or invalid authentication
- **404 Not Found**: Router not found or access denied
- **500 Internal Server Error**: Server or Mikrotik API errors

Error responses include detailed error messages:
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
Enable Django debug mode to see detailed error information during development.

## Support

For issues and questions:
1. Check the Django logs for detailed error messages
2. Verify router connectivity manually
3. Ensure all dependencies are installed
4. Check database configuration and migrations
