#!/bin/sh

python manage.py collectstatic --noinput
python manage.py migrate

exec gunicorn primo.wsgi:application --bind 0.0.0.0:8000 --workers 3
