#!/bin/bash

echo "Building the container..."
echo

docker stop json-queries > /dev/null 2>&1
docker rm json-queries > /dev/null 2>&1
docker image prune --filter label=stage=builder -f > /dev/null 2>&1
docker build --force-rm -t json-queries . 2>&1 > /dev/null
docker run --rm --name test-suite json-queries python -m unittest -v

