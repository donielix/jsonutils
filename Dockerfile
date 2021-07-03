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

# create an Ipython profile to manage default imports
RUN ipython profile create template --ipython-dir /code/.ipython && \
    echo "c.InteractiveShellApp.exec_lines = ['from jsonutils import JSONObject']" >> /code/.ipython/profile_template/ipython_config.py

RUN python -m unittest -v

# set ipython environment variable
ENV IPYTHONDIR=/code/.ipython

# command to run on container start
CMD [ "ipython", "--profile=template" ] 
