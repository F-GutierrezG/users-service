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
docker container exec users python manage.py recreate-db
```

## Lint
```
docker container exec users flake8 project
```

## Run Test
```
docker container exec users python manage.py test
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
docker container exec users python manage.py test --file=health_test
```

## Run Code Coverage
```
docker container exec users python manage.py cov
```

## Run Shell
```
docker container exec users python flask shell
```

## Create new DB Migrations
```
docker container exec users python manage.py db migrate
```

## Apply DB Migrations
```
docker container exec users python manage.py db upgrade
<<<<<<< HEAD

=======
>>>>>>> 64e3587ca75739934a79d9820695d51aeafb72a6
```

## Init DB Migrations (Only new projects)
```
docker container exec users python manage.py db init
```
