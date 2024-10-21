FROM python:3.12.4-slim

ENV PYTHONUNBUFFERED=1

ARG DJANGO_SUPERUSER_USERNAME
ENV DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME}

ARG HOSTNAME
ENV HOSTNAME=${HOSTNAME}

WORKDIR /app
EXPOSE 443
VOLUME [ "/app" ]

COPY conf/requirements.txt requirements.txt

RUN apt update && \
    apt upgrade -y && \
    apt install -y openssl coreutils gettext && \
    apt clean && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    groupadd -r appGroup && \
    useradd -r -g appGroup ${DJANGO_SUPERUSER_USERNAME} && \
    mkdir -p /static /ssl/ && \
    chown ${DJANGO_SUPERUSER_USERNAME}:appGroup /static /ssl/

USER ${DJANGO_SUPERUSER_USERNAME}

COPY --chown=${DJANGO_SUPERUSER_USERNAME}:appGroup src /app
COPY --chown=${DJANGO_SUPERUSER_USERNAME}:appGroup conf/start.sh /start.sh

RUN chmod a+x /start.sh

CMD [ "/start.sh" ]
