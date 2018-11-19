# !/bin/bash
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} "docker login -u gitlab-ci-token -p $DOCKER_TOKEN registry.gitlab.com"

ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker network create users-service-network'

ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker container stop users'
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker container stop users-db'
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker container stop users-swagger'


ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker container rm users'
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker container rm users-db'
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker container rm users-swagger'

ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} "docker image rm $(docker images $REGISTRY_REPO/$SWAGGER -q)"
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} "docker image rm $(docker images $REGISTRY_REPO/$USERS_DB -q)"
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} "docker image rm $(docker images $REGISTRY_REPO/$USERS -q)"
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} "docker image rm $(docker images -f "dangling=true" -q)"

ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} "docker run -d -e 'POSTGRES_USER=postgres' -e 'POSTGRES_PASSWORD=postgres' -p 5433:5432 --name users-db --network users-service-network $REGISTRY_REPO/$USERS_DB:$TAG"
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} "docker run -d -e 'API_URL=definitions/swagger.yml' -p 8081:8080 --name users-swagger --network users-service-network $REGISTRY_REPO/$SWAGGER:$TAG"
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} "docker run -d -e 'FLASK_ENV=development' -e 'FLASK_APP=manage.py' -e 'APP_SETTINGS=project.config.DevelopmentConfig' -e 'DATABASE_URL=postgres://postgres:postgres@users-db:5432/users' -e 'DATABASE_TEST_URL=postgres://postgres:postgres@users-db:5432/users_test' -e 'SECRET_KEY=secret_key' -p 5001:5000 --name users --network users-service-network $REGISTRY_REPO/$USERS:$TAG"

ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker network connect client-network users'
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker network connect client-network users-swagger'

ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker container exec users python manage.py recreate-db'
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker container exec users python manage.py seed-db'
