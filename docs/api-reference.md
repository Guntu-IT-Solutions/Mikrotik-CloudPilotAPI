# API Reference

This document provides a quick reference for all API endpoints in the Mikrotik CloudPilot API.

## Authentication

All endpoints require authentication using one of these methods:

### Method 1: JWT Token
```
Authorization: Bearer <your_jwt_token>
```

### Method 2: Dual API Keys
```
X-API-Key: <your_public_key>
X-Private-Key: <your_private_key>
```

## Base URL
```
http://localhost:8000
```

## User Management

### Register User
```http
POST /users/register/
Content-Type: application/json

{
    "username": "string",
    "email": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "message": "User registered successfully",
    "user_id": 1,
    "api_key": {
        "public_key": "string",
        "message": "Store your private key securely — it won't be shown again."
    },
    "note": "API keys created automatically"
}
```

### Login User
```http
POST /users/login/
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "access_token": "string",
    "refresh_token": "string",
    "user_id": 1,
    "username": "string"
}
```

### Get User Profile
```http
GET /users/profile/
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "bio": "string",
    "website": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### Update User Profile
```http
PUT /users/profile/
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "bio": "string",
    "website": "string"
}
```

### Get API Keys
```http
GET /users/api-keys/
Authorization: Bearer <jwt_token>
```

### Generate New API Key
```http
POST /users/generate-api-key/
Authorization: Bearer <jwt_token>
```

### Rotate API Keys
```http
POST /users/rotate-api-keys/
Authorization: Bearer <jwt_token>
```

## Router Management

### List Routers
```http
GET /routers/
Authorization: Bearer <jwt_token>
```

**Response:**
```json
[
    {
        "id": 1,
        "name": "string",
        "host": "string",
        "port": 80,
        "username": "string",
        "use_https": false,
        "is_online": false,
        "last_checked": "datetime",
        "created_at": "datetime",
        "updated_at": "datetime"
    }
]
```

### Create Router
```http
POST /routers/
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "name": "string",
    "host": "string",
    "port": 80,
    "username": "string",
    "password": "string",
    "use_https": false
}
```

### Get Router Details
```http
GET /routers/{id}/
Authorization: Bearer <jwt_token>
```

### Update Router
```http
PUT /routers/{id}/
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "name": "string",
    "host": "string",
    "port": 80,
    "username": "string",
    "password": "string",
    "use_https": false
}
```

### Delete Router
```http
DELETE /routers/{id}/
Authorization: Bearer <jwt_token>
```

## Router Operations

### Test Connection
```http
POST /routers/{id}/test-connection/
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "router_id": 1,
    "is_online": true,
    "message": "Connection test completed"
}
```

### Execute Command
```http
POST /routers/{id}/execute-command/
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "command": "string"
}
```

**Response:**
```json
{
    "router_id": 1,
    "command": "string",
    "result": "object",
    "message": "Command executed successfully"
}
```

### Get Device Info
```http
GET /routers/{id}/device-info/
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
    "router_id": 1,
    "device_info": {
        "identity": "string",
        "cpu_load": "string",
        "free_memory": "string",
        "total_memory": "string",
        "free_hdd_space": "string",
        "total_hdd_space": "string",
        "version": "string",
        "uptime": "string"
    },
    "message": "Device information retrieved successfully"
}
```

## Error Responses

All endpoints return consistent error responses:

### 400 Bad Request
```json
{
    "error": "Detailed error description"
}
```

### 401 Unauthorized
```json
{
    "error": "Authentication credentials were not provided or are invalid"
}
```

### 404 Not Found
```json
{
    "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal server error occurred"
}
```

## Setup Commands

### Generate Encryption Key
```bash
python manage.py generate_encryption_key
```

### Run Migrations
```bash
python manage.py migrate
```

## Example Usage

### Complete Router Management Flow

1. **Register a user:**
```bash
curl -X POST http://localhost:8000/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

2. **Login to get JWT token:**
```bash
curl -X POST http://localhost:8000/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

3. **Create a router:**
```bash
curl -X POST http://localhost:8000/routers/ \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Router",
    "host": "192.168.1.1",
    "username": "admin",
    "password": "password123"
  }'
```

4. **Test router connection:**
```bash
curl -X POST http://localhost:8000/routers/1/test-connection/ \
  -H "Authorization: Bearer <jwt_token>"
```

5. **Get device information:**
```bash
curl -X GET http://localhost:8000/routers/1/device-info/ \
  -H "Authorization: Bearer <jwt_token>"
```

### Using Dual API Keys

If you prefer to use API keys instead of JWT tokens:

```bash
curl -X GET http://localhost:8000/routers/ \
  -H "X-API-Key: <your_public_key>" \
  -H "X-Private-Key: <your_private_key>"
```

## Notes

- **User Isolation**: All endpoints automatically filter data based on the authenticated user
- **Password Security**: Router passwords are encrypted before storage
- **Authentication**: Choose between JWT tokens (web apps) or dual API keys (scripts)
- **Error Handling**: All endpoints provide detailed error messages for debugging
