#!/bin/bash

echo "=== Applying migrations ==="
python manage.py migrate

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Starting Django server ==="
gunicorn gestion_produits.wsgi:application --bind 0.0.0.0:$PORT


