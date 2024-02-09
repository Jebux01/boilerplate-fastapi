FROM python:3.11.0b3-slim-buster as builder

WORKDIR /usr/src/app

RUN apt-get update \
  && apt-get clean \
  && apt-get -y install libpq-dev curl build-essential

RUN uname -a

RUN apt-get update && apt-get install -y curl apt-transport-https

COPY requirements.txt /tmp/requirements.txt

RUN pip install pip --upgrade && pip install -r /tmp/requirements.txt
RUN pwd

COPY . ./