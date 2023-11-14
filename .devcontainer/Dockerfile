FROM python:3.9.18

WORKDIR /workdir

RUN apt-get update && apt-get upgrade -y

# install docker to interact with docker socket (https://docs.docker.com/engine/install/debian/)
RUN apt-get install ca-certificates curl gnupg -y
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
RUN chmod a+r /etc/apt/keyrings/docker.gpg
RUN echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update
RUN apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

RUN pip install --upgrade pip \
    && pip install 'poetry==1.6.1'

# needed for pyvista in notebooks
RUN apt-get install libgl1-mesa-glx xvfb -y

# git stuff required for linux
RUN git config --global --add safe.directory /workdir

# activate poetry and pre-commit hook
CMD poetry install \
    && poetry shell \
    && pre-commit install
