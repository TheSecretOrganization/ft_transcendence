FROM python:3.12.4-slim

RUN apt update -y && apt upgrade -y
RUN python -m pip install django
WORKDIR /app

EXPOSE 8000
VOLUME [ "/app" ]
ENTRYPOINT [ "python", "manage.py" ]
CMD [ "runserver" ]
