# Vector Oligo Search

Python Flask web application for running a genome vector search script.

## Running as container

```
❯ docker compose build
❯ docker compose up
```

Needs to rebuild the container after every code edit, which is a downer.

## Running Directly

```
❯ pip3 install -r requirements.txt
❯ flask --app app.py --debug run
```

Not quite hot-module, but instant reload on the server itself! Much better.