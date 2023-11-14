FROM python:3.9.18

WORKDIR /workdir

RUN apt-get update && apt-get upgrade -y
RUN pip install --upgrade pip \
    && pip install 'poetry==1.6.1'

# needed for pyvista in notebooks
RUN apt-get install libgl1-mesa-glx xvfb -y

# activate poetry and pre-commit hook
CMD poetry install \
    && poetry shell \
    && pre-commit install
