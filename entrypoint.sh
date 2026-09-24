#!/bin/sh

python manage.py collectstatic --noinput
python manage.py migrate

WORKERS=3
if [ "${DEBUG}" = "true" ]; then WORKERS=1; fi
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers $WORKERS --timeout 120
