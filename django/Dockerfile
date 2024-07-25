FROM python:3.12.4-slim

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
COPY conf/requirements.txt .
RUN pip install -r requirements.txt

COPY conf/entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

COPY conf/gunicorn.conf.py .


ENTRYPOINT ["sh", "/entrypoint.sh"]
