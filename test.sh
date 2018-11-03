#!/bin/bash

type=$1

watchTests() {
  docker-compose -f docker-compose-dev.yml run users ptw -cn --runner "python manage.py test"
}

test() {
  docker-compose -f docker-compose-dev.yml run users python manage.py test
}

if [[ "${type}" == "watch" ]]; then
  echo "\n"
  echo "Testing!"
  watchTests
else
  echo "\n"
  echo "Testing!"
  test
fi
