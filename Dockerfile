# syntax=docker/dockerfile:1.4
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY ./pages /app/pages
COPY ./static /app/static
COPY ./CHANGELOG.md /app/pages/changelog.md
COPY ./resources /app/resources
COPY ./search /app/search
COPY ./templates /app/templates
COPY ./app.py /app/app.py

CMD ["flask", "--app", "app.py", "--debug", "run", "--host", "0.0.0.0"]