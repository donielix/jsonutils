#!/bin/bash
docker stop json-queries
docker rm json-queries
docker image prune -f
docker build -t json-queries .
docker run --name json-queries -it json-queries