# json-queries
Allow us to query json objects

# executing within docker

```docker build -t json-queries .``` This is to build the image
```docker run --name json-queries -it json-queries``` To run a container instance of the image
```docker start json-queries``` To run the container
```docker exec -it json-queries ipython --profile=template``` Open an Ipython session in a running container

# deleting docker files
```docker stop $(docker ps -a -q)``` To stop all running containers
```docker system prune```
```docker rmi $(docker images -aq)```


