FROM python:3.7.1-slim

RUN apt-get update && \
    apt-get clean

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY ./src /usr/src/app

CMD ["gunicorn", "-b", "0.0.0.0:5000", "manage:app"]