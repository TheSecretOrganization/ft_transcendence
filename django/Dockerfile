FROM python:3.12.4-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app
EXPOSE 8000
VOLUME [ "/app" ]

COPY conf/requirements.txt /app/
RUN pip install -r requirements.txt

# RUN python manage.py migrate
# RUN python manage.py createsuperuser

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
