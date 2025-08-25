#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
echo "Installing dependencies..."
pip install -r requirements.txt

# Build MkDocs documentation
echo "Building MkDocs documentation..."
mkdocs build

# Copy MkDocs output to Django static directory
echo "Copying documentation to Django static directory..."
cp -r site/* staticfiles/

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# Create a super user
python manage.py createsuperuser