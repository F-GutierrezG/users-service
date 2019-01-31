#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z localhost 5432; do
  sleep 0.1
done

sleep 1

echo "PostgreSQL started"

gunicorn -b 0.0.0.0:5000 manage:app
