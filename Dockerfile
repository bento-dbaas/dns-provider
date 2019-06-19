FROM python:3.7-alpine

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY dns_provider/ /app

WORKDIR /app

EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "main:app"]
