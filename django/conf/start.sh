#!/bin/sh
set -e

echo "Starting Django..."

if [ ! -e "/ssl/${HOSTNAME}.key" ]; then
    echo "SSL key for ${HOSTNAME} not found. Generating a new self-signed SSL certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /ssl/${HOSTNAME}.key -out /ssl/${HOSTNAME}.crt -subj "/CN=${HOSTNAME}"
    echo "SSL certificate generated and saved at /ssl/${HOSTNAME}.crt"
    chmod 644 /ssl/${HOSTNAME}.key /ssl/${HOSTNAME}.crt
    echo "Permissions set for SSL key and certificate."
else
    echo "SSL key for ${HOSTNAME} already exists. Skipping certificate generation."
fi

echo "Applying database migrations..."
python manage.py migrate --noinput
echo "Database migrations completed."

if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "Checking if superuser with username ${DJANGO_SUPERUSER_USERNAME} exists..."
    exists=$(python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists())")
    if [ "$exists" = "True" ]; then
        echo "Superuser ${DJANGO_SUPERUSER_USERNAME} already exists. Skipping creation."
    else
        echo "Superuser ${DJANGO_SUPERUSER_USERNAME} does not exist. Creating superuser..."
        (python manage.py createsuperuser \
            --noinput \
            --username $DJANGO_SUPERUSER_USERNAME \
            --email $DJANGO_SUPERUSER_EMAIL) \
        || true
        echo "Superuser ${DJANGO_SUPERUSER_USERNAME} created."
    fi
else
    echo "No superuser username provided. Skipping superuser creation."
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "Static files collected."

echo "Starting Gunicorn server with SSL..."
gunicorn --certfile=/ssl/${HOSTNAME}.crt --keyfile=/ssl/${HOSTNAME}.key ft_transcendence.wsgi:application --bind 0.0.0.0:443
