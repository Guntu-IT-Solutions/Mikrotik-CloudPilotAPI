# Payment Credentials API

The Payment Credentials API allows users to securely store and manage their payment provider API credentials for Kopokopo and InstaSend. Private keys are encrypted using the project's encryption key for enhanced security.

## Features

- **Secure Storage**: Private keys are encrypted using Fernet encryption
- **Multiple Providers**: Support for Kopokopo and InstaSend with more to be added
- **Environment Support**: Sandbox and Live environments
- **Verification**: Hash-based verification of private keys
- **Status Management**: Activate/deactivate credentials as needed

## Authentication

All endpoints require JWT authentication. Include the JWT token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### 1. List/Create Payment Credentials

#### GET /payments/credentials/
List all payment credentials for the authenticated user.

**Response:**
```json
[
    {
        "id": 1,
        "provider": "kopokopo",
        "provider_display": "KopoKopo",
        "environment": "sandbox",
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "is_live": false,
        "is_sandbox": true
    }
]
```

#### POST /payments/credentials/
Create new payment credentials.

**Request Body:**
```json
{
    "provider": "kopokopo",
    "api_key": "pk_test_kopokopo_1234567890abcdef",
    "private_key": "sk_test_kopokopo_0987654321fedcba",
    "environment": "sandbox"
}
```

**Response:**
```json
{
    "id": 1,
    "provider": "kopokopo",
    "provider_display": "KopoKopo",
    "environment": "sandbox",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "is_live": false,
    "is_sandbox": true
}
```

### 2. Manage Specific Credentials

#### GET /payments/credentials/{id}/
Retrieve specific payment credentials.

#### PUT /payments/credentials/{id}/
Update payment credentials (excluding private key).

**Request Body:**
```json
{
    "api_key": "pk_test_kopokopo_new_key_12345",
    "environment": "live"
}
```

#### DELETE /payments/credentials/{id}/
Delete payment credentials.

**Response:**
```json
{
    "message": "Payment credentials for KopoKopo have been successfully deleted"
}
```

### 3. Private Key Management

#### POST /payments/credentials/{id}/update-private-key/
Update the private key for existing credentials.

**Request Body:**
```json
{
    "private_key": "sk_test_kopokopo_new_private_key_12345"
}
```

**Response:**
```json
{
    "message": "Private key updated successfully",
    "credentials": {
        "id": 1,
        "provider": "kopokopo",
        "provider_display": "KopoKopo",
        "environment": "sandbox",
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:35:00Z",
        "is_live": false,
        "is_sandbox": true
    }
}
```

#### GET /payments/credentials/{id}/get-private-key/
Retrieve the decrypted private key for API usage.

**Response:**
```json
{
    "credentials_id": 1,
    "provider": "kopokopo",
    "provider_display": "KopoKopo",
    "private_key": "sk_test_kopokopo_0987654321fedcba",
    "message": "Private key retrieved successfully"
}
```

### 4. Verification and Status

#### POST /payments/credentials/{id}/verify/
Verify credentials by checking the private key.

**Request Body:**
```json
{
    "private_key": "sk_test_kopokopo_0987654321fedcba"
}
```

**Response (Valid):**
```json
{
    "credentials_id": 1,
    "provider": "kopokopo",
    "provider_display": "KopoKopo",
    "is_valid": true,
    "message": "Credentials verified successfully"
}
```

**Response (Invalid):**
```json
{
    "credentials_id": 1,
    "provider": "kopokopo",
    "provider_display": "KopoKopo",
    "is_valid": false,
    "message": "Invalid private key"
}
```

#### POST /payments/credentials/{id}/toggle-status/
Toggle the active status of credentials.

**Response:**
```json
{
    "message": "Payment credentials for KopoKopo have been deactivated",
    "credentials": {
        "id": 1,
        "provider": "kopokopo",
        "provider_display": "KopoKopo",
        "environment": "sandbox",
        "is_active": false,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:40:00Z",
        "is_live": false,
        "is_sandbox": true
    }
}
```

### 5. Provider-Specific Queries

#### GET /payments/credentials/provider/{provider}/
Get credentials for a specific provider.

**Response:**
```json
{
    "id": 1,
    "provider": "kopokopo",
    "provider_display": "KopoKopo",
    "environment": "sandbox",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "is_live": false,
    "is_sandbox": true
}
```

## Code Examples

### Create Payment Credentials

=== "cURL"
    ```bash
    # Login to get JWT token
    TOKEN=$(curl -s -X POST http://localhost:8000/users/login/ \
      -H "Content-Type: application/json" \
      -d '{"username": "your_username", "password": "your_password"}' \
      | jq -r '.access_token')

    # Create Kopokopo credentials
    curl -X POST http://localhost:8000/payments/credentials/ \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "provider": "kopokopo",
        "api_key": "pk_test_kopokopo_1234567890abcdef",
        "private_key": "sk_test_kopokopo_0987654321fedcba",
        "environment": "sandbox"
      }'
    ```

=== "Python"
    ```python
    import requests

    # Login to get JWT token
    login_response = requests.post('http://localhost:8000/users/login/', {
        'username': 'your_username',
        'password': 'your_password'
    })
    access_token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    # Create Kopokopo credentials
    credentials_data = {
        'provider': 'kopokopo',
        'api_key': 'pk_test_kopokopo_1234567890abcdef',
        'private_key': 'sk_test_kopokopo_0987654321fedcba',
        'environment': 'sandbox'
    }

    response = requests.post(
        'http://localhost:8000/payments/credentials/',
        json=credentials_data,
        headers=headers
    )

    if response.status_code == 201:
        credentials_id = response.json()['id']
        print(f"Credentials created with ID: {credentials_id}")
    ```

=== "JavaScript"
    ```javascript
    // Login to get JWT token
    const loginResponse = await fetch('http://localhost:8000/users/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: 'your_username',
            password: 'your_password'
        })
    });

    const { access_token } = await loginResponse.json();
    const headers = {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json'
    };

    // Create InstaSend credentials
    const credentialsData = {
        provider: 'instasend',
        api_key: 'pk_test_instasend_1234567890abcdef',
        private_key: 'sk_test_instasend_0987654321fedcba',
        environment: 'sandbox'
    };

    const response = await fetch('http://localhost:8000/payments/credentials/', {
        method: 'POST',
        headers,
        body: JSON.stringify(credentialsData)
    });

    if (response.ok) {
        const credentials = await response.json();
        console.log(`Credentials created with ID: ${credentials.id}`);
    }
    ```

### List Payment Credentials

=== "cURL"
    ```bash
    curl -X GET http://localhost:8000/payments/credentials/ \
      -H "Authorization: Bearer $TOKEN"
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>"
    }

    response = requests.get(
        "http://localhost:8000/payments/credentials/",
        headers=headers
    )

    credentials = response.json()
    print(f"Found {len(credentials)} payment credentials")
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/payments/credentials/', {
        headers: {
            'Authorization': 'Bearer <your_jwt_token>'
        }
    });

    const credentials = await response.json();
    console.log(`Found ${credentials.length} payment credentials`);
    ```

### Get Credentials by Provider

=== "cURL"
    ```bash
    curl -X GET http://localhost:8000/payments/credentials/provider/kopokopo/ \
      -H "Authorization: Bearer $TOKEN"
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>"
    }

    response = requests.get(
        "http://localhost:8000/payments/credentials/provider/kopokopo/",
        headers=headers
    )

    credentials = response.json()
    print(f"Provider: {credentials['provider_display']}")
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/payments/credentials/provider/kopokopo/', {
        headers: {
            'Authorization': 'Bearer <your_jwt_token>'
        }
    });

    const credentials = await response.json();
    console.log(`Provider: ${credentials.provider_display}`);
    ```

### Update Private Key

=== "cURL"
    ```bash
    curl -X POST http://localhost:8000/payments/credentials/1/update-private-key/ \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "private_key": "sk_test_kopokopo_new_private_key_12345"
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
        "private_key": "sk_test_kopokopo_new_private_key_12345"
    }

    response = requests.post(
        "http://localhost:8000/payments/credentials/1/update-private-key/",
        headers=headers,
        json=data
    )

    result = response.json()
    print(f"Update message: {result['message']}")
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/payments/credentials/1/update-private-key/', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer <your_jwt_token>',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            private_key: 'sk_test_kopokopo_new_private_key_12345'
        })
    });

    const result = await response.json();
    console.log(`Update message: ${result.message}`);
    ```

### Verify Credentials

=== "cURL"
    ```bash
    curl -X POST http://localhost:8000/payments/credentials/1/verify/ \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "private_key": "sk_test_kopokopo_0987654321fedcba"
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
        "private_key": "sk_test_kopokopo_0987654321fedcba"
    }

    response = requests.post(
        "http://localhost:8000/payments/credentials/1/verify/",
        headers=headers,
        json=data
    )

    result = response.json()
    print(f"Verification result: {result['is_valid']}")
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/payments/credentials/1/verify/', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer <your_jwt_token>',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            private_key: 'sk_test_kopokopo_0987654321fedcba'
        })
    });

    const result = await response.json();
    console.log(`Verification result: ${result.is_valid}`);
    ```

### Get Decrypted Private Key

=== "cURL"
    ```bash
    curl -X GET http://localhost:8000/payments/credentials/1/get-private-key/ \
      -H "Authorization: Bearer $TOKEN"
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>"
    }

    response = requests.get(
        "http://localhost:8000/payments/credentials/1/get-private-key/",
        headers=headers
    )

    result = response.json()
    print(f"Private key: {result['private_key']}")
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/payments/credentials/1/get-private-key/', {
        headers: {
            'Authorization': 'Bearer <your_jwt_token>'
        }
    });

    const result = await response.json();
    console.log(`Private key: ${result.private_key}`);
    ```

### Toggle Credentials Status

=== "cURL"
    ```bash
    curl -X POST http://localhost:8000/payments/credentials/1/toggle-status/ \
      -H "Authorization: Bearer $TOKEN"
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>"
    }

    response = requests.post(
        "http://localhost:8000/payments/credentials/1/toggle-status/",
        headers=headers
    )

    result = response.json()
    print(f"Status message: {result['message']}")
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/payments/credentials/1/toggle-status/', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer <your_jwt_token>'
        }
    });

    const result = await response.json();
    console.log(`Status message: ${result.message}`);
    ```

### Update Credentials

=== "cURL"
    ```bash
    curl -X PUT http://localhost:8000/payments/credentials/1/ \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "api_key": "pk_test_kopokopo_new_key_12345",
        "environment": "live"
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
        "api_key": "pk_test_kopokopo_new_key_12345",
        "environment": "live"
    }

    response = requests.put(
        "http://localhost:8000/payments/credentials/1/",
        headers=headers,
        json=data
    )

    result = response.json()
    print(f"Updated environment: {result['environment']}")
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/payments/credentials/1/', {
        method: 'PUT',
        headers: {
            'Authorization': 'Bearer <your_jwt_token>',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            api_key: 'pk_test_kopokopo_new_key_12345',
            environment: 'live'
        })
    });

    const result = await response.json();
    console.log(`Updated environment: ${result.environment}`);
    ```

### Delete Credentials

=== "cURL"
    ```bash
    curl -X DELETE http://localhost:8000/payments/credentials/1/ \
      -H "Authorization: Bearer $TOKEN"
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>"
    }

    response = requests.delete(
        "http://localhost:8000/payments/credentials/1/",
        headers=headers
    )

    result = response.json()
    print(f"Delete message: {result['message']}")
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/payments/credentials/1/', {
        method: 'DELETE',
        headers: {
            'Authorization': 'Bearer <your_jwt_token>'
        }
    });

    const result = await response.json();
    console.log(`Delete message: ${result.message}`);
    ```

## Security Features

### Encryption
- Private keys are encrypted using Fernet (symmetric encryption)
- Uses the project's `ENCRYPTION_KEY` from settings
- Encryption happens automatically when saving

### Verification
- Private key hash is stored for verification
- Hash is SHA-256 for security
- Verification doesn't require decryption

### Access Control
- Users can only access their own credentials
- JWT authentication required for all endpoints
- Admin interface restricted to superusers

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
    "error": "Private key must be at least 10 characters long"
}
```

**404 Not Found:**
```json
{
    "error": "Payment credentials not found or access denied"
}
```

**500 Internal Server Error:**
```json
{
    "error": "Failed to decrypt private key: Invalid token"
}
```

## Database Schema

The `PaymentCredentials` model includes:

- `user`: Foreign key to User model
- `provider`: Choice between 'kopokopo' and 'instasend'
- `api_key`: Public API key (stored as plain text)
- `encrypted_private_key`: Encrypted private key (BinaryField)
- `private_key_hash`: SHA-256 hash for verification
- `environment`: 'sandbox' or 'live'
- `is_active`: Boolean status flag
- `created_at` and `updated_at`: Timestamps

## Testing

Use the provided test script to verify functionality:

```bash
python test_payment_credentials.py
```

This script tests all endpoints and demonstrates the complete workflow for managing payment credentials.
