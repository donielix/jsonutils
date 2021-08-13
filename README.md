# json-queries
Allow us to query json objects

# testing

We have developed a Docker container with all the configuration options, modules and initialized variables so that you can test the operation of the package, just by typing:

```bash build.sh```

# executing within docker

```docker build -t json-queries .``` To build the image
```docker run --name json-queries -it json-queries``` To run a new container instance of the image
```docker start json-queries``` To run the container, if it is stopped
```docker exec -it json-queries ipython --profile=template``` Open an Ipython session in a running container

# deleting docker files
```docker stop $(docker ps -a -q)``` To stop all running containers
```docker system prune``` To remove all stopped containers and dangling images
```docker rm json-queries```
```docker rmi $(docker images -aq)```

# utils
```docker images -a | tail -n +2 | wc -l``` Count the total number of docker images


