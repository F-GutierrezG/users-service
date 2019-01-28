# !/bin/bash
ssh -o StrictHostKeyChecking=no ubuntu@${PRODUCTION_SERVER} "docker login -u gitlab-ci-token -p $DOCKER_TOKEN registry.gitlab.com"

ssh -o StrictHostKeyChecking=no ubuntu@${PRODUCTION_SERVER} 'docker network create --subnet=172.20.0.0/16 users-service-network'

ssh -o StrictHostKeyChecking=no ubuntu@${PRODUCTION_SERVER} 'docker container stop users'
ssh -o StrictHostKeyChecking=no ubuntu@${PRODUCTION_SERVER} 'docker container stop users-swagger'

ssh -o StrictHostKeyChecking=no ubuntu@${PRODUCTION_SERVER} 'docker container rm users'
ssh -o StrictHostKeyChecking=no ubuntu@${PRODUCTION_SERVER} 'docker container rm users-swagger'

ssh -o StrictHostKeyChecking=no ubuntu@${PRODUCTION_SERVER} 'docker image rm $(docker images registry.gitlab.com/gusisoft/onelike/users-service/users-swagger -q)'
ssh -o StrictHostKeyChecking=no ubuntu@${PRODUCTION_SERVER} 'docker image rm $(docker images registry.gitlab.com/gusisoft/onelike/users-service/users -q)'

ssh -o StrictHostKeyChecking=no ubuntu@${PRODUCTION_SERVER} "docker run -d --log-driver=awslogs --log-opt awslogs-region=us-east-2 --log-opt awslogs-group=UsersServiceSwagger --restart always -e 'API_URL=definitions/swagger.yml' --name users-swagger --network users-service-network --ip 172.20.0.3 $REGISTRY_REPO/$SWAGGER:$TAG"
ssh -o StrictHostKeyChecking=no ubuntu@${PRODUCTION_SERVER} "docker run -d --log-driver=awslogs --log-opt awslogs-region=us-east-2 --log-opt awslogs-group=UsersService --restart always -e 'FLASK_ENV=production' -e 'FLASK_APP=manage.py' -e 'APP_SETTINGS=project.config.ProductionConfig' -e 'DATABASE_URL=postgres://$DATABASE_PROD_USER:$DATABASE_PROD_PASSWORD@$DATABASE_PROD_URL:$DATABASE_PROD_PORT/$DATABASE_PROD_NAME' -e 'SECRET_KEY=$PROD_SECRET_KEY' -e 'CHANGE_PASSWORD_URL=$CHANGE_PASSWORD_URL' -e 'MAILER_SERVICE_URL=$PROD_MAILER_SERVICE_URL' --name users --network users-service-network --ip 172.20.0.2 $REGISTRY_REPO/$USERS:$TAG"

ssh -o StrictHostKeyChecking=no ubuntu@${PRODUCTION_SERVER} 'docker network connect onelike-network --ip 172.18.0.6 users'
ssh -o StrictHostKeyChecking=no ubuntu@${PRODUCTION_SERVER} 'docker network connect onelike-network --ip 172.18.0.7 users-swagger'

ssh -o StrictHostKeyChecking=no ubuntu@${PRODUCTION_SERVER} 'docker container exec users python manage.py db upgrade'
