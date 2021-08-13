# json-enhanced
Nowadays, communication between API infrastructures commonly uses JSON data. 

This library aims to emulate the behavior of the Django ORM, exporting such functionality to JSON objects.

# Installation

```
pip install json-enhanced
```

# Simple case of use
```
>> import jsonutils as js
   from datetime import datetime

>> json_data = js.JSONObject(
    {
        "data": [
            {
                "name": "Dan",
                "birthday": "1991-01-02 09:00:00",
                "publications": 15
            },
            {
                "name": "Mar",
                "birthday": "1991-03-02 12:30:00",
                "publications": 13
            },
            {
                "name": "Carl",
                "birthday": "1950-06-02 16:00:00",
                "publications": 36
            },
            {
                "name": "Vic",
                "birthday": "1986-07-02 16:00:00",
                "publications": None
            },
        ]
    }
)

# now we can navegate through this object by attribute accesion

>> json_data.data._1.name
    'Mar'

# or we can make queries as django's ORM

>> result = json_data.query(birthday__lt=datetime(1985,1,1))

>> result
    <QuerySet ['1950-06-02 16:00:00']>

>> result.first().parent
    {'name': 'Carl', 'birthday': '1950-06-02 16:00:00', 'publications': 36}

# retrieving the path of a node object

>> result.first().jsonpath
    data/2/

# testing environment

We have developed a Docker container with all the configuration options, modules and variables already setted up, so that you can test the behaviour of the package, just by typing:

```bash build.sh```
Then, on Ipython terminal, you can access `test` variable with some json data, or create new a JSONObject

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


