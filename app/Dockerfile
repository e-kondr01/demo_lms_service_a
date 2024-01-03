FROM python:3.12

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements/base.txt base.txt
COPY requirements/production.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
