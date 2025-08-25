# Mikrotik CloudPilot API

A Django-based API for managing Mikrotik routers with user authentication and secure API key management.

## 🚀 Features

- **User Management**: User registration, authentication, and profile management
- **Router Management**: CRUD operations for Mikrotik routers with encrypted passwords
- **Dual Authentication**: Both JWT tokens and dual API key (public + private) authentication
- **Mikrotik Integration**: Test connections, execute commands, and get device information
- **Secure Storage**: Router passwords encrypted using Fernet encryption

## 🏗️ Architecture

### Database Structure
- **Single Database**: All data stored in the default `db.sqlite3` database
- **Proper Relationships**: Models use Django ForeignKey relationships for data integrity
- **User Isolation**: Users can only access their own data through proper filtering

### Authentication Methods
1. **JWT Authentication**: Standard JWT tokens for user management
2. **Dual API Key Authentication**: Public + Private key pairs for router access
3. **User-Specific Access**: Users can only access their own data

## 🔧 Current Status

✅ **Completed Features:**
- Simplified single-database architecture
- Router model with encrypted passwords
- Dual authentication system (JWT + API Keys)
- Automatic API key generation on user registration
- Complete CRUD operations for routers
- Mikrotik API integration framework
- Connection testing and command execution

## 🚨 Important Notes

- **Simplified Architecture**: All data stored in a single database with proper relationships
- **Automatic Setup**: API keys are created automatically when users register
- **Standard Django Patterns**: Uses Django's built-in ForeignKey relationships

## 📖 Documentation Sections

- **[Setup Guide](docs/setup-guide.md)**: Complete installation and configuration
- **[Authentication](docs/authentication.md)**: JWT and API key authentication details
- **[Router API](docs/router-api.md)**: Complete router management API reference
- **[API Reference](docs/api-reference.md)**: Quick reference guide for API endpoints

## 🔒 Security Features

- **User Data Isolation**: Users can only access their own data through proper filtering
- **Encrypted Passwords**: Router passwords encrypted using Fernet
- **Dual API Key Authentication**: Requires both public and private keys
- **Input Validation**: Comprehensive validation and sanitization
- **JWT Authentication**: Secure token-based authentication

## 🚀 Getting Started

1. **Install dependencies**:
```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers cryptography
pip install -r requirements-docs.txt
```

2. **Generate encryption key**:
```bash
python manage.py generate_encryption_key
```

3. **Run initial setup**:
```bash
python manage.py migrate
```

4. **Start the Django server** (API at `/openapi.json`):
```bash
python manage.py runserver 8000
```

5. **Serve the documentation** (defaults to `http://127.0.0.1:8001`):
```bash
mkdocs serve -a 127.0.0.1:8001
```

## 🤝 Contributing

This project is designed with a clean, maintainable architecture. Key design principles:

- **Separation of Concerns**: Clear separation between user management and router operations
- **Simplified Architecture**: Single database with proper relationships
- **Flexible Authentication**: Support for multiple authentication methods
- **Extensible Design**: Easy to add new features and endpoints

## 📄 License

See [LICENSE](LICENSE) file for details.
