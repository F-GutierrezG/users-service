# Users Service
You must choose the docker-compose file depending on the desired environment and replace the `%docker-file%` placeholders on the commands above
```
Development: docker-compose-dev.yml
```

## Start Project
```
docker-compose -f %docker-file% up -d --build
```
Service is now up on http://localhost:5001, you can check the service's health on http://localhost:5001/users/health

## Create Database
```
docker-compose -f %docker-file% run users python manage.py recreate-db
```

## Lint
```
docker-compose -f %docker-file% run users flake8 project
```

## Run Test
```
docker-compose -f %docker-file% run users python manage.py test
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
```
docker-compose -f %docker-file% run users python manage.py test --file=health_test
```

## Run Code Coverage
```
docker-compose -f %docker-file% run users python manage.py cov
```

## Run Shell
```
docker-compose -f %docker-file% run users python flask shell
```

## Create new DB Migrations
```
docker-compose -f %docker-file% run users python manage.py db migrate
```

## Apply DB Migrations
```
docker-compose -f %docker-file% run users python manage.py db upgrade
```

## Init DB Migrations (Only new projects)
```
docker-compose -f %docker-file% run users python manage.py db init
```
