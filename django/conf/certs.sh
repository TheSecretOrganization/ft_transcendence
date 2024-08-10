#!/bin/sh
set -e

if [ "${DEV}" = "True" ]
then
    echo "DEV"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/${HOSTNAME}.key -out /etc/ssl/certs/${HOSTNAME}.crt -subj "/CN=${HOSTNAME}"
else
    echo "PROD"
    certbot --nginx --non-interactive --agree-tos --email ${ADMIN_MAIL} --redirect -d ${HOSTNAME}
    cp /etc/letsencrypt/live/${HOSTNAME}/fullchain.pem /etc/ssl/certs/${HOSTNAME}.crt
    cp /etc/letsencrypt/live/${HOSTNAME}/privkey.pem /etc/ssl/private/${HOSTNAME}.key
fi
