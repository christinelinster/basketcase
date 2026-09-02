# Basketcase

Basketcase is a local webhook inspection application. Create a basket in the
browser, send HTTP requests to its generated webhook URL, and inspect the
captured method, path, headers, query parameters, and body.

## Prerequisites

Install these services and tools before starting:

- Python 3 with `venv`
- Node.js and npm
- PostgreSQL
- MongoDB

PostgreSQL and MongoDB must both be running locally before database
initialization or backend startup.

## 1. Create the PostgreSQL role and database

The application expects the PostgreSQL role and database to exist before it
initializes the schema. Open `psql` as an administrative role:

```bash
psql postgres
```

Create a local application role and database. Replace the example password
with a local development password:

```sql
CREATE ROLE basketcase_app WITH LOGIN PASSWORD 'replace-with-local-password';
CREATE DATABASE basketcase OWNER basketcase_app;
\q
```

If you use an existing PostgreSQL role, ensure it can connect to the database
and create tables, types, and indexes.

MongoDB creates the configured database and collection during initialization.
The default configuration assumes local MongoDB authentication is disabled.

## 2. Configure and initialize the backend

From the repository root:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Update `backend/.env` to match the PostgreSQL role created above:

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

Initialize PostgreSQL and MongoDB:

```bash
python -m db.initialize
```

This applies the idempotent PostgreSQL schema and ensures the MongoDB
`raw_requests` collection and its indexes exist. Run it explicitly whenever
setting up fresh local databases. Backend startup does not run database DDL.

## 3. Build the frontend

The backend serves the compiled frontend from `frontend/dist` and will not
start until that directory exists. From the repository root:

```bash
cd frontend
npm install
npm run build
```

## 4. Start the backend

Keep the Python virtual environment active and run:

```bash
python index.py
```

The API listens on `http://127.0.0.1:8000` by default, and serves the
frontend built in the previous step.

## 5. Create and use a basket

1. Open `http://127.0.0.1:8000` in a browser. Enter an alphanumeric basket
   name in the New Basket form and select **Create**.
2. Copy the webhook URL returned by the backend using **Copy URL**.
3. Send a request to that URL. You may append any nested path and query
   parameters. For example, if the returned URL ends in `/demo123`:

```bash
curl -i -X POST 'http://127.0.0.1:8000/demo123/events?source=local' \
  -H 'Content-Type: application/json' \
  -d '{"event":"example","status":"received"}'
```

4. Select `demo123` under My Baskets.
5. Use the refresh control to load the captured request.

Basket names and ownership tokens are stored in the browser's local storage.
Only baskets created in that browser appear under My Baskets. The ownership
token is required to delete a basket.

## Tests and checks

Run backend tests from `backend` with the virtual environment active:

```bash
python -m pytest tests -q
```

Run frontend verification from `frontend`:

```bash
npm test
npm run lint
npm run build
```

Additional component-specific information is available in
[`backend/README.md`](backend/README.md) and
[`frontend/README.md`](frontend/README.md).
