#!/bin/bash

docker build -t swagger -f Dockerfile .
docker container rm -f users-service-swagger
docker run -d --name users-service-swagger -p 8081:8080 -e "API_URL=definitions/users-service.yml" --rm swagger
