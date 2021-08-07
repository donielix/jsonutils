#!/bin/bash

docker stop json-queries || true && \
docker rm json-queries || true && \
docker image prune -f && \
docker build -t json-queries . && \
if [[ $# -eq 0 ]]
then
    echo "==== Building without volume ===="
    docker run --rm --name json-queries -it json-queries
else
    echo "==== Building with volume ===="
    echo $1
    docker run --rm --name json-queries -v $1:/mnt/$1 -it json-queries
fi