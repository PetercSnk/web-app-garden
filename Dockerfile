# syntax=docker/dockerfile:1

FROM python:3.11.9-slim

WORKDIR /automated-garden

COPY app ./app
COPY application.py .
COPY wsgi.py .
COPY requirements.txt .
COPY gunicorn_config.py .

RUN mkdir ./logs
VOLUME ./logs

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--config", "gunicorn_config.py", "wsgi:app"]
