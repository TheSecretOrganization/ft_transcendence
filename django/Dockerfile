FROM python:3.12.4-slim

ARG DEV
ENV DEV=${DEV}

ARG HOSTNAME
ENV HOSTNAME=${HOSTNAME}

ARG ADMIN_MAIL
ENV ADMIN_MAIL=${ADMIN_MAIL}

ARG DJANGO_SUPERUSER_USERNAME
ENV DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME}

WORKDIR /app
EXPOSE 8000
VOLUME [ "/app" ]

RUN apt update && apt upgrade -y
RUN apt install -y openssl certbot python3-certbot-nginx && apt clean

COPY conf/requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /static /etc/ssl/private /etc/ssl/certs

COPY conf/certs.sh /certs.sh
RUN chmod a+x /certs.sh
RUN /certs.sh

COPY conf/entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

RUN groupadd -r appGroup && useradd -r -g appGroup ${DJANGO_SUPERUSER_USERNAME}
RUN chown ${DJANGO_SUPERUSER_USERNAME}:appGroup /app /static /etc/ssl/private /etc/ssl/certs
USER ${DJANGO_SUPERUSER_USERNAME}

CMD [ "/entrypoint.sh" ]
