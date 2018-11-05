# Users Service

## Start Project
Development Mode
```
docker-compose -f docker-compose-dev.yml up -d --build
```
Service is now up on http://localhost:5001, you can check the service's health on http://localhost:5001/users/health

## Create Database
Development Mode
```
docker-compose -f docker-compose-dev.yml run users python manage.py recreate-db
```

## Lint
Development Mode
```
docker-compose -f docker-compose-dev.yml run users flake8 project
```

## Run Test
Development Mode
```
docker-compose -f docker-compose-dev.yml run users python manage.py test
```
or
```
./test.sh
```

## Autorun test on file changes
```
./test.sh watch
```

## Run a specific test file
Development Mode
```
docker-compose -f docker-compose-dev.yml run users python manage.py test --file=health_test
```

## Run Code Coverage
Development Mode
```
docker-compose -f docker-compose-dev.yml run users python manage.py cov
```

## Run Shell
Development Mode
```
docker-compose -f docker-compose-dev.yml run users python flask shell
```

## Create new DB Migrations
Development Mode
```
docker-compose -f docker-compose-dev.yml run users python manage.py db migrate
```

## Apply DB Migrations
Development Mode
```
docker-compose -f docker-compose-dev.yml run users python manage.py db upgrade
```

## Init DB Migrations (Only new projects)
Development Mode
```
docker-compose -f docker-compose-dev.yml run users python manage.py db init
```
