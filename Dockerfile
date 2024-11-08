# syntax=docker/dockerfile:1

FROM debian:bookworm

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y python3-pip python3-venv cmake

WORKDIR /web-app-garden

RUN python3 -m venv venv

COPY app ./app
COPY application.py .
COPY wsgi.py .
COPY requirements.txt .
COPY gunicorn_config.py .
RUN mkdir ./logs

RUN venv/bin/pip install -r requirements.txt

EXPOSE 8000

CMD ["venv/bin/gunicorn", "--preload", "--config", "gunicorn_config.py", "wsgi:app"]
