#!/bin/bash

docker container rm --force elevate-container
docker build -t elevate-security-challenge .
docker run -d --name elevate-container -e WEB_CONCURRENCY=1 -e MAX_WORKERS=1 -e ELEVATE_USERNAME=$ELEVATE_USERNAME -e ELEVATE_PASSWORD=$ELEVATE_PASSWORD -p 9000:80 elevate-security-challenge
