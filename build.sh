#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Build MkDocs documentation
echo "Building MkDocs documentation..."
mkdocs build

# Copy MkDocs output to Django static directory
echo "Copying documentation to Django static directory..."
cp -r site/* staticfiles/

# Collect Django static files
echo "Collecting Django static files..."
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create a super user (optional - comment out if not needed)
echo "Creating superuser..."
python manage.py createsuperuser

echo "Build complete! Documentation available at /docs/"