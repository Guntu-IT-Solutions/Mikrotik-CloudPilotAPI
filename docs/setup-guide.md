# Setup Guide

This guide will walk you through setting up the Mikrotik CloudPilot API on your system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Mikrotik-CloudPilotAPI
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Set Up Environment Variables

**Important**: Environment variables contain sensitive information and should never be committed to version control.

```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

**Required Environment Variables:**

| Variable | Purpose | Generate Command |
|----------|---------|------------------|
| `SECRET_KEY` | Django cryptographic signing | `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `ENCRYPTION_KEY` | Router password encryption | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `DEBUG` | Debug mode (True/False) | Set to `True` for development |
| `ALLOWED_HOSTS` | Allowed domains | `localhost,127.0.0.1` for development |

**Optional Environment Variables:**

| Variable | Purpose | Default |
|----------|---------|---------|
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | JWT access token lifetime | `600` (10 hours) |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | JWT refresh token lifetime | `1` (1 day) |
| `JWT_SIGNING_KEY` | JWT signing key | Uses `SECRET_KEY` |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | Development defaults |
| `DATABASE_URL` | Production database | SQLite for development |

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4.1. Security Configuration

**Production Security Settings:**

For production deployments, ensure these environment variables are properly configured:

```bash
# Security Headers
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
SECURE_HSTS_SECONDS=31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# HTTPS Settings
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
CSRF_COOKIE_HTTPONLY=True

# CORS Restrictions
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
CORS_ALLOW_CREDENTIALS=True

# Host Restrictions
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
DEBUG=False
```

**Development vs Production:**

| Setting | Development | Production |
|---------|-------------|------------|
| `DEBUG` | `True` | `False` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Your domain names |
| `CORS_ALLOW_ALL_ORIGINS` | `True` | `False` |
| `SECURE_*` settings | `False` | `True` |
| `DATABASE` | SQLite | PostgreSQL/MySQL |

### 5. Generate Encryption Key

Generate a secure encryption key for router passwords:

```bash
python manage.py generate_encryption_key
```

Copy the generated key and update `mikrotik_cloudpilot/settings.py`:

```python
ENCRYPTION_KEY = b'your-generated-key-here'
```

### 6. Run Database Migrations

```bash
python manage.py migrate
```

### 7. Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

## Production Deployment

### Environment Variables for Production

Create a production `.env` file with secure settings:

```bash
# Django Core
SECRET_KEY=your_production_secret_key_here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com,www.yourdomain.com

# Security
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# HTTPS
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
CSRF_COOKIE_HTTPONLY=True

# CORS
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
CORS_ALLOW_CREDENTIALS=True

# Database
DATABASE_URL=postgresql://user:password@host:port/database

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
JWT_SIGNING_KEY=your_production_jwt_key_here

# Encryption
ENCRYPTION_KEY=your_production_encryption_key_here

# Static Files
STATIC_URL=https://yourdomain.com/static/
STATIC_ROOT=/path/to/staticfiles
```

### Deployment Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure production database
- [ ] Set secure `ALLOWED_HOSTS`
- [ ] Restrict CORS origins
- [ ] Enable HTTPS security headers
- [ ] Use strong, unique keys
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Enable rate limiting
- [ ] Configure backup strategy

## Configuration

### Environment-Based Configuration

The application uses environment variables for all configuration, making it easy to deploy across different environments:

- **Development**: Uses `.env` file with development-friendly defaults
- **Staging**: Uses environment variables with moderate security
- **Production**: Uses environment variables with maximum security

### Key Configuration Areas

#### 1. **Security Settings**
- `SECRET_KEY`: Django cryptographic operations
- `ENCRYPTION_KEY`: Router password encryption
- `DEBUG`: Application debug mode
- `ALLOWED_HOSTS`: Domain restrictions

#### 2. **Authentication & JWT**
- `JWT_ACCESS_TOKEN_LIFETIME_MINUTES`: Access token validity
- `JWT_REFRESH_TOKEN_LIFETIME_DAYS`: Refresh token validity
- `JWT_SIGNING_KEY`: JWT signature key
- `JWT_ALGORITHM`: JWT algorithm (HS256, RS256)

#### 3. **Database Configuration**
- `DATABASE_URL`: Production database connection
- `DATABASE_ENGINE`: Database backend
- `DATABASE_NAME`: Database name
- `DATABASE_USER`: Database username
- `DATABASE_PASSWORD`: Database password

#### 4. **CORS & Security Headers**
- `CORS_ALLOWED_ORIGINS`: Allowed cross-origin requests
- `SECURE_*`: HTTPS security headers
- `SESSION_COOKIE_*`: Session security settings
- `CSRF_COOKIE_*`: CSRF protection settings

### Database Architecture

- **Single Database**: All data stored in the configured database
- **User Isolation**: Achieved through proper database filtering
- **Standard Django Patterns**: Uses Django's built-in ForeignKey relationships
- **Production Ready**: Supports PostgreSQL, MySQL, and other databases

## Starting the Application

### 1. Start Django Server

```bash
python manage.py runserver 8000
```

The API will be available at `http://localhost:8000/`

### 2. Start Documentation Server

In another terminal:

```bash
mkdocs serve -a 127.0.0.1:8001
```

Documentation will be available at `http://127.0.0.1:8001/`

## Testing the Setup

### 1. Check API Health

```bash
curl http://localhost:8000/admin/
```

### 2. Register a Test User

```bash
curl -X POST http://localhost:8000/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### 3. Test Router Endpoints

Use the generated API keys to test router management:

```bash
# List routers (will be empty initially)
curl -X GET http://localhost:8000/routers/ \
  -H "X-API-Key: <your_public_key>" \
  -H "X-Private-Key: <your_private_key>"
```

## Troubleshooting

### Common Issues

#### 1. Authentication Errors

If you see authentication errors:

```bash
# Check if user exists and has API keys
python manage.py shell -c "from django.contrib.auth.models import User; from users.models import APIKey; user = User.objects.get(username='testuser'); print(f'User: {user.username}'); print(f'API Key: {user.api_key.public_key if hasattr(user, \"api_key\") else \"None\"}')"
```

#### 2. Database Errors

If you see database errors:

```bash
# Check database status
python manage.py check
python manage.py showmigrations
```

#### 3. Encryption Errors

If you see encryption errors:

```bash
# Verify encryption key is set
python manage.py shell -c "from django.conf import settings; print(f'Encryption key set: {hasattr(settings, \"ENCRYPTION_KEY\")}')"
```

### Debug Mode

Enable Django debug mode in `settings.py` for detailed error information during development:

```python
DEBUG = True
```

## Next Steps

After successful setup:

1. **Explore the API**: Use the interactive documentation at `http://127.0.0.1:8001/`
2. **Create Routers**: Add your Mikrotik routers through the API
3. **Test Connections**: Verify router connectivity
4. **Execute Commands**: Try custom commands on your routers

## Support

For additional help:

1. Check the [API Reference](api-reference.md) for endpoint details
2. Review the [Router API](router-api.md) for router-specific operations
3. Check Django logs for detailed error messages
4. Verify all dependencies are properly installed
