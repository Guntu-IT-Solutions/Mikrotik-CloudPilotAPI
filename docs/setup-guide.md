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

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-docs.txt
```

### 4. Generate Encryption Key

Generate a secure encryption key for router passwords:

```bash
python manage.py generate_encryption_key
```

Copy the generated key and update `mikrotik_cloudpilot/settings.py`:

```python
ENCRYPTION_KEY = b'your-generated-key-here'
```

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

## Configuration

### Environment Variables

The application automatically configures:
- Single database architecture
- Encryption key for router passwords
- User authentication and isolation

### Database Architecture

- **Single Database**: All data stored in `db.sqlite3`
- **User Isolation**: Achieved through proper database filtering
- **Standard Django Patterns**: Uses Django's built-in ForeignKey relationships

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
