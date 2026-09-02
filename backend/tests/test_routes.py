from datetime import datetime, timezone
from unittest.mock import AsyncMock
import uuid

import asyncpg
import httpx
import pytest
import pytest_asyncio
from fastapi import HTTPException

from db import mongo, postgres
from db.dependencies import get_basket_token, get_postgres_pool
from index import app


pytestmark = pytest.mark.asyncio


class FakeAcquire:
    def __init__(self, connection):
        self.connection = connection

    async def __aenter__(self):
        return self.connection

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False


class FakePool:
    def __init__(self, connection):
        self.connection = connection

    def acquire(self):
        return FakeAcquire(self.connection)


class RecordingConnection:
    def __init__(self, result):
        self.result = result
        self.fetchrow_calls = []

    async def fetchrow(self, query, *args):
        self.fetchrow_calls.append((query, args))
        if isinstance(self.result, BaseException):
            raise self.result
        return self.result


class BasketConnection:
    def __init__(self, basket, requests):
        self.basket = basket
        self.requests = requests
        self.fetchrow_calls = []
        self.fetch_calls = []

    async def fetchrow(self, query, *args):
        self.fetchrow_calls.append((query, args))
        return self.basket

    async def fetch(self, query, *args):
        self.fetch_calls.append((query, args))
        return self.requests


class MutationConnection:
    def __init__(self, fetchrow_results):
        self.fetchrow_results = list(fetchrow_results)
        self.fetchrow_calls = []
        self.execute_calls = []

    async def fetchrow(self, query, *args):
        self.fetchrow_calls.append((query, args))
        return self.fetchrow_results.pop(0)

    async def execute(self, query, *args):
        self.execute_calls.append((query, args))


class MongoCollection:
    def __init__(self):
        self.insert_one = AsyncMock()


class MongoDatabase:
    def __init__(self, collection):
        self.collection = collection

    def __getitem__(self, collection_name):
        assert collection_name == "raw_requests"
        return self.collection


@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as async_client:
        yield async_client


async def test_hello_route(client):
    response = await client.get("/api/baskets/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "hello world"}


async def test_get_postgres_pool_returns_initialized_pool(monkeypatch):
    expected_pool = FakePool(RecordingConnection(None))
    monkeypatch.setattr(postgres, "pool", expected_pool)

    assert get_postgres_pool() is expected_pool


async def test_get_postgres_pool_rejects_unavailable_database(monkeypatch):
    monkeypatch.setattr(postgres, "pool", None)

    with pytest.raises(HTTPException) as caught:
        get_postgres_pool()

    assert caught.value.status_code == 503
    assert caught.value.detail == "Database unavailable"


async def test_get_basket_token_returns_valid_uuid():
    token = "12345678-1234-5678-1234-567812345678"

    assert get_basket_token(token) == uuid.UUID(token)


@pytest.mark.parametrize("token", [None, "", "not-a-uuid"])
async def test_get_basket_token_rejects_missing_or_invalid_value(token):
    with pytest.raises(HTTPException) as caught:
        get_basket_token(token)

    assert caught.value.status_code == 404
    assert caught.value.detail == "Resource not found"


async def test_delete_basket_uses_injected_token(client, monkeypatch):
    token = uuid.UUID("12345678-1234-5678-1234-567812345678")
    connection = RecordingConnection({"id": 7})
    monkeypatch.setattr(postgres, "pool", FakePool(connection))
    app.dependency_overrides[get_basket_token] = lambda: token

    try:
        response = await client.delete("/api/baskets/demo123")
    finally:
        app.dependency_overrides.pop(get_basket_token, None)

    assert response.status_code == 204
    _, args = connection.fetchrow_calls[0]
    assert args == ("demo123", token)


async def test_create_basket_uses_injected_postgres_pool(client, monkeypatch):
    connection = RecordingConnection(
        {
            "name": "demo123",
            "token": uuid.UUID("12345678-1234-5678-1234-567812345678"),
            "expires_at": datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc),
        }
    )
    injected_pool = FakePool(connection)
    monkeypatch.setattr(postgres, "pool", None)
    app.dependency_overrides[get_postgres_pool] = lambda: injected_pool

    try:
        response = await client.post("/api/baskets", json={"name": "demo123"})
    finally:
        app.dependency_overrides.pop(get_postgres_pool, None)

    assert response.status_code == 201


async def test_webhook_stores_basket_id_in_mongo(client, monkeypatch):
    connection = MutationConnection([{"id": 7}])
    pool = FakePool(connection)
    collection = MongoCollection()
    database = MongoDatabase(collection)
    monkeypatch.setattr(mongo, "get_database", lambda: database)
    app.dependency_overrides[get_postgres_pool] = lambda: pool

    try:
        response = await client.post(
            "/demo123/events?source=postman",
            content=b'{"ok":true}',
            headers={"Content-Type": "application/json"},
        )
    finally:
        app.dependency_overrides.pop(get_postgres_pool, None)

    assert response.status_code == 200
    document = collection.insert_one.await_args.args[0]
    assert document["basket_id"] == 7
    assert document["body"] == b'{"ok":true}'


async def test_create_basket_returns_webhook_url_token_and_expiry(client, monkeypatch):
    token = uuid.UUID("12345678-1234-5678-1234-567812345678")
    expires_at = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)
    connection = RecordingConnection(
        {
            "name": "demo123",
            "token": token,
            "expires_at": expires_at,
        }
    )
    monkeypatch.setattr(postgres, "pool", FakePool(connection))

    response = await client.post("/api/baskets", json={"name": "demo123"})

    assert response.status_code == 201
    assert response.json() == {
        "name": "demo123",
        "webhook_url": "http://testserver/demo123",
        "token": "12345678-1234-5678-1234-567812345678",
        "expires_at": "2026-09-01T12:00:00Z",
    }
    assert len(connection.fetchrow_calls) == 1
    query, args = connection.fetchrow_calls[0]
    assert "INSERT INTO baskets (name)" in query
    assert "ON CONFLICT (name) DO NOTHING" in query
    assert "RETURNING name, token, expires_at" in query
    assert args == ("demo123",)


@pytest.mark.parametrize(
    "name",
    ["", "demo-123", "baskets", "Baskets", "BASKETS", "a" * 51],
)
async def test_create_basket_rejects_invalid_names_without_database_call(
    client, monkeypatch, name
):
    connection = RecordingConnection(None)
    monkeypatch.setattr(postgres, "pool", FakePool(connection))

    response = await client.post("/api/baskets", json={"name": name})

    assert response.status_code == 422
    assert connection.fetchrow_calls == []


async def test_create_basket_returns_conflict_for_duplicate_name(client, monkeypatch):
    connection = RecordingConnection(None)
    monkeypatch.setattr(postgres, "pool", FakePool(connection))

    response = await client.post("/api/baskets", json={"name": "demo123"})

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Failed to create basket - demo123 already exists."
    }


async def test_create_basket_returns_internal_error_for_other_unique_violation(
    client, monkeypatch
):
    error = asyncpg.UniqueViolationError("duplicate token")
    error.constraint_name = "baskets_token_key"
    connection = RecordingConnection(error)
    monkeypatch.setattr(postgres, "pool", FakePool(connection))

    response = await client.post("/api/baskets", json={"name": "demo123"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


async def test_create_basket_returns_internal_error_for_database_error(
    client, monkeypatch
):
    connection = RecordingConnection(asyncpg.PostgresError("database error"))
    monkeypatch.setattr(postgres, "pool", FakePool(connection))

    response = await client.post("/api/baskets", json={"name": "demo123"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


async def test_create_basket_returns_internal_error_for_unexpected_error(
    client, monkeypatch
):
    connection = RecordingConnection(RuntimeError("unexpected error"))
    monkeypatch.setattr(postgres, "pool", FakePool(connection))

    response = await client.post("/api/baskets", json={"name": "demo123"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


async def test_get_basket_returns_metadata_and_requests_newest_first(client, monkeypatch):
    older_received_at = datetime(2026, 8, 29, 19, 0, tzinfo=timezone.utc)
    newer_received_at = datetime(2026, 8, 29, 20, 0, tzinfo=timezone.utc)
    connection = BasketConnection(
        {
            "id": 7,
            "name": "demo123",
            "capacity": 200,
            "expires_at": datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc),
        },
        [
            {
                "id": 2,
                "method": "POST",
                "path": "/events",
                "headers": {"content-type": "application/json"},
                "query_params": {"source": "test"},
                "body": '{"ok":true}',
                "received_at": newer_received_at,
            },
            {
                "id": 1,
                "method": "GET",
                "path": "/health",
                "headers": {},
                "query_params": {},
                "body": None,
                "received_at": older_received_at,
            },
        ],
    )
    monkeypatch.setattr(postgres, "pool", FakePool(connection))

    response = await client.get("/api/baskets/demo123")

    assert response.status_code == 200
    assert response.json() == {
        "name": "demo123",
        "capacity": 200,
        "expires_at": "2026-09-01T12:00:00Z",
        "requests": [
            {
                "id": 2,
                "method": "POST",
                "path": "/events",
                "headers": {"content-type": "application/json"},
                "query_params": {"source": "test"},
                "body": '{"ok":true}',
                "received_at": "2026-08-29T20:00:00Z",
            },
            {
                "id": 1,
                "method": "GET",
                "path": "/health",
                "headers": {},
                "query_params": {},
                "body": None,
                "received_at": "2026-08-29T19:00:00Z",
            },
        ],
    }
    assert len(connection.fetchrow_calls) == 1
    basket_query, basket_args = connection.fetchrow_calls[0]
    assert "FROM baskets" in basket_query
    assert "WHERE name = $1" in basket_query
    assert basket_args == ("demo123",)
    assert len(connection.fetch_calls) == 1
    requests_query, request_args = connection.fetch_calls[0]
    assert "FROM requests" in requests_query
    assert "ORDER BY received_at DESC" in requests_query
    assert request_args == (7,)


async def test_get_basket_returns_empty_requests_for_basket_without_requests(
    client, monkeypatch
):
    connection = BasketConnection(
        {
            "id": 7,
            "name": "demo123",
            "capacity": 200,
            "expires_at": datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc),
        },
        [],
    )
    monkeypatch.setattr(postgres, "pool", FakePool(connection))

    response = await client.get("/api/baskets/demo123")

    assert response.status_code == 200
    assert response.json()["requests"] == []


async def test_get_basket_returns_not_found_for_unknown_name(client, monkeypatch):
    connection = BasketConnection(None, [])
    monkeypatch.setattr(postgres, "pool", FakePool(connection))

    response = await client.get("/api/baskets/missing123")

    assert response.status_code == 404
    assert response.json() == {"detail": "Basket not found"}
    assert connection.fetch_calls == []


@pytest.mark.parametrize(
    "method",
    ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE"],
)
async def test_webhook_methods_are_registered(client, method):
    response = await client.request(method, "/example")

    assert response.status_code == 200


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/api/baskets"),
        ("DELETE", "/api/baskets/example"),
        ("DELETE", "/api/baskets/example/requests"),
        ("GET", "/api/baskets/example/requests/request-id"),
        ("DELETE", "/api/baskets/example/requests/request-id"),
    ],
)
async def test_future_interface_routes_are_not_implemented(client, method, path):
    response = await client.request(method, path)

    assert response.status_code == 501
    assert response.json() == {"detail": "Not implemented"}
