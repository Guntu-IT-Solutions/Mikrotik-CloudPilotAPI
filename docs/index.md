# Mikrotik CloudPilot API Documentation

Welcome to the comprehensive documentation for the Mikrotik CloudPilot API - a Django-based system for managing Mikrotik routers with secure user authentication and API key management.

## 🚀 Quick Start

### 1. Installation
```bash
git clone <repository-url>
cd Mikrotik-CloudPilotAPI
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-docs.txt
```

### 2. Setup
```bash
python manage.py generate_encryption_key
python manage.py migrate
```

### 3. Run
```bash
python manage.py runserver 8000
mkdocs serve -a 127.0.0.1:8001
```

## 🏗️ Architecture Overview

### Database Structure
- **Single Database**: All data stored in `db.sqlite3`
- **User Isolation**: Achieved through proper database filtering
- **Standard Django Patterns**: Uses Django's built-in ForeignKey relationships

### Authentication Methods
1. **JWT Authentication**: Standard login with username/password
2. **Dual API Key Authentication**: Public + Private key pairs for router access
3. **User-Specific Access**: Users can only access their own data

### Core Components
- **User Management**: Registration, authentication, profile management
- **Router Management**: CRUD operations with encrypted passwords
- **Mikrotik Integration**: Connection testing, command execution, device info
- **API Key Management**: Automatic generation and rotation

## 📖 Documentation Sections

### [Setup Guide](setup-guide.md)
Complete installation and configuration instructions for the CloudPilot API.

**What you'll learn:**
- System requirements and prerequisites
- Step-by-step installation process
- Configuration and environment setup
- Troubleshooting common issues

### [Authentication](authentication.md)
Comprehensive guide to the dual authentication system.

**What you'll learn:**
- JWT token authentication for web applications
- Dual API key authentication for scripts and integrations
- Security best practices and key management
- Authentication flow and error handling

### [Router API](router-api.md)
Complete reference for router management operations.

**What you'll learn:**
- Router CRUD operations
- Connection testing and status monitoring
- Custom command execution on Mikrotik devices
- Device information retrieval
- Error handling and troubleshooting

### [Payment Credentials](payment-credentials.md)
Secure management of payment provider API credentials.

**What you'll learn:**
- Encrypted storage of private keys for Kopokopo and InstaSend
- Secure credential management and verification
- Environment support (sandbox/live)
- API integration patterns for payment providers

### [API Reference](api-reference.md)
Quick reference guide for all API endpoints.

**What you'll learn:**
- Complete endpoint listing with HTTP methods
- Request/response formats and examples
- Authentication requirements for each endpoint
- Common use cases and integration patterns

## 🔒 Security Features

### User Data Isolation
- **Filtered Access**: Users can only access their own data through proper database filtering
- **Authentication Required**: All endpoints require valid JWT tokens or dual API keys
- **Encrypted Storage**: Router passwords encrypted using Fernet encryption

### Authentication Security
- **Dual Key System**: Requires both public and private keys for API access
- **JWT Tokens**: Secure token-based authentication for web applications
- **Input Validation**: Comprehensive validation and sanitization of all inputs

## 🚀 Getting Started

### 1. **Setup the System**
Follow the [Setup Guide](setup-guide.md) to install and configure the API.

### 2. **Register a User**
Create your first user account to get API keys:
```bash
curl -X POST http://localhost:8000/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "email": "your_email@example.com",
    "password": "your_secure_password"
  }'
```

### 3. **Add Your First Router**
Use the generated API keys to add a Mikrotik router:
```bash
curl -X POST http://localhost:8000/routers/ \
  -H "X-API-Key: <your_public_key>" \
  -H "X-Private-Key: <your_private_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Router",
    "host": "192.168.1.1",
    "username": "admin",
    "password": "router_password"
  }'
```

### 4. **Test the Integration**
Verify your router connection and try some commands:
```bash
# Test connection
curl -X POST http://localhost:8000/routers/1/test-connection/ \
  -H "X-API-Key: <your_public_key>" \
  -H "X-Private-Key: <your_private_key>"

# Get device info
curl -X GET http://localhost:8000/routers/1/device-info/ \
  -H "X-API-Key: <your_public_key>" \
  -H "X-Private-Key: <your_private_key>"
```

## 🔧 Development

### Key Design Principles
- **Separation of Concerns**: Clear separation between user management and router operations
- **Simplified Architecture**: Single database with proper relationships
- **Flexible Authentication**: Support for multiple authentication methods
- **Extensible Design**: Easy to add new features and endpoints

### Technology Stack
- **Backend**: Django 4.2+ with Django REST Framework
- **Database**: SQLite with Django ORM
- **Authentication**: JWT + Custom dual API key system
- **Encryption**: Fernet (cryptography library)
- **Documentation**: MkDocs with Material theme

## 📚 Additional Resources

### API Testing
- Use the provided `test_router_api.py` script to test all endpoints
- Interactive API documentation available at `/openapi.json`
- Swagger UI for endpoint exploration

### Error Handling
- Comprehensive error responses with detailed messages
- HTTP status codes for different error types
- Debug mode for development troubleshooting

### Performance
- Single database connection for better performance
- Efficient querying with proper database filtering
- Optimized for small to medium-scale deployments

## 🤝 Contributing

This project is designed with maintainability in mind. Key areas for contribution:

- **API Extensions**: Add new router management features
- **Authentication**: Enhance security and add new auth methods
- **Documentation**: Improve guides and examples
- **Testing**: Add comprehensive test coverage
- **Performance**: Optimize database queries and API responses

## 📄 License

See [LICENSE](../../LICENSE) file for details. This project is licensed under the Apache License, Version 2.0.

---

**Ready to get started?** Begin with the [Setup Guide](setup-guide.md) to install and configure your CloudPilot API system.
