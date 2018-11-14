# !/bin/bash

ssh -o StrictHostKeyChecking=no ubuntu@${DEVEL_SERVER} "docker login -u gitlab-ci-token -p $DOCKER_TOKEN registry.gitlab.com"
ssh -o StrictHostKeyChecking=no ubuntu@${DEVEL_SERVER} 'docker network create users-service-network'
ssh -o StrictHostKeyChecking=no ubuntu@${DEVEL_SERVER} 'docker container stop users users-db users-swagger'
ssh -o StrictHostKeyChecking=no ubuntu@${DEVEL_SERVER} 'docker container rm users users-db users-swagger'
ssh -o StrictHostKeyChecking=no ubuntu@${DEVEL_SERVER} "docker image rm $REGISTRY_REPO/$USERS:$TAG"
ssh -o StrictHostKeyChecking=no ubuntu@${DEVEL_SERVER} "docker image rm $REGISTRY_REPO/$USERS_DB:$TAG"
ssh -o StrictHostKeyChecking=no ubuntu@${DEVEL_SERVER} "docker image rm $REGISTRY_REPO/$SWAGGER:$TAG"
ssh -o StrictHostKeyChecking=no ubuntu@${DEVEL_SERVER} 'docker run -d -e "POSTGRES_USER=postgres" -e "POSTGRES_PASSWORD=postgres" --name users-db --network users-service-network registry.gitlab.com/gusisoft/onelike/client/users-service/users-db:devel'
ssh -o StrictHostKeyChecking=no ubuntu@${DEVEL_SERVER} 'docker run -d -e "API_URL=definitions/users-service.yml" -p 8081:8080 --name users-swagger --network users-service-network registry.gitlab.com/gusisoft/onelike/client/users-service/swagger:devel'
ssh -o StrictHostKeyChecking=no ubuntu@${DEVEL_SERVER} 'docker run -d -e "FLASK_ENV=development" -e "FLASK_APP=manage.py" -e "APP_SETTINGS=project.config.DevelopmentConfig" -e "DATABASE_URL=postgres://postgres:postgres@users-db:5432/users" -e "DATABASE_TEST_URL=postgres://postgres:postgres@users-db:5432/users_test" -e "SECRET_KEY=secret_key" -p 5001:5000 --name users --network users-service-network registry.gitlab.com/gusisoft/onelike/client/users-service/users:devel'
