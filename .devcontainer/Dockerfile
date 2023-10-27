FROM python:3.9.18

WORKDIR /workdir

RUN apt-get update && apt-get upgrade -y
RUN pip install --upgrade pip \
    && pip install 'poetry==1.6.1'