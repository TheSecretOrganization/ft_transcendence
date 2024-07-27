FROM python:3.12.4-slim

WORKDIR /app
EXPOSE 8000
VOLUME [ "/app" ]

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

RUN apt update && apt upgrade -y

RUN pip install --upgrade pip
COPY conf/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY conf/entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

CMD [ "/entrypoint.sh" ]
