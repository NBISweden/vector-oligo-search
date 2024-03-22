# syntax=docker/dockerfile:1.4
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /app

CMD ["flask", "--app", "app.py", "--debug", "run", "--host", "0.0.0.0"]