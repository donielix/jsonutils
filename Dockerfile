# each statement makes a new layer
# set base image (host OS)
FROM python:3

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -U pip && pip install -r requirements.txt

# copy the content of the local directory to the working directory
COPY . .

# create an Ipython profile to manage default imports
RUN ipython profile create template --ipython-dir /code/.ipython && \
    echo "c.InteractiveShellApp.exec_lines = \
    ['from jsonutils.base import JSONObject, \
    JSONDict, \
    JSONList, \
    JSONStr, \
    JSONFloat, \
    JSONInt, \
    JSONNull, \
    JSONBool, \
    JSONUnknown', \
    'from jsonutils.query import SingleQuery, All', \
    'from jsonutils.functions.parsers import parse_float, \
    parse_datetime, url_validator', \
    'from datetime import date, datetime', \
    'import pytz', \
    'import json', \
    'test = JSONObject.open(\'jsonutils/tests/json-schema-test.json\')' \
    ]" >> /code/.ipython/profile_template/ipython_config.py

# set ipython environment variable
ENV IPYTHONDIR=/code/.ipython

RUN python -m unittest -v; exit 0

# command to run on container start
CMD [ "ipython", "--profile=template" ] 
