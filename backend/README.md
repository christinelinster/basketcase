# Basketcase backend

## Setup

Start the PostgreSQL and MongoDB instances, then create a local environment file:

```bash
cd backend
cp .env.example .env
```

Create the PostgreSQL database and role before initialization, then configure
the connection using individual values:

```dotenv
PGHOST=localhost
PGPORT=5432
PGUSER=basketcase_app
PGPASSWORD=password
PGDATABASE=basketcase
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=basketcase
```

The PostgreSQL database in `PGDATABASE` and role in `PGUSER` must already exist.
The role must authenticate with `PGPASSWORD`, connect to the database, and be
allowed to create tables, types, and indexes. PostgreSQL commonly provides a
role named `postgres`, but it has no universal default password. Leave
`PGPASSWORD` empty only when the server permits passwordless authentication.
Explicit values in `.env` override the local defaults.

The MongoDB credentials, when present, must already exist and have permission
to create collections and indexes in `MONGODB_DATABASE`.

## Initialize the databases

Run initialization explicitly before starting the application:

```bash
python -m db.initialize
```

The command connects to the existing `PGDATABASE` and applies the idempotent
`db/schema.sql`, which creates missing PostgreSQL tables, types, and indexes.
Existing tables are not migrated or altered. MongoDB creates
`MONGODB_DATABASE` implicitly when needed, creates the `raw_requests` collection
when missing, and ensures its indexes exist. Application startup does not run
database DDL.

## Start the backend

```bash
python index.py
```

The local server listens on `http://127.0.0.1:8000` by default. Verify the
backend hello route with:

```bash
curl -i http://127.0.0.1:8000/api/baskets/hello
```

Expected response:

```json
{"message":"hello world"}
```

The Vite proxy targets port `8000`. If your local `.env` overrides `PORT`, set
it to `8000` for this workflow or update the proxy target in
`frontend/vite.config.ts` to the same port.

## Verify the frontend connection

With the backend running, start the Vite development server in a second
terminal:

```bash
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173`. The page should show the default Vite counter
and the `hello world` message returned by the backend through the Vite `/api`
proxy.

## Run tests

```bash
python -m pytest tests -q
```
