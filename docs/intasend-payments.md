# IntaSend Payment Integration

This document provides comprehensive information about the IntaSend payment integration endpoints for processing M-Pesa STK push payments and payment links.

## Overview

The IntaSend integration provides secure, real-time payment processing capabilities for WiFi packages:

- **STK Push Payments**: Direct M-Pesa mobile money payments via STK push
- **Payment Links**: Shareable payment links for customer convenience
- **Real-time Status Updates**: Check payment status and update local records
- **Secure Credentials**: Encrypted API keys with user-specific access
- **Comprehensive Tracking**: Full payment lifecycle with error handling
- **Official SDK**: Uses the official IntaSend Python SDK for reliable API integration
- **Payment Provider Tracking**: Automatically tracks whether payments are from IntaSend or KopoKopo
- **Smart Status Management**: Only calls IntaSend API when payment is still pending
- **Public Key Authentication**: Public endpoints for frontend integration without JWT tokens

### Automatic Credential Management

The IntaSend API automatically handles all credential management:

1. **Credential Retrieval**: When you call any IntaSend endpoint, the system automatically fetches your latest active IntaSend credentials from the database
2. **Private Key Decryption**: The encrypted private key is automatically decrypted using your Django encryption key
3. **Environment Detection**: The system automatically detects whether to use sandbox or live IntaSend endpoints
4. **SDK Integration**: All IntaSend API calls are automatically handled through the official SDK with proper authentication

**Benefits:**
- **Simplified Integration**: No need to pass credentials in each request
- **Enhanced Security**: Credentials are never exposed in API requests
- **Automatic Updates**: Always uses your latest credentials
- **Error Prevention**: Eliminates credential-related configuration errors
- **Reliable API**: Uses official IntaSend SDK for stable integration

## Prerequisites

### 1. IntaSend Account Setup
- Create an account at [IntaSend](https://intasend.com)
- Generate API keys (public and secret)
- Configure webhook endpoints (optional)

### 2. IntaSend SDK Installation
Install the official IntaSend Python SDK:

```bash
pip install intasend
```

Or add to your requirements:
```
intasend>=1.0.0
```

### 3. Payment Credentials
Before using IntaSend endpoints, you must add your IntaSend credentials to the system:

```http
POST /payments/credentials/
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
    "provider": "instasend",
    "api_key": "your_public_api_key",
    "private_key": "your_secret_key",
    "environment": "sandbox"
}
```

**Note**: Once credentials are added, all IntaSend payment endpoints will automatically fetch and use them. The system automatically:
- Retrieves your latest active IntaSend credentials
- Decrypts the private key for API authentication
- Uses the appropriate environment (sandbox/live)
- Handles all credential management internally

You don't need to pass credentials in individual payment requests.

### 3. URL Configuration (Optional)

The IntaSend integration automatically generates callback, success, and failure URLs. You can customize these URLs by adding the following settings to your Django `settings.py`:

```python
# IntaSend URL Configuration
INTASEND_CALLBACK_URL = "https://yourdomain.com/payments/webhook/"
INTASEND_SUCCESS_URL_BASE = "https://yourdomain.com/payment/success/"
INTASEND_FAIL_URL_BASE = "https://yourdomain.com/payment/failed/"
```

**Note**: If you don't configure custom URLs, the system will:
1. Try to detect your domain from `django.contrib.sites` (if available)
2. Fall back to generic URLs (`https://yourdomain.com/...`)
3. You can update these URLs later in your production environment

**Important**: If you want to use automatic domain detection, add `'django.contrib.sites'` to your `INSTALLED_APPS` in `settings.py`.

### Quick Fix for Sites App Error

If you're getting the error:
```
Model class django.contrib.sites.models.Site doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS
```

**Immediate Solution**: Add these settings to your `settings.py`:
```python
# IntaSend URL Configuration (add these to avoid sites app dependency)
INTASEND_CALLBACK_URL = "https://yourdomain.com/api/payments/webhook/"
INTASEND_SUCCESS_URL_BASE = "https://yourdomain.com/payment/success/"
INTASEND_FAIL_URL_BASE = "https://yourdomain.com/payment/failed/"
```

Replace `yourdomain.com` with your actual domain. This will bypass the sites app dependency entirely.

## Authentication

All IntaSend endpoints require JWT authentication:

```http
Authorization: Bearer <your_jwt_token>
```

### Public Key Authentication

The IntaSend payment endpoints use a custom authentication system that validates requests using the user's public API key. This allows clients to initiate payments without requiring JWT authentication.

### How It Works

1. **Public API Key**: Each user has a unique 32-character hexadecimal public API key
2. **Header Authentication**: The public key is sent in the `X-Public-Key` header
3. **User Lookup**: The system looks up the user by their public key
4. **Access Control**: Only the user who owns the public key can access their payment endpoints

### Public Endpoints

The following endpoints are accessible using public key authentication:

- `POST /payments/intasend/initiate/` - Initiate STK push payment
- `POST /payments/intasend/{payment_id}/check-status/` - Check payment status
- `POST /payments/intasend/create-link/` - Create payment link

### Authentication Header

```http
X-Public-Key: c1eb9fed9dabc57f61d56c26ef3870ae
```

**Note**: The public API key should be exactly 32 characters long and contain only hexadecimal characters (0-9, a-f).

**Benefits:**
- **Frontend Ready**: Perfect for public login pages
- **No Token Management**: Simple public key authentication
- **Secure**: Public key identifies user automatically
- **Easy Integration**: Just add the header to your requests

## API Endpoints

### Overview

The IntaSend integration provides secure, real-time payment processing capabilities for WiFi packages:

- **STK Push Payments**: Direct M-Pesa mobile money payments via STK push
- **Payment Links**: Shareable payment links for customer convenience
- **Real-time Status Updates**: Check payment status and update local records
- **Secure Credentials**: Encrypted API keys with user-specific access
- **Comprehensive Tracking**: Full payment lifecycle with error handling

### Automatic Credential Management

The IntaSend API automatically handles all credential management:

1. **Credential Retrieval**: When you call any IntaSend endpoint, the system automatically fetches your latest active IntaSend credentials from the database
2. **Private Key Decryption**: The encrypted private key is automatically decrypted using your Django encryption key
3. **Environment Detection**: The system automatically detects whether to use sandbox or live IntaSend endpoints
4. **SDK Integration**: All IntaSend API calls are automatically handled through the official SDK with proper authentication

**Benefits:**
- **Simplified Integration**: No need to pass credentials in each request
- **Enhanced Security**: Credentials are never exposed in API requests
- **Automatic Updates**: Always uses your latest credentials
- **Error Prevention**: Eliminates credential-related configuration errors
- **Reliable API**: Uses official IntaSend SDK for stable integration

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| **POST** | `/payments/intasend/initiate/` | Initiate STK push payment |
| **POST** | `/payments/intasend/{id}/check-status/` | Check payment status |
| **POST** | `/payments/intasend/create-link/` | Create payment link |

### 1. Initiate STK Push Payment

#### Endpoint
```http
POST /payments/intasend/initiate/
```

#### Description
Initiates an M-Pesa STK push payment for a specific WiFi package. This endpoint:
- Creates a payment record in the database
- Validates package and router ownership
- Sends STK push to the customer's phone
- Returns payment details with IntaSend information

#### Request Body
```json
{
    "router_id": 1,
    "package_id": 2,
    "phone_number": "0712345678",
    "amount": "50.00",
    "payment_method": "mpesa",
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "ip_address": "192.168.1.100"
}
```

#### Required Fields
| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `router_id` | integer | ID of the router | Must belong to authenticated user |
| `package_id` | integer | ID of the package | Must be active and belong to router |
| `phone_number` | string | Customer phone number | East Africa format (0712345678) |
| `amount` | string | Payment amount | Must match package price exactly |

#### Optional Fields
| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `payment_method` | string | Payment method | "mpesa" |
| `mac_address` | string | Device MAC address | "" |
| `ip_address` | string | Device IP address | "" |

#### Response Format

**Success Response (201 Created):**
```json
{
    "message": "STK push initiated successfully",
    "payment": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "user": 1,
        "router": 1,
        "package": 2,
        "phone_number": "0712345678",
        "amount": "50.00",
        "currency": "KES",
        "payment_method": "mpesa",
        "payment_provider": "instasend",
        "status": "processing",
        "intasend_payment_id": "0666538f-9f84-435b-bee7-bb25f23a815f",
        "intasend_invoice_id": "Y5JJV4V",
        "intasend_state": "PENDING",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "ip_address": "192.168.1.100",
        "created_at": "2025-08-25T10:30:00Z",
        "updated_at": "2025-08-25T10:30:00Z"
    },
    "intasend": {
        "payment_id": "0666538f-9f84-435b-bee7-bb25f23a815f",
        "invoice_id": "Y5JJV4V",
        "state": "PENDING",
        "message": "STK push sent successfully"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "Amount must match package price: 25.00 KES",
    "payment_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Response (404 Not Found):**
```json
{
    "error": "No active IntaSend credentials found. Please add your IntaSend API credentials first."
}
```

### 2. Check Payment Status

#### Endpoint
```http
POST /payments/intasend/{payment_id}/check-status/
```

#### Description
Checks the current status of an IntaSend payment and updates the local payment record accordingly. This endpoint:
- Retrieves payment status from IntaSend API
- Updates local payment status based on IntaSend response
- Handles status transitions (pending → completed/failed)
- Returns updated payment information

#### Path Parameters
- `payment_id` (UUID, required): Payment ID to check status for

#### Request Body
```json
{}
```
*No request body required*

#### Response Format

**Success Response for Completed Payment (200 OK):**
```json
{
    "message": "Payment completed successfully!",
    "payment": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "completed",
        "intasend_state": "COMPLETE",
        "package_expiry_time": "2025-08-26T10:30:00Z",
        "completed_at": "2025-08-25T10:35:00Z",
        "updated_at": "2025-08-25T10:35:00Z"
    },
    "status": "completed",
    "state": "COMPLETE"
}
```

**Success Response for Pending Payment (200 OK):**
```json
{
    "message": "Payment status checked successfully",
    "payment": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "processing",
        "intasend_state": "PENDING",
        "updated_at": "2025-08-25T10:35:00Z"
    },
    "status": "processing",
    "state": "PENDING",
    "details": {
        "amount": "50.00",
        "currency": "KES",
        "provider": "M-PESA",
        "mpesa_reference": "ISL_faa26ef9-eb08-4353-b125-ec6a8f022815"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "This payment was not initiated through IntaSend"
}
```

**Error Response (404 Not Found):**
```json
{
    "error": "Payment not found or access denied"
}
```

### 3. Create Payment Link

#### Endpoint
```http
POST /payments/intasend/create-link/
```

#### Description
Creates a shareable payment link for a WiFi package. This endpoint:
- Creates a payment record in the database
- Generates a payment link via IntaSend API
- Returns the payment link for customer use
- Useful for scenarios where STK push isn't preferred

#### Request Body
```json
{
    "router_id": 1,
    "package_id": 2,
    "phone_number": "0712345678",
    "amount": "50.00",
    "payment_method": "mpesa",
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "ip_address": "192.168.1.100"
}
```

#### Response Format

**Success Response (201 Created):**
```json
{
    "message": "Payment link created successfully",
    "payment": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "pending",
        "intasend_invoice_id": "invoice_12345",
        "intasend_state": "PENDING"
    },
    "intasend": {
        "payment_url": "https://pay.intasend.com/invoice_12345",
        "invoice_id": "invoice_12345",
        "state": "PENDING"
    }
}
```

## Usage Examples

### Initiate STK Push Payment

=== "cURL"
    ```bash
    curl -X POST http://localhost:8000/payments/intasend/initiate/ \
      -H "Authorization: Bearer <your_jwt_token>" \
      -H "Content-Type: application/json" \
      -d '{
        "router_id": 1,
        "package_id": 2,
        "phone_number": "0712345678",
        "amount": "50.00",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "ip_address": "192.168.1.100"
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
        "router_id": 1,
        "package_id": 2,
        "phone_number": "0712345678",
        "amount": "50.00",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "ip_address": "192.168.1.100"
    }

    response = requests.post(
        "http://localhost:8000/payments/intasend/initiate/",
        headers=headers,
        json=data
    )

    if response.status_code == 201:
        result = response.json()
        print(f"STK push initiated: {result['message']}")
        print(f"Payment ID: {result['payment']['id']}")
        print(f"IntaSend ID: {result['intasend']['payment_id']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/payments/intasend/initiate/', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer <your_jwt_token>',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            router_id: 1,
            package_id: 2,
            phone_number: '0712345678',
            amount: '50.00',
            mac_address: 'AA:BB:CC:DD:EE:FF',
            ip_address: '192.168.1.100'
        })
    });

    if (response.ok) {
        const result = await response.json();
        console.log(`STK push initiated: ${result.message}`);
        console.log(`Payment ID: ${result.payment.id}`);
        console.log(`IntaSend ID: ${result.intasend.payment_id}`);
    } else {
        const error = await response.json();
        console.error(`Error: ${response.status}`, error);
    }
    ```

### Check Payment Status

=== "cURL"
    ```bash
    curl -X POST http://localhost:8000/api/payments/intasend/550e8400-e29b-41d4-a716-446655440000/check-status/ \
      -H "Authorization: Bearer <your_jwt_token>"
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>"
    }

    payment_id = "550e8400-e29b-41d4-a716-446655440000"
    
    response = requests.post(
        f"http://localhost:8000/api/payments/intasend/{payment_id}/check-status/",
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result['payment']['status']}")
        print(f"IntaSend State: {result['intasend_status']['state']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
    ```

=== "JavaScript"
    ```javascript
    const paymentId = '550e8400-e29b-41d4-a716-446655440000';
    
    const response = await fetch(`http://localhost:8000/api/payments/intasend/${paymentId}/check-status/`, {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer <your_jwt_token>'
        }
    });

    if (response.ok) {
        const result = await response.json();
        console.log(`Status: ${result.payment.status}`);
        console.log(`IntaSend State: ${result.intasend_status.state}`);
    } else {
        const error = await response.json();
        console.error(`Error: ${response.status}`, error);
    }
    ```

### Create Payment Link

=== "cURL"
    ```bash
    curl -X POST http://localhost:8000/api/payments/intasend/create-link/ \
      -H "Authorization: Bearer <your_jwt_token>" \
      -H "Content-Type: application/json" \
      -d '{
        "router_id": 1,
        "package_id": 2,
        "phone_number": "0712345678",
        "amount": "50.00"
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
        "router_id": 1,
        "package_id": 2,
        "phone_number": "0712345678",
        "amount": "50.00"
    }

    response = requests.post(
        "http://localhost:8000/api/payments/intasend/create-link/",
        headers=headers,
        json=data
    )

    if response.status_code == 201:
        result = response.json()
        print(f"Payment link created: {result['intasend']['payment_url']}")
        print(f"Invoice ID: {result['intasend']['invoice_id']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
    ```

## Payment Flow

### 1. STK Push Payment Flow
```
Customer Request → Create Payment → Initiate STK Push → Customer Receives STK → 
Payment Processing → Status Update → Package Activation
```

### 2. Payment Link Flow
```
Create Payment → Generate Link → Share with Customer → Customer Clicks Link → 
Payment Processing → Webhook/Callback → Status Update → Package Activation
```

## Status Management

### Payment Status Transitions
- **pending** → **processing** (STK push sent)
- **processing** → **completed** (payment successful)
- **processing** → **failed** (payment failed/cancelled)

### IntaSend State Mapping
- **PENDING**: Payment initiated, waiting for customer action
- **PROCESSING**: Payment being processed
- **COMPLETE**: Payment successful (IntaSend uses "COMPLETE", not "COMPLETED")
- **FAILED**: Payment failed
- **CANCELLED**: Payment cancelled by customer

### Smart Status Management
The system intelligently manages payment status updates:

1. **Completed Payments**: Returns simplified success response with package expiry time
2. **Pending Payments**: Returns detailed response with current status and IntaSend details
3. **API Efficiency**: Only calls IntaSend API when payment is still pending/processing
4. **Automatic Updates**: Updates local payment record with IntaSend state changes
5. **Package Activation**: Automatically calculates package expiry time for completed payments

## Payment Provider Tracking

### Automatic Provider Detection
The system automatically tracks which payment provider was used for each transaction:

- **IntaSend Payments**: Automatically set `payment_provider = 'instasend'`
- **KopoKopo Payments**: Can be set to `payment_provider = 'kopokopo'` (future implementation)
- **Provider Validation**: Status checks verify the payment was initiated through the correct provider

### Database Fields
Each payment record includes:

| Field | Description | Example |
|-------|-------------|---------|
| `payment_provider` | Payment provider used | `"instasend"` |
| `intasend_payment_id` | IntaSend payment reference | `"0666538f-9f84-435b-bee7-bb25f23a815f"` |
| `intasend_invoice_id` | IntaSend invoice reference | `"Y5JJV4V"` |
| `intasend_state` | Current IntaSend state | `"COMPLETE"`, `"PENDING"`, `"FAILED"` |

### Benefits
- **Provider Isolation**: Prevents cross-provider status checks
- **Audit Trail**: Clear tracking of which provider processed each payment
- **Future Expansion**: Easy to add support for additional payment providers
- **Data Integrity**: Ensures payment data consistency across providers

## Error Handling

### Common Error Scenarios

#### Missing Credentials
```json
{
    "error": "No active IntaSend credentials found for this user"
}
```
**Solution**: Add IntaSend credentials via `/api/payments/credentials/` with `provider: "instasend"`

#### Invalid Package/Router
```json
{
    "error": "Package not found or not active for this router"
}
```
**Solution**: Verify package ID and ensure it's active for the specified router

#### Amount Mismatch
```json
{
    "error": "Amount must match package price: 25.00 KES"
}
```
**Solution**: Use the exact package price amount

#### Phone Number Format
```json
{
    "error": "Invalid phone number format"
}
```
**Solution**: Use East Africa format (0712345678, 254712345678, etc.)

#### Credential Decryption Issues
```json
{
    "error": "Failed to decrypt private key: Invalid encryption key"
}
```
**Solution**: Check if your encryption key is properly configured in Django settings

## Troubleshooting

### STK Push Not Received
1. **Check Credentials**: Verify IntaSend API keys are correct
2. **Phone Number**: Ensure phone number is in correct format
3. **Network**: Check if customer has network coverage
4. **Safaricom**: Verify customer has M-Pesa account

### Payment Status Not Updating
1. **API Keys**: Check if credentials are active
2. **Webhooks**: Verify webhook URLs are accessible
3. **Manual Check**: Use status check endpoint
4. **IntaSend Dashboard**: Check payment status in IntaSend portal
5. **State Values**: IntaSend uses "COMPLETE" (not "COMPLETED")
6. **Provider Validation**: Ensure payment was initiated through IntaSend

### Common Issues

#### IntaSend State Mismatch
**Problem**: Payment shows as "processing" even when IntaSend shows "COMPLETE"

**Solution**: The system now correctly handles IntaSend's "COMPLETE" state value. Check that:
- Payment has `payment_provider = 'instasend'`
- Both `intasend_payment_id` and `intasend_invoice_id` are populated
- Status check endpoint is being used correctly

#### Payment Provider Errors
**Problem**: "This payment was not initiated through IntaSend" error

**Solution**: Ensure the payment record has:
- `payment_provider = 'instasend'`
- Valid IntaSend credentials in the database
- Payment was created using IntaSend endpoints

### Common Issues

#### Django Sites App Error
If you see this error:
```
Model class django.contrib.sites.models.Site doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS
```

**Solution**: Add `'django.contrib.sites'` to your `INSTALLED_APPS` in `settings.py`:
```python
INSTALLED_APPS = [
    # ... other apps
    'django.contrib.sites',
    # ... your apps
]
```

**Alternative**: Configure custom URLs in settings to avoid the sites dependency:
```python
INTASEND_CALLBACK_URL = "https://yourdomain.com/payments/webhook/"
INTASEND_SUCCESS_URL_BASE = "https://yourdomain.com/payment/success/"
INTASEND_FAIL_URL_BASE = "https://yourdomain.com/payment/failed/"
```

#### Sandbox vs Live Environment
- **Sandbox**: Use for testing with test phone numbers
- **Live**: Use for production with real M-Pesa accounts
- **Environment Mismatch**: Ensure credentials match the environment you're testing

#### Rate Limits
- **API Limits**: Respect IntaSend API rate limits
- **Retry Logic**: Implement exponential backoff for failed requests
- **Error Handling**: Log all API responses for debugging

## Security Features

### Access Control
- **User Isolation**: Users can only access their own payments
- **Router Ownership**: Payments must be for routers owned by the user
- **Automatic Credential Management**: API keys are automatically fetched and managed

### Data Validation
- **Package Validation**: Ensures package is active and belongs to router
- **Amount Validation**: Prevents price manipulation
- **Phone Number Formatting**: Automatic formatting for IntaSend API

### Credential Security
- **Encrypted Storage**: Private keys are encrypted using Fernet encryption
- **Automatic Decryption**: Keys are decrypted only when needed for API calls
- **Latest Credentials**: System automatically uses the most recent active credentials
- **Environment Isolation**: Sandbox and live environments are handled separately

## Integration Tips

### 1. Webhook Setup
Configure IntaSend webhooks to automatically update payment status:
- **URL**: `