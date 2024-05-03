#!/bin/sh

name=crispr
image=$name:latest

docker build -t "$image" .
docker run --rm --name "$name" --publish 127.0.0.1:5000:5000 -d "$image"

printf 'Use "docker stop %s" to stop the service\n' "$name"
