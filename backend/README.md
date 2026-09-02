# Basketcase backend

The backend is a FastAPI application backed by PostgreSQL and MongoDB. See the
[root setup guide](../README.md) for the complete local workflow, including
frontend startup and sending a webhook request.

## Install dependencies

From `backend`:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

`requirements-dev.txt` includes the runtime requirements and backend testing
dependencies.

## Configure databases

PostgreSQL and MongoDB must be running before initialization or application
startup. Configure `backend/.env`:

```dotenv
PGHOST=localhost
PGPORT=5432
PGUSER=basketcase_app
PGPASSWORD=replace-with-local-password
PGDATABASE=basketcase

MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=basketcase

HOST=127.0.0.1
PORT=8000
APP_ENV=development
```

The PostgreSQL role and database must already exist. The role must be able to
connect and create tables, types, and indexes. If MongoDB authentication is
enabled, include the credentials and `authSource` in `MONGODB_URL` and ensure
the user can create collections and indexes.

## Initialize databases

Run from `backend` with the virtual environment active:

```bash
python -m db.initialize
```

The initializer applies `db/schema.sql` to PostgreSQL and ensures the MongoDB
`raw_requests` collection and its indexes exist. The PostgreSQL schema is
idempotent for fresh setup, but it does not migrate or alter existing tables.
Application startup does not run database DDL.

## Start the API

```bash
python index.py
```

The default address is `http://127.0.0.1:8000`.

## Supported basket workflow

- `POST /api/baskets` creates a basket and returns its webhook URL and
  ownership token.
- `GET /api/baskets/{name}` returns basket metadata and captured requests.
- `DELETE /api/baskets/{name}` deletes a basket when supplied with its
  `X-Basket-Token` ownership header.
- Requests sent to `/{basket-name}` or nested paths below it are captured as
  webhooks.

The browser frontend uses the Vite `/api` proxy for API requests. Webhook
traffic is sent directly to the URL returned when the basket is created.

## Run tests

```bash
python -m pytest tests -q
```
