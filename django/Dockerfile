FROM python:3.12.4-slim

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
    apt install -y openssl && \
    apt clean && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY conf/start.sh /start.sh
RUN chmod a+x /start.sh && \
    groupadd -r appGroup && \
    useradd -r -g appGroup ${DJANGO_SUPERUSER_USERNAME} && \
    mkdir -p /static /ssl/ && \
    chown ${DJANGO_SUPERUSER_USERNAME}:appGroup /app /static /ssl

USER ${DJANGO_SUPERUSER_USERNAME}

CMD [ "/start.sh" ]
