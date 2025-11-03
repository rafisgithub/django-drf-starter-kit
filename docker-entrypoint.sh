#!/bin/bash

# Exit on error
set -e

echo "Waiting for database..."
echo "Database is ready!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Check if database needs seeding
if [ "$AUTO_SEED" = "true" ]; then
    echo "Checking if database needs seeding..."
    NEEDS_SEED=$(python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()
from apps.user.models import User
print('0' if User.objects.exists() else '1')
")
    
    if [ "$NEEDS_SEED" = "1" ]; then
        echo "Database is empty. Running seed command..."
        python manage.py seed
    else
        echo "Database already has data. Skipping seed."
    fi
else
    echo "AUTO_SEED is disabled. Skipping seed check."
fi

echo "Starting server..."
exec "$@"