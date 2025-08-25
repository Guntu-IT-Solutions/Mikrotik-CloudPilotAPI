# Package Management

This document provides comprehensive information about the Package management system for WiFi internet packages.

## Overview

The Package system allows you to create and manage different WiFi internet packages for each router. Each package defines:

- **Duration**: How long the package is valid (hourly or monthly)
- **Speed Limits**: Separate download and upload bandwidth limits
- **Pricing**: Cost in Kenyan Shillings (KES)
- **Router Association**: Which router the package applies to

## Package Model

### Core Fields

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

#### Hourly Packages
- **Duration**: 1-24 hours
- **Use Case**: Short-term access, pay-per-use
- **Example**: 1 hour at 10 Mbps for KES 2.50

#### Monthly Packages
- **Duration**: 30 days (720 hours)
- **Use Case**: Long-term subscriptions
- **Example**: 1 month at 100 Mbps for KES 150.00

### Speed Limits

#### Download Speed
- **Field**: `download_speed_mbps`
- **Unit**: Megabits per second (Mbps)
- **Range**: 1 Mbps to 10,000+ Mbps
- **Display**: Automatically converts to Gbps for high speeds

#### Upload Speed
- **Field**: `upload_speed_mbps`
- **Unit**: Megabits per second (Mbps)
- **Range**: 1 Mbps to 10,000+ Mbps
- **Display**: Automatically converts to Gbps for high speeds

#### Combined Display
The system automatically generates human-readable speed displays:
- **Low Speed**: "10 Mbps / 5 Mbps"
- **High Speed**: "1.0 Gbps / 500 Mbps"

### Validation Rules

#### Package Name
- **Uniqueness**: Must be unique per router
- **Length**: Maximum 100 characters
- **Format**: Human-readable names (e.g., "Basic Hourly", "Premium Monthly")

#### Duration
- **Minimum**: 1 hour
- **Maximum**: No upper limit (practical limit around 8760 hours = 1 year)
- **Calculation**: Monthly packages use 720 hours (30 days × 24 hours)

#### Pricing
- **Minimum**: KES 0.01
- **Currency**: Kenyan Shillings (KES)
- **Decimal Places**: 2 decimal places supported

#### Speed Limits
- **Minimum**: 1 Mbps
- **Maximum**: No upper limit (practical limit around 10,000 Mbps)
- **Symmetry**: Download and upload can be different

## Admin Interface

### Package Admin Features

#### List Display
- Package name and router
- Package type and duration
- Price and speed limits
- Active status and creation date

#### Filtering Options
- By router
- By package type (hourly/monthly)
- By active status
- By creation/update dates

#### Search Capabilities
- Package name
- Description
- Router name

#### Field Organization
1. **Basic Information**: Name, router, type, description, status
2. **Package Details**: Duration, price
3. **Speed Limits**: Download/upload speeds with display properties
4. **Metadata**: Creation/update timestamps

### Admin Actions

#### Create Package
1. Navigate to **Routers > Packages**
2. Click **Add Package**
3. Fill in required fields:
   - **Name**: Unique package name
   - **Router**: Select from available routers
   - **Type**: Hourly or Monthly
   - **Duration**: Hours (1 for hourly, 720 for monthly)
   - **Price**: Amount in KES
   - **Speeds**: Download and upload limits
   - **Description**: Optional details
4. Click **Save**

#### Edit Package
1. Find the package in the list
2. Click on the package name
3. Modify desired fields
4. Click **Save**

#### Deactivate Package
1. Edit the package
2. Uncheck **Is Active**
3. Save changes

**Note**: Deactivating a package prevents new purchases but doesn't affect existing active subscriptions.

## Business Logic

### Package Lifecycle

#### Creation
1. **Setup**: Admin creates package with router association
2. **Configuration**: Set duration, pricing, and speed limits
3. **Activation**: Mark package as active for customer purchase

#### Active Period
1. **Available**: Customers can see and purchase the package
2. **Purchased**: Payment creates a Payment record
3. **Active**: Customer has internet access until expiry

#### Expiry
1. **Expired**: Package access ends automatically
2. **Renewal**: Customer can purchase the same or different package

### Speed Management

#### Bandwidth Control
- **Download Limit**: Controls how fast customers can download
- **Upload Limit**: Controls how fast customers can upload
- **Asymmetric**: Common to have higher download than upload speeds

#### Speed Examples
- **Basic**: 10 Mbps down / 5 Mbps up
- **Standard**: 25 Mbps down / 10 Mbps up
- **Premium**: 100 Mbps down / 50 Mbps up
- **Ultra**: 1 Gbps down / 500 Mbps up

### Pricing Strategy

#### Hourly Packages
- **Target**: Casual users, short-term access
- **Pricing**: Higher per-hour cost
- **Example**: 1 hour at 10 Mbps for KES 2.50

#### Monthly Packages
- **Target**: Regular users, long-term access
- **Pricing**: Lower per-hour cost
- **Example**: 720 hours at 100 Mbps for KES 150.00

## API Endpoints

### Overview

The Package system provides API endpoints for retrieving package information. All endpoints require JWT authentication and provide user-specific data access.

### Authentication

All package endpoints require authentication using JWT tokens:

```http
Authorization: Bearer <your_jwt_token>
```

**How to get JWT tokens:**
1. **Username/Password**: `POST /users/login/`
2. **API Keys**: `POST /users/api-key-login/` (requires both public and private keys)

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| **GET** | `/routers/{id}/packages/` | Get packages for a specific router |
| **GET** | `/routers/packages/` | List all packages from user's routers |
| **POST** | `/routers/packages/` | Create a new package |
| **GET** | `/routers/packages/{id}/` | Get package details |
| **PUT** | `/routers/packages/{id}/` | Update package configuration |
| **DELETE** | `/routers/packages/{id}/` | Delete a package |

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

**Error Response (404 Not Found):**
```json
{
    "error": "Router not found or access denied"
}
```

**Error Response (401 Unauthorized):**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### Package CRUD Operations

#### List/Create Packages
```http
GET/POST /routers/packages/
```

#### Description
**GET**: List all packages from routers owned by the authenticated user
**POST**: Create a new package for a router owned by the user

#### Request Headers
```http
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

#### POST Request Body
```json
{
    "name": "Basic Hourly",
    "router": 1,
    "package_type": "hourly",
    "duration_hours": 1,
    "price": "2.50",
    "download_speed_mbps": 10,
    "upload_speed_mbps": 5,
    "description": "Basic internet access for 1 hour",
    "is_active": true
}
```

#### Response Format

**GET Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Basic Hourly",
        "router": 1,
        "router_name": "Office Router",
        "package_type": "hourly",
        "package_type_display": "Hourly Package",
        "duration_hours": 1,
        "duration_display": "1 hour",
        "price": "2.50",
        "download_speed_mbps": 10,
        "upload_speed_mbps": 5,
        "download_speed_display": "10 Mbps",
        "upload_speed_display": "5 Mbps",
        "speed_display": "10 Mbps / 5 Mbps",
        "description": "Basic internet access for 1 hour",
        "is_active": true,
        "created_at": "2025-08-13T13:19:26Z",
        "updated_at": "2025-08-13T13:19:26Z"
    }
]
```

**POST Success Response (201 Created):**
```json
{
    "id": 2,
    "name": "Premium Monthly",
    "router": 1,
    "router_name": "Office Router",
    "package_type": "monthly",
    "package_type_display": "Monthly Package",
    "duration_hours": 720,
    "duration_display": "1 month",
    "price": "150.00",
    "download_speed_mbps": 100,
    "upload_speed_mbps": 50,
    "download_speed_display": "100 Mbps",
    "upload_speed_display": "50 Mbps",
    "speed_display": "100 Mbps / 50 Mbps",
    "description": "High-speed internet for 1 month",
    "is_active": true,
    "created_at": "2025-08-13T14:30:00Z",
    "updated_at": "2025-08-13T14:30:00Z"
}
```

**POST Error Response (400 Bad Request):**
```json
{
    "name": [
        "A package with name 'Basic Hourly' already exists for this router."
    ],
    "price": [
        "Price must be greater than 0."
    ]
}
```

#### Package Details
```http
GET/PUT/DELETE /routers/packages/{id}/
```

#### Description
**GET**: Get package details
**PUT**: Update package configuration
**DELETE**: Remove package

#### Path Parameters
- `id` (integer, required): Package ID to operate on

#### PUT Request Body
```json
{
    "name": "Updated Package Name",
    "price": "3.00",
    "download_speed_mbps": 15,
    "upload_speed_mbps": 8,
    "description": "Updated package description"
}
```

#### Response Format

**GET Response (200 OK):**
```json
{
    "id": 1,
    "name": "Basic Hourly",
    "router": 1,
    "router_name": "Office Router",
    "package_type": "hourly",
    "package_type_display": "Hourly Package",
    "duration_hours": 1,
    "duration_display": "1 hour",
    "price": "2.50",
    "download_speed_mbps": 10,
    "upload_speed_mbps": 5,
    "download_speed_display": "10 Mbps",
    "upload_speed_display": "5 Mbps",
    "speed_display": "10 Mbps / 5 Mbps",
    "description": "Basic internet access for 1 hour",
    "is_active": true,
    "created_at": "2025-08-13T13:19:26Z",
    "updated_at": "2025-08-13T13:19:26Z"
}
```

**PUT Response (200 OK):**
```json
{
    "id": 1,
    "name": "Updated Package Name",
    "router": 1,
    "router_name": "Office Router",
    "package_type": "hourly",
    "package_type_display": "Hourly Package",
    "duration_hours": 1,
    "duration_display": "1 hour",
    "price": "3.00",
    "download_speed_mbps": 15,
    "upload_speed_mbps": 8,
    "download_speed_display": "15 Mbps",
    "upload_speed_display": "8 Mbps",
    "speed_display": "15 Mbps / 8 Mbps",
    "description": "Updated package description",
    "is_active": true,
    "created_at": "2025-08-13T13:19:26Z",
    "updated_at": "2025-08-13T14:45:00Z"
}
```

**DELETE Response (200 OK):**
```json
{
    "message": "Package \"Updated Package Name\" has been successfully deleted"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `router_id` | integer | ID of the router |
| `router_name` | string | Name of the router |
| `packages` | array | Array of package objects |
| `message` | string | Summary message |

#### Package Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique package identifier |
| `name` | string | Package name |
| `package_type` | string | Package type (hourly/monthly) |
| `package_type_display` | string | Human-readable package type |
| `duration_hours` | integer | Duration in hours |
| `duration_display` | string | Human-readable duration |
| `price` | string | Price in KES (decimal as string) |
| `currency` | string | Currency code (KES) |
| `download_speed_mbps` | integer | Download speed limit in Mbps |
| `upload_speed_mbps` | integer | Upload speed limit in Mbps |
| `download_speed_display` | string | Human-readable download speed |
| `upload_speed_display` | string | Human-readable upload speed |
| `speed_display` | string | Combined speed display |
| `description` | string | Package description |
| `is_active` | boolean | Whether package is available |

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
        
        for package in packages['packages']:
            print(f"- {package['name']}: {package['speed_display']} for {package['duration_display']} at {package['price']} {package['currency']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
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
        
        packages.packages.forEach(package => {
            console.log(`- ${package.name}: ${package.speed_display} for ${package.duration_display} at ${package.price} ${package.currency}`);
        });
    } else {
        const error = await response.json();
        console.error(`Error: ${response.status}`, error);
    }
    ```

### Filter Packages by Type

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
        
        # Filter hourly packages
        hourly_packages = [p for p in packages['packages'] if p['package_type'] == 'hourly']
        print(f"Found {len(hourly_packages)} hourly packages")
        
        # Filter monthly packages
        monthly_packages = [p for p in packages['packages'] if p['package_type'] == 'monthly']
        print(f"Found {len(monthly_packages)} monthly packages")
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
        
        // Filter hourly packages
        const hourlyPackages = packages.packages.filter(p => p.package_type === 'hourly');
        console.log(`Found ${hourlyPackages.length} hourly packages`);
        
        // Filter monthly packages
        const monthlyPackages = packages.packages.filter(p => p.package_type === 'monthly');
        console.log(`Found ${monthlyPackages.length} monthly packages`);
    }
    ```

### Find Packages by Speed Range

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
        
        # Find packages with download speed >= 50 Mbps
        fast_packages = [p for p in packages['packages'] if p['download_speed_mbps'] >= 50]
        print(f"Found {len(fast_packages)} packages with 50+ Mbps download")
        
        # Find packages within price range
        affordable_packages = [p for p in packages['packages'] if float(p['price']) <= 100.0]
        print(f"Found {len(affordable_packages)} packages under KES 100")
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
        
        // Find packages with download speed >= 50 Mbps
        const fastPackages = packages.packages.filter(p => p.download_speed_mbps >= 50);
        console.log(`Found ${fastPackages.length} packages with 50+ Mbps download`);
        
        // Find packages within price range
        const affordablePackages = packages.packages.filter(p => parseFloat(p.price) <= 100.0);
        console.log(`Found ${affordablePackages.length} packages under KES 100`);
    }
    ```

### Create a New Package

=== "cURL"
    ```bash
    curl -X POST http://localhost:8000/routers/packages/ \
      -H "Authorization: Bearer <your_jwt_token>" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "Basic Hourly",
        "router": 1,
        "package_type": "hourly",
        "duration_hours": 1,
        "price": "2.50",
        "download_speed_mbps": 10,
        "upload_speed_mbps": 5,
        "description": "Basic internet access for 1 hour",
        "is_active": true
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
        "name": "Basic Hourly",
        "router": 1,
        "package_type": "hourly",
        "duration_hours": 1,
        "price": "2.50",
        "download_speed_mbps": 10,
        "upload_speed_mbps": 5,
        "description": "Basic internet access for 1 hour",
        "is_active": True
    }

    response = requests.post(
        "http://localhost:8000/routers/packages/",
        headers=headers,
        json=data
    )

    if response.status_code == 201:
        package = response.json()
        print(f"Created package: {package['name']} with ID {package['id']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/routers/packages/', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer <your_jwt_token>',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: 'Basic Hourly',
            router: 1,
            package_type: 'hourly',
            duration_hours: 1,
            price: '2.50',
            download_speed_mbps: 10,
            upload_speed_mbps: 5,
            description: 'Basic internet access for 1 hour',
            is_active: true
        })
    });

    if (response.ok) {
        const package = await response.json();
        console.log(`Created package: ${package.name} with ID ${package.id}`);
    } else {
        const error = await response.json();
        console.error(`Error: ${response.status}`, error);
    }
    ```

### Update Package Details

=== "cURL"
    ```bash
    curl -X PUT http://localhost:8000/routers/packages/1/ \
      -H "Authorization: Bearer <your_jwt_token>" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "Updated Package Name",
        "price": "3.00",
        "download_speed_mbps": 15,
        "upload_speed_mbps": 8,
        "description": "Updated package description"
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
        "name": "Updated Package Name",
        "price": "3.00",
        "download_speed_mbps": 15,
        "upload_speed_mbps": 8,
        "description": "Updated package description"
    }

    response = requests.put(
        "http://localhost:8000/routers/packages/1/",
        headers=headers,
        json=data
    )

    if response.status_code == 200:
        package = response.json()
        print(f"Updated package: {package['name']}")
        print(f"New price: {package['price']} KES")
        print(f"New speed: {package['speed_display']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/routers/packages/1/', {
        method: 'PUT',
        headers: {
            'Authorization': 'Bearer <your_jwt_token>',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: 'Updated Package Name',
            price: '3.00',
            download_speed_mbps: 15,
            upload_speed_mbps: 8,
            description: 'Updated package description'
        })
    });

    if (response.ok) {
        const package = await response.json();
        console.log(`Updated package: ${package.name}`);
        console.log(`New price: ${package.price} KES`);
        console.log(`New speed: ${package.speed_display}`);
    } else {
        const error = await response.json();
        console.error(`Error: ${response.status}`, error);
    }
    ```

### Delete a Package

=== "cURL"
    ```bash
    curl -X DELETE http://localhost:8000/routers/packages/1/ \
      -H "Authorization: Bearer <your_jwt_token>"
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>"
    }

    response = requests.delete(
        "http://localhost:8000/routers/packages/1/",
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        print(f"Delete message: {result['message']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/routers/packages/1/', {
        method: 'DELETE',
        headers: {
            'Authorization': 'Bearer <your_jwt_token>'
        }
    });

    if (response.ok) {
        const result = await response.json();
        console.log(`Delete message: ${result.message}`);
    } else {
        const error = await response.json();
        console.error(`Error: ${response.status}`, error);
    }
    ```

### List All Packages

=== "cURL"
    ```bash
    curl -X GET http://localhost:8000/routers/packages/ \
      -H "Authorization: Bearer <your_jwt_token>"
    ```

=== "Python"
    ```python
    import requests

    headers = {
        "Authorization": "Bearer <your_jwt_token>"
    }

    response = requests.get(
        "http://localhost:8000/routers/packages/",
        headers=headers
    )

    if response.status_code == 200:
        packages = response.json()
        print(f"Found {len(packages)} packages across all routers")
        
        for package in packages:
            print(f"- {package['name']} ({package['router_name']}): {package['speed_display']} for {package['duration_display']} at {package['price']} KES")
    ```

=== "JavaScript"
    ```javascript
    const response = await fetch('http://localhost:8000/routers/packages/', {
        headers: {
            'Authorization': 'Bearer <your_jwt_token>'
        }
    });

    if (response.ok) {
        const packages = await response.json();
        console.log(`Found ${packages.length} packages across all routers`);
        
        packages.forEach(package => {
            console.log(`- ${package.name} (${package.router_name}): ${package.speed_display} for ${package.duration_display} at ${package.price} KES`);
        });
    }
    ```

## Error Handling

### HTTP Status Codes

| Status | Description | Common Causes |
|--------|-------------|---------------|
| **200 OK** | Request successful | Valid request with packages found |
| **401 Unauthorized** | Authentication required | Missing or invalid JWT token |
| **404 Not Found** | Router not found | Invalid router ID or access denied |
| **500 Internal Server Error** | Server error | Database or system issues |

### Error Response Format
```json
{
    "error": "Detailed error description"
}
```

### Common Error Scenarios

#### Authentication Errors
```json
{
    "detail": "Authentication credentials were not provided."
}
```
**Solution**: Include valid JWT token in Authorization header

#### Router Not Found
```json
{
    "error": "Router not found or access denied"
}
```
**Solution**: Verify router ID and ensure user has access

#### No Packages Available
```json
{
    "router_id": 1,
    "router_name": "Office Router",
    "packages": [],
    "message": "Found 0 active packages for Office Router"
}
```
**Solution**: This is not an error - router exists but has no active packages

#### Package Validation Errors
```json
{
    "name": [
        "A package with name 'Basic Hourly' already exists for this router."
    ],
    "price": [
        "Price must be greater than 0."
    ],
    "download_speed_mbps": [
        "Download speed must be greater than 0."
    ],
    "upload_speed_mbps": [
        "Upload speed must be greater than 0."
    ],
    "duration_hours": [
        "Duration must be greater than 0."
    ]
}
```
**Solution**: Fix validation errors in the request data

#### Package Not Found
```json
{
    "error": "Package not found or access denied"
}
```
**Solution**: Verify package ID and ensure user owns the router it belongs to

#### Router Access Denied (Package Creation/Update)
```json
{
    "error": "Router not found or access denied"
}
```
**Solution**: Ensure the router ID in the request belongs to the authenticated user

## Security Features

### Access Control
- **JWT Authentication**: Secure token-based authentication
- **User Isolation**: Users can only access packages for their own routers
- **Router Validation**: Verifies router ownership before package access

### Data Protection
- **No Sensitive Data**: Package endpoints don't expose sensitive information
- **Input Validation**: All parameters are validated and sanitized
- **SQL Injection Protection**: Django ORM provides built-in protection

## Integration Examples

### Frontend Integration

#### React Component Example
```jsx
import React, { useState, useEffect } from 'react';

const PackageList = ({ routerId, token }) => {
    const [packages, setPackages] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchPackages = async () => {
            try {
                const response = await fetch(`/routers/${routerId}/packages/`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    setPackages(data.packages);
                } else {
                    setError('Failed to fetch packages');
                }
            } catch (err) {
                setError('Network error');
            } finally {
                setLoading(false);
            }
        };

        fetchPackages();
    }, [routerId, token]);

    if (loading) return <div>Loading packages...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div className="package-list">
            <h3>Available Packages</h3>
            {packages.map(package => (
                <div key={package.id} className="package-card">
                    <h4>{package.name}</h4>
                    <p>Speed: {package.speed_display}</p>
                    <p>Duration: {package.duration_display}</p>
                    <p>Price: {package.price} {package.currency}</p>
                    <p>{package.description}</p>
                </div>
            ))}
        </div>
    );
};

export default PackageList;
```

## Troubleshooting

### Common Issues

#### Empty Package List
- **Cause**: Router has no active packages
- **Solution**: Check admin interface for package status

#### Authentication Errors
- **Cause**: Expired or invalid JWT token
- **Solution**: Re-authenticate and get new token

#### Router Access Denied
- **Cause**: User doesn't own the router
- **Solution**: Verify router ownership and user permissions

### Debug Tips
1. **Check JWT Token**: Ensure token is valid and not expired
2. **Verify Router ID**: Confirm router exists and belongs to user
3. **Check Package Status**: Ensure packages are marked as active
4. **Review Logs**: Check Django logs for detailed error information

## Database Relationships

```
Package (1) ←→ (1) Router
Package (1) ←→ (N) Payment
```

#### Router Relationship
- Each package belongs to exactly one router
- Router can have multiple packages
- Package names must be unique per router

#### Payment Relationship
- Each payment references one package
- Package can have multiple payments
- Payment expiry is calculated from package duration

### Database Indexes

#### Performance Optimization
- **Router + Status**: Fast filtering by router and active status
- **Package Type + Price**: Efficient package listing
- **Created/Updated**: Time-based queries

## Best Practices

### Package Design

#### Naming Convention
- **Clear Names**: "Basic Hourly", "Premium Monthly"
- **Descriptive**: Include speed or duration hints
- **Consistent**: Use similar naming across routers

#### Speed Tiers
- **Entry Level**: 5-10 Mbps for basic browsing
- **Standard**: 25-50 Mbps for streaming and downloads
- **Premium**: 100+ Mbps for heavy usage
- **Enterprise**: 1+ Gbps for business needs

#### Pricing Strategy
- **Competitive**: Research local market rates
- **Tiered**: Higher speeds command premium prices
- **Bulk Discounts**: Monthly packages offer better value

### Router Management

#### Package Distribution
- **Even Distribution**: Offer similar packages across routers
- **Local Customization**: Adjust pricing for local markets
- **Seasonal Packages**: Special offers for peak usage periods

#### Quality Control
- **Speed Testing**: Verify actual speeds match advertised
- **Customer Feedback**: Monitor satisfaction and usage patterns
- **Regular Updates**: Adjust packages based on demand

## Troubleshooting

### Common Issues

#### Package Not Visible
- Check if package is marked as active
- Verify router association
- Ensure package hasn't expired

#### Speed Mismatch
- Confirm speed limits are set correctly
- Check router configuration
- Verify customer device capabilities

#### Pricing Errors
- Ensure price is above minimum (KES 0.01)
- Check decimal places (maximum 2)
- Verify currency is KES

### Admin Tips

#### Package Creation
- Start with basic packages and expand
- Test packages before making them active
- Monitor usage patterns for optimization

#### Maintenance
- Regularly review and update packages
- Deactivate unused packages
- Archive old packages for reference

## Support

For additional help with package management:

1. **Admin Interface**: Use the Django admin for package operations
2. **API Integration**: Use the Package API for programmatic access
3. **Database Queries**: Direct database access for complex operations
4. **Documentation**: Refer to Package API documentation for endpoints

## Related Documentation

- **[Router API](router-api.md)**: Router management and operations including package endpoints
- **[Payment Transactions](payment-transactions.md)**: Payment processing and tracking
- **[API Reference](api-reference.md)**: Complete API endpoint reference
