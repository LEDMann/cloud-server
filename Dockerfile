# Use the official Ubuntu 20.04 image as the base image
FROM ubuntu:20.04
ENV DEBIAN_FRONTEND noninteractive
# Update the package list and install essential packages
RUN apt-get update -y && \
    apt-get install -y \
    python3.8 \
    python3-pip \
    libasound-dev \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    python3-dev \
    python3-pyaudio \
    libsndfile1-dev \
    gcc

# Create a directory for your application (you can modify the path)
WORKDIR /app

# Copy your Python application code into the container
COPY . /app

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Replace with your application's command
CMD [ "python3", "server.py" ]
