# syntax=docker/dockerfile:1

FROM python:3.11.9-slim

WORKDIR /web-application

COPY web-application/* /web-application

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["gunicorn", "--config", "gunicorn_config.py" "app:app"]
