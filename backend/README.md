# Basketcase backend

## Setup

Start the PostgreSQL and MongoDB instances, then create a local environment file:

```bash
cd backend
cp .env.example .env
```

The configured databases should both be named `basketcase`:

```dotenv
POSTGRES_URL=postgresql://postgres:password@localhost:5432/basketcase
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=basketcase
```

## Initialize the databases

Run initialization explicitly before starting the application:

```bash
python -m db.initialize
```

The command connects to both configured database instances. PostgreSQL receives
the existing `db/schema.sql` on a fresh database. MongoDB creates the
`raw_requests` collection and its indexes. If the PostgreSQL schema is already
complete, the command leaves it unchanged. Application startup does not run
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

## Run tests

```bash
python -m pytest tests -q
```
