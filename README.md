# Mikrotik CloudPilot API

A Django-based API for managing Mikrotik routers with user authentication, secure API key management, and integrated payment processing for WiFi packages.

## 🚀 Features

- **User Management**: User registration, authentication, and profile management
- **Router Management**: CRUD operations for Mikrotik routers with encrypted passwords
- **Dual Authentication**: Both JWT tokens and dual API key (public + private) authentication
- **Mikrotik Integration**: Test connections, execute commands, and get device information
- **Secure Storage**: Router passwords encrypted using Fernet encryption
- **WiFi Package Management**: Create and manage internet packages for routers
- **Payment Integration**: IntaSend M-Pesa STK push payments for WiFi access
- **Mikrotik Login Pages**: Ready-to-use HTML pages for hotspot authentication
- **Production Ready**: Deployed on Render with automatic documentation building

## 🏗️ Architecture

### Database Structure
- **Single Database**: All data stored in the default `db.sqlite3` database
- **Proper Relationships**: Models use Django ForeignKey relationships for data integrity
- **User Isolation**: Users can only access their own data through proper filtering

### Authentication Methods
1. **JWT Authentication**: Standard JWT tokens for user management
2. **Dual API Key Authentication**: Public + Private key pairs for router access
3. **Public Key Authentication**: For payment endpoints (IntaSend integration)
4. **User-Specific Access**: Users can only access their own data

### Payment System
- **IntaSend Integration**: M-Pesa STK push payments for WiFi packages
- **Secure Credentials**: Encrypted storage of payment provider API keys
- **Package Management**: WiFi packages with duration and speed limits
- **Automatic Activation**: Package expiry management for Mikrotik access control

## 🔧 Current Status

✅ **Completed Features:**
- Simplified single-database architecture
- Router model with encrypted passwords
- Dual authentication system (JWT + API Keys)
- Automatic API key generation on user registration
- Complete CRUD operations for routers
- Mikrotik API integration framework
- Connection testing and command execution
- WiFi package management system
- IntaSend payment integration
- Mikrotik login pages (basic and enhanced)
- Production deployment on Render
- Automatic documentation building and serving

## 🚨 Important Notes

- **Simplified Architecture**: All data stored in a single database with proper relationships
- **Automatic Setup**: API keys are created automatically when users register
- **Standard Django Patterns**: Uses Django's built-in ForeignKey relationships
- **Production Ready**: Deployed at https://mikrotik-cloudpilotapi.onrender.com/
- **Documentation**: Available at https://mikrotik-cloudpilotapi.onrender.com/docs/

## 📖 Documentation Sections

- **[Setup Guide](https://mikrotik-cloudpilotapi.onrender.com/docs/setup-guide/)**: Complete installation and configuration
- **[Authentication](https://mikrotik-cloudpilotapi.onrender.com/docs/authentication/)**: JWT and API key authentication details
- **[Router API](https://mikrotik-cloudpilotapi.onrender.com/docs/router-api/)**: Complete router management API reference
- **[Package Management](https://mikrotik-cloudpilotapi.onrender.com/docs/packages/)**: WiFi package creation and management
- **[Payment Credentials](https://mikrotik-cloudpilotapi.onrender.com/docs/payment-credentials/)**: Secure payment provider integration
- **[IntaSend Integration](https://mikrotik-cloudpilotapi.onrender.com/docs/intasend-payments/)**: M-Pesa payment processing
- **[Mikrotik Integration](https://mikrotik-cloudpilotapi.onrender.com/docs/mikrotik-integration/)**: Hotspot and login page setup
- **[API Reference](https://mikrotik-cloudpilotapi.onrender.com/docs/api-reference/)**: Quick reference guide for API endpoints

## 🔒 Security Features

- **User Data Isolation**: Users can only access their own data through proper filtering
- **Encrypted Passwords**: Router passwords encrypted using Fernet
- **Dual API Key Authentication**: Requires both public and private keys
- **Input Validation**: Comprehensive validation and sanitization
- **JWT Authentication**: Secure token-based authentication
- **Encrypted Payment Credentials**: Private keys stored with encryption
- **CORS Configuration**: Proper cross-origin request handling

## 🚀 Getting Started

### Local Development

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Generate encryption key**:
```bash
python manage.py generate_encryption_key
```

3. **Run initial setup**:
```bash
python manage.py migrate
```

4. **Build documentation**:
```bash
mkdocs build
python manage.py collectstatic --noinput
```

5. **Start the Django server**:
```bash
python manage.py runserver 8000
```

6. **Access documentation**:
- Local: http://localhost:8000/docs/
- Production: https://mikrotik-cloudpilotapi.onrender.com/docs/

### Production Deployment

The application is automatically deployed on Render with:
- **Automatic builds** on git push
- **Documentation building** during deployment
- **Static file collection** and serving
- **Database migrations** on startup

## 🌐 Production URLs

- **API Base**: https://mikrotik-cloudpilotapi.onrender.com/
- **Documentation**: https://mikrotik-cloudpilotapi.onrender.com/docs/
- **Admin Panel**: https://mikrotik-cloudpilotapi.onrender.com/admin/

## 📱 Mikrotik Integration

### Login Pages
- **Basic Login**: `/payments/mikrotik-login/`
- **Enhanced Login**: `/payments/mikrotik-login-enhanced/`

### Features
- Automatic client IP/MAC detection
- Package selection interface
- M-Pesa STK push integration
- Automatic Mikrotik authentication
- Responsive design for mobile devices

## 💳 Payment Integration

### IntaSend Features
- **STK Push**: Direct M-Pesa mobile money payments
- **Payment Links**: Shareable payment URLs
- **Status Tracking**: Real-time payment status updates
- **Automatic Credentials**: Secure API key management

### Supported Payment Methods
- M-Pesa (Safaricom)
- Card payments (via IntaSend)
- Bank transfers (via IntaSend)

## 🤝 Contributing

This project is designed with a clean, maintainable architecture. Key design principles:

- **Separation of Concerns**: Clear separation between user management, router operations, and payments
- **Simplified Architecture**: Single database with proper relationships
- **Flexible Authentication**: Support for multiple authentication methods
- **Extensible Design**: Easy to add new features and endpoints
- **Production Ready**: Built-in deployment and documentation automation

## 📄 License

See [LICENSE](LICENSE) file for details.

---

**Ready to get started?** Visit our [documentation](https://mikrotik-cloudpilotapi.onrender.com/docs/) for complete setup and usage instructions.
