# Users Service

## Start Project
Development Mode: `docker-compose -f docker-compose-dev.yml up -d --build`

## Create Database
Development Mode: `docker-compose -f docker-compose-dev.yml run users python manage.py recreate-db`

## Lint
Development Mode: `docker-compose -f docker-compose-dev.yml run users flake8 project`

## Run Test
Development Mode: `docker-compose -f docker-compose-dev.yml run users python manage.py test`

## Run Code Coverage
Development Mode: `docker-compose -f docker-compose-dev.yml run users python manage.py cov`

## Create new DB Migrations
Development Mode: `docker-compose -f docker-compose-dev.yml run users python manage.py db migrate `

## Apply DB Migrations
Development Mode: `docker-compose -f docker-compose-dev.yml run users python manage.py db upgrade `

## Init DB Migrations (Only new projects)
Development Mode: `docker-compose -f docker-compose-dev.yml run users python manage.py db init `
