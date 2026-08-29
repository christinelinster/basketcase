import httpx
import pytest
import pytest_asyncio

from index import app


pytestmark = pytest.mark.asyncio


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
        ("POST", "/api/baskets"),
        ("GET", "/api/baskets/example"),
        ("DELETE", "/api/baskets/example"),
        ("GET", "/api/baskets/example/requests"),
        ("DELETE", "/api/baskets/example/requests"),
        ("GET", "/api/baskets/example/requests/request-id"),
        ("DELETE", "/api/baskets/example/requests/request-id"),
    ],
)
async def test_future_interface_routes_are_not_implemented(client, method, path):
    response = await client.request(method, path)

    assert response.status_code == 501
    assert response.json() == {"detail": "Not implemented"}
