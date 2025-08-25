# Authentication

The Mikrotik CloudPilot API uses a simple, clean JWT authentication system:

## Authentication Flow

1. **Get API Keys**: Register a user to receive API keys
2. **Login**: Use either username/password OR API keys to get JWT tokens
3. **Use JWT Tokens**: Access all protected endpoints with JWT tokens

## Login Methods

### Method 1: Username/Password Login
```http
POST /users/login/
```

**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

### Method 2: API Key Login
```http
POST /users/api-key-login/
```

**Request Body:**
```json
{
    "public_key": "your_public_api_key",
    "private_key": "your_private_api_key"
}
```

## Login Response

Both login methods return the same JWT tokens:

```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_id": 1,
    "username": "your_username"
}
```

## Using JWT Tokens

Once you have obtained a JWT token, use it to authenticate all protected requests:

```http
Authorization: Bearer <your_jwt_token>
```

## API Key Management

### Generate New API Keys
```http
POST /users/generate-api-key/
Authorization: Bearer <your_jwt_token>
```

### Get Current API Keys
```http
GET /users/api-keys/
Authorization: Bearer <your_jwt_token>
```

### Rotate API Keys
```http
POST /users/rotate-api-keys/
Authorization: Bearer <your_jwt_token>
```

## Security Notes

1. **JWT Tokens**: All protected endpoints require JWT tokens
2. **API Keys**: Used only for initial authentication to obtain JWT tokens
3. **Token Expiry**: JWT tokens have expiration times for security
4. **Private Keys**: Store private API keys securely - they're only shown once

## Example Usage

### Option 1: Username/Password Login
```bash
# Login with username/password
curl -X POST http://localhost:8000/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

### Option 2: API Key Login
```bash
# Login with API keys
curl -X POST http://localhost:8000/users/api-key-login/ \
  -H "Content-Type: application/json" \
  -d '{
    "public_key": "your_public_key",
    "private_key": "your_private_key"
  }'
```

### Use JWT Token for All Operations
```bash
# Access routers
curl -X GET http://localhost:8000/routers/ \
  -H "Authorization: Bearer <jwt_token>"

# Execute commands
curl -X POST http://localhost:8000/routers/1/execute-command/ \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"command": "system/resource"}'

# Manage profile
curl -X GET http://localhost:8000/users/profile/ \
  -H "Authorization: Bearer <jwt_token>"
```

## Error Responses

### Invalid Credentials
```json
{
    "error": "Invalid credentials"
}
```

### Invalid API Keys
```json
{
    "error": "Invalid API keys"
}
```

### Missing Fields
```json
{
    "error": "Public key and private key are required"
}
```

### Unauthorized Access
```json
{
    "detail": "Authentication credentials were not provided."
}
```
