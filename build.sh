docker container rm --force container
docker build -t myimage .
docker run -d --name container -e WEB_CONCURRENCY=1 -e MAX_WORKERS=1 -e ELEVATE_USERNAME=$ELEVATE_USERNAME -e ELEVATE_PASSWORD=$ELEVATE_PASSWORD -p 9000:80 myimage
