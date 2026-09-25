#!/bin/bash
# Azure App Service startup for Hub.
set -e

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py crea_schema_giacenza

exec gunicorn hub.wsgi:application \
  --bind=0.0.0.0:${PORT:-8000} \
  --workers ${GUNICORN_WORKERS:-2} \
  --timeout 600
