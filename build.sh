#!/bin/bash

echo "Building the container..."
echo
docker stop json-queries > /dev/null 2>&1 || true && \
docker rm json-queries > /dev/null 2>&1 || true && \
docker image prune --filter label=stage=builder -f > /dev/null 2>&1 && \
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