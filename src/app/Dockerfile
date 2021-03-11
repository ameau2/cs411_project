FROM python:3.8.3-alpine

# set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1

# set work directory
WORKDIR /usr/src/app

# install dependencies
COPY ./requirements.txt .
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install psycopg2-binary

RUN pip install -r requirements.txt

ADD . /usr/src/app
# copy project
COPY . .
