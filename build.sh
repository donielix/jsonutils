#!/bin/bash

docker stop json-queries || true && \
docker rm json-queries || true && \
docker image prune -f && \
docker build -t json-queries . && \
if [[ $# -eq 0 ]]
then
    echo "==== Building without volume ===="
    echo
    docker run --rm --name json-queries -it json-queries
else
    echo "==== Building with volume ===="
    echo "mounted at /mnt$1"
    echo
    docker run --rm --name json-queries -v $1:/mnt/$1 -it json-queries
fi