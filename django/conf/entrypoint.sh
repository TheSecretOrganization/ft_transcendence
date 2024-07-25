#!/bin/sh

set -e

if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py migrate

if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "Creating superuser..."
    (python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL) \
    || true
fi

python manage.py collectstatic --noinput --clear

gunicorn ft_transcendence.wsgi:application --bind 0.0.0.0:8000
