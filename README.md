# Vector Oligo Search

Python Flask/Gunicorn web application for running a genome vector search
script.

## Running the development environment

This builds and runs the service using Flask, and mounts the current
directory as `/app` within the containter:

```shell
$ docker compose build
$ docker compose up -d
```

The running service will be avaliable at `http://localhost:5000/`.

To stop the service:

```shell
$ docker compose down
```

## Running the production environment

This builds and runs the service using Gunicorn in a self-contained
container:

```shell
$ docker build -t crispr:latest .
$ docker run --rm --name crispr --publish 127.0.0.1:5000:5000 -d crispr:latest
```

The running service will be avaliable at `http://localhost:5000/`.

To stop the service:

```shell
$ docker stop crispr
```

Alternatively, using `docker compose`:

```shell
$ docker compose -f docker-compose.prod.yml build
$ docker compose -f docker-compose.prod.yml up -d
```

To stop the service:

```shell
$ docker compose down
```

## Using the public image
The image is built from either the `main` branch or any tag. Tags are created for each release and the tag `latest` will always point to the same commit as the latest released version.

To use an image you can access it from githubs registry as follows:
```sh
docker pull ghcr.io/nbisweden/vector-oligo-search:main
```