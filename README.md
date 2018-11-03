# Users Service

## Start Project
Development Mode
```
docker-compose -f docker-compose-dev.yml up -d --build
```
Service is now up in http://localhost:5001, you can check the service's health on http://localhost:5001/users/health

## Create Database
Development Mode
```
docker-compose -f docker-compose-dev.yml run users python manage.py recreate-db+
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

## Run a specific test file
Development Mode
```
docker-compose -f docker-compose-dev.yml run users python manage.py test --path=project/tests --file=health_test.py
```

## Run Code Coverage
Development Mode
```
docker-compose -f docker-compose-dev.yml run users python manage.py cov
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
