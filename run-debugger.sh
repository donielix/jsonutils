#!/bin/bash

echo "Building the container..."
echo

docker stop json-queries > /dev/null 2>&1
docker rm json-queries > /dev/null 2>&1
docker image prune --filter label=stage=builder -f > /dev/null 2>&1
docker build --force-rm -t json-queries . 2>&1 > /dev/null
echo "Attach your debugger"
docker run --rm --name test-suite \
-p 1357:1357 \
json-queries bash -c "python -m debugpy --listen 0.0.0.0:1357 --wait-for-client -m unittest -v $1 > /dev/null 2>&1"
