# !/bin/bash
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} "docker login -u gitlab-ci-token -p $DOCKER_TOKEN registry.gitlab.com"

ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker network create --subnet=172.20.0.0/16 users-service-network'

ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker container stop users'
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker container stop users-db'
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker container stop users-swagger'

ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker container rm users'
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker container rm users-db'
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker container rm users-swagger'

ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker image rm $(docker images registry.gitlab.com/gusisoft/onelike/users-service/users-swagger -q)'
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker image rm $(docker images registry.gitlab.com/gusisoft/onelike/users-service/users-db -q)'
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker image rm $(docker images registry.gitlab.com/gusisoft/onelike/users-service/users -q)'

ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} "docker run -d --restart always -e 'POSTGRES_USER=postgres' -e 'POSTGRES_PASSWORD=postgres' -p 5433:5432 --name users-db --network users-service-network --ip 172.20.0.4 $REGISTRY_REPO/$USERS_DB:$TAG"
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} "docker run -d --restart always -e 'API_URL=definitions/swagger.yml' --name users-swagger --network users-service-network --ip 172.20.0.3 $REGISTRY_REPO/$SWAGGER:$TAG"
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} "docker run -d --restart always -e 'FLASK_ENV=development' -e 'FLASK_APP=manage.py' -e 'APP_SETTINGS=project.config.DevelopmentConfig' -e 'DATABASE_URL=postgres://postgres:postgres@users-db:5432/users' -e 'DATABASE_TEST_URL=postgres://postgres:postgres@users-db:5432/users_test' -e 'SECRET_KEY=secret_key' -e 'MAILER_SERVICE_URL=$MAILER_SERVICE_URL' -e 'CHANGE_PASSWORD_URL=https://stage.onelike.gusisoft.cl/pages/change-password' --name users --network users-service-network --ip 172.20.0.2 $REGISTRY_REPO/$USERS:$TAG"

ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker network connect onelike-network --ip 172.18.0.6 users'
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker network connect onelike-network --ip 172.18.0.7 users-swagger'

ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker container exec users python manage.py db upgrade'
ssh -o StrictHostKeyChecking=no ubuntu@${STAGE_SERVER} 'docker container exec users python manage.py seed-db'
