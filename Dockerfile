# each statement makes a new layer
# set base image (host OS)
FROM python:3

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local directory to the working directory
COPY . .

RUN ipython profile create template --ipython-dir /code/.ipython && \
    echo "c.InteractiveShellApp.exec_lines = ['import os', 'import sys']" >> /code/.ipython/profile_template/ipython_config.py

ENV IPYTHONDIR=/code/.ipython

# command to run on container start
CMD [ "ipython", "--profile=template" ] 
