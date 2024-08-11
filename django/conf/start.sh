#!/bin/sh
set -e

openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /ssl/${HOSTNAME}.key -out /ssl/${HOSTNAME}.crt -subj "/CN=${HOSTNAME}"
chmod 644 /ssl/${HOSTNAME}.key /ssl/${HOSTNAME}.crt

python manage.py migrate --noinput

if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "Checking if superuser exists..."
    exists=$(python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists())")
    if [ "$exists" = "True" ]; then
        echo "Superuser already exists. Skipping creation."
    else
        echo "Creating superuser..."
        (python manage.py createsuperuser \
            --noinput \
            --username $DJANGO_SUPERUSER_USERNAME \
            --email $DJANGO_SUPERUSER_EMAIL) \
        || true
    fi
fi

python manage.py collectstatic --noinput

gunicorn --certfile=/ssl/${HOSTNAME}.crt --keyfile=/ssl/${HOSTNAME}.key ft_transcendence.wsgi:application --bind 0.0.0.0:443
