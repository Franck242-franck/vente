#!/bin/bash

echo "=== Applying migrations ==="
python manage.py migrate

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Creating superuser if not exists ==="
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); \
if not User.objects.filter(username='admin').exists(): User.objects.create_superuser('admin', 'admin@example.com', 'papaet242@@')"

echo "=== Starting Django server ==="
gunicorn gestion_produits.wsgi:application --bind 0.0.0.0:8080
