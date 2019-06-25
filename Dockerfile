FROM python:3.7-alpine

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY dns_provider/ /app/dns_provider

WORKDIR /app

EXPOSE 5000
CMD export FLASK_APP="dns_provider/main.py"; flask run
