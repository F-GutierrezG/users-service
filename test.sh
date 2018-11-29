#!/bin/bash

type=$1

watchTests() {
  docker container exec users ptw -cn --runner "python manage.py test"
}

test() {
  docker container exec users python manage.py test
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
