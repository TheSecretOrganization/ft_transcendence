#!/bin/sh
set -e

python manage.py migrate --noinput

if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "Creating superuser..."
    (python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME) \
    || true
fi

python manage.py collectstatic --noinput

python manage.py runserver 0.0.0.0:8000
