docker container rm --force container
docker build -t myimage .
docker run -d --name container -p 9000:80 myimage
