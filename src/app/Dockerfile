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

#pillow dependencies
RUN apk --no-cache add \
    build-base \
    openssl \
    bash \
    git \
    py3-pip \
    sudo \
    freetype-dev \
    fribidi-dev \
    harfbuzz-dev \
    jpeg-dev \
    lcms2-dev \
    openjpeg-dev \
    tcl-dev \
    tiff-dev \
    tk-dev \
    zlib-dev

ADD depends /depends
RUN cd /depends \
    && ./install_webp.sh \
    && ./install_imagequant.sh \
    && ./install_raqm.sh

RUN apk add openjdk11 bash

RUN pip install psycopg2-binary

RUN pip install -r requirements.txt

RUN python3 -m pip install --upgrade Pillow pymongo

ADD . /usr/src/app
# copy project
COPY . .
