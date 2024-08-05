FROM python:3.12.4-slim

ARG DJANGO_SUPERUSER_USERNAME
ENV DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME}

WORKDIR /app
EXPOSE 8000
VOLUME [ "/app" ]

RUN groupadd -r appGroup && useradd -r -g appGroup ${DJANGO_SUPERUSER_USERNAME}
RUN chown ${DJANGO_SUPERUSER_USERNAME}:appGroup /app
RUN mkdir /static
RUN chown ${DJANGO_SUPERUSER_USERNAME}:appGroup /static

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

RUN apt update && apt upgrade -y

RUN pip install --upgrade pip
COPY conf/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY conf/entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

USER ${DJANGO_SUPERUSER_USERNAME}

CMD [ "/entrypoint.sh" ]
