# syntax=docker/dockerfile:1

FROM python:3.11.9-slim

WORKDIR /app

COPY app /app
COPY application.py /app
COPY wsgi.py /app
COPY requirements.txt /app
COPY gunicorn_config.py /app

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--config", "gunicorn_config.py" "wsgi:app"]
