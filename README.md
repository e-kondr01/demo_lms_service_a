# Service A
## Python version
3.12
## Local
### Installation
#### FastAPI app
1. Create venv
```bash
python3.12 -m venv .venv
```

2. Activate venv
```bash
source .venv/bin/activate
```

3. Install requirements
```bash
pip install -r app/requirements/local.txt
```

4. Copy .env
```bash
cp app/app/local.example.env app/app/.env
```

#### Docker and Docker compose
Refer to:

https://docs.docker.com/engine/install/

### Usage

Use the script to start PSQL, PGAdmin in Docker Compose, apply migrations and run uvicorn:
```bash
make local
```

## Migrations
Powered by Alembic
```bash
make migrations
```

## Swagger Docs
Go to http://127.0.0.1:8000/api/docs after running server

## Development

During development use Black formatter, Pylint, Flake8 and MyPy.

## Prod

### Installation
Copy .env:
```bash
cp app/app/production.example.env app/app/.env
```

### Deploy
Use shortcut script:
```bash
make up
```
