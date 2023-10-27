FROM python:3.9.18

WORKDIR /ebl_coords

RUN apt-get update && apt-get upgrade -y
RUN pip install --upgrade pip \
    && pip install 'poetry==1.6.1'
RUN curl -sSL https://install.python-poetry.org | python3 -