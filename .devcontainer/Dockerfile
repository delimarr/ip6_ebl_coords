FROM python:3.9.18

WORKDIR /workdir

# pyqt6 environment variables
ENV QT_DEBUG_PLUGINS=1
ENV QT_QPA_PLATFORM=xcb

RUN apt-get update && apt-get upgrade -y

RUN pip install --upgrade pip \
    && pip install 'poetry==1.6.1'

# Install necessary libraries for pyvista
RUN apt-get install libgl1-mesa-glx xvfb -y

# Install necessary libraries for Qt and XCB
RUN apt-get install -y \
    libegl1-mesa \
    libxkbcommon0 \
    libdbus-1-3 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xinput0 \
    libxcb-xfixes0 \
    libxkbcommon-x11-0 \
    libfontconfig1 \
    libfreetype6 \
    libx11-xcb1 \
    libxi6 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libxcb-shape0

# git stuff required for linux
RUN git config --global --add safe.directory /workdir

# activate poetry and pre-commit hook
CMD poetry install \
    && poetry shell \
    && pre-commit install
