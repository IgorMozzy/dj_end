FROM python:3.12-slim

WORKDIR /app

COPY . /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

RUN python manage.py collectstatic --noinput

EXPOSE 8000
