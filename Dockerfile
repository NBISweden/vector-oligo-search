# syntax=docker/dockerfile:1.4
FROM python:3.9-slim as base

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

ARG UID=1000
ARG GID=1000
RUN groupadd -g "$GID" python && useradd -u "$UID" -g "$GID" python


FROM base as prod

COPY ./pages /app/pages
COPY ./static /app/static
COPY ./CHANGELOG.md /app/pages/changelog.md
COPY ./resources /app/resources
COPY ./search /app/search
COPY ./templates /app/templates
COPY ./app.py /app/app.py

USER python
CMD gunicorn -w "${APP_WORKERS:-4}" "app:app" -b "0.0.0.0:${APP_PORT:-5000}"


FROM base as dev

USER python
CMD flask --app app.py --debug run --host 0.0.0.0 --port "${APP_PORT:-5000}"