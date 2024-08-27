# syntax=docker/dockerfile:1

FROM python:3.11.9-slim

WORKDIR /web-application

COPY web-application/* /web-application

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "app:app"]
