#!/bin/bash

docker stop json-queries || true && \
docker rm json-queries || true && \
docker image prune -f && \
docker build -t json-queries . && \
docker run --name json-queries -it json-queries