FROM python:3.9

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install line-bot-sdk

RUN pip install django-allauth-bootstrap

RUN pip install -r requirements.txt

COPY . /app

