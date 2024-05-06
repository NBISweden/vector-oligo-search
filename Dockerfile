# syntax=docker/dockerfile:1.4
FROM python:3.9-slim AS base

WORKDIR /app

COPY start-script.sh start-script.sh
COPY requirements.txt requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

ARG UID=1000
ARG GID=1000
RUN groupadd -g "$GID" python && useradd -u "$UID" -g "$GID" python

EXPOSE ${APP_PORT:-5000}/tcp

FROM base AS dev

COPY requirements.dev.txt requirements.dev.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.dev.txt

USER python
CMD flask --app app.py --debug run --host 0.0.0.0 --port "${APP_PORT:-5000}"

FROM base AS prod

COPY pages pages
COPY static static
COPY CHANGELOG.md pages/changelog.md
COPY resources resources
COPY search search
COPY templates templates
COPY app.py app.py

USER python
CMD ./start-script.sh
