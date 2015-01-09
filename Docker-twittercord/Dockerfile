############################################################
# Dockerfile to build Python WSGI Application Containers
# Based on Ubuntu
############################################################

# Set the base image to Ubuntu
FROM ubuntu

# File Author / Maintainer
MAINTAINER Jonas Rosland

# Add the application resources URL
RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list

# Update the sources list
RUN apt-get update

# Install basic applications
#RUN apt-get install -y tar git curl nano wget dialog net-tools build-essential

# Install Python and Basic Python Tools
RUN apt-get install -y python python-dev python-distribute python-pip

ADD requirements.txt /app/requirements.txt

# Get pip to download and install requirements:
RUN pip install -r /app/requirements.txt

# Expose ports
EXPOSE 8080

# Copy correct default.html file
#RUN cp /app/templates/default-us.html /app/templates/default.html

# Copy the application folder inside the container
ADD default_config.py.template /app/default_config.py
ADD TwitterCord.py /app/TwitterCord.py
ADD static /app/static
ADD templates /app/templates

VOLUME /config

# Set the default directory where CMD will execute
WORKDIR /app

# Set the default command to execute
# when creating a new container
# i.e. using CherryPy to serve the application
CMD python TwitterCord.py