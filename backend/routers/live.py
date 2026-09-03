import asyncio
import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect, status

from db import postgres


# WebSockets live at /ws/{name}
router = APIRouter()
logger = logging.getLogger(__name__)

# `watchers` maps each basket name to that basket's active connections.
# * Connection state is scoped to a single uvicorn process. 
#   If deployed with multiple processes, webhook requests may bind to a different 
#   process, breaking live-refresh functionality for that browser-basket connection.
watchers: dict[str, set[WebSocket]] = {}

# If a browser fails to respond to broadcast_refresh() within 5 seconds, stop waiting
SEND_TIMEOUT_SECONDS = 5

# Every method the ingest catch-all accepts, so a failed upgrade on this path
# cannot fall through to it. See ws_upgrade_required() below.
HTTP_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "HEAD",
    "OPTIONS",
    "TRACE",
]


def refresh_message(name: str) -> dict[str, str]:
    """Return the basket name to the frontend. 
    - "refresh" prompts the frontend service to re-fetch the GET /api/baskets/{name} route.
    """

    return {"event": "refresh", "basket_name": name}


@router.websocket("/ws/{name}")
async def watch_basket(
    websocket: WebSocket,
    name: str,
    token: str | None = Query(None),
) -> None:
    """Establish a persistent connection between a browser and a basket.
      - Basket tokens are given in the query string since WebSockets do not support
        custom HTTP headers.
    """

    try:
        basket_token = UUID(token)
    except (ValueError, TypeError):
        # Closing before accept() means the browser sees the handshake itself
        # fail, rather than a socket that opened and immediately died.
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Server is temporarily unavailable; retry the connection
    if postgres.pool is None:
        await websocket.close(code=status.WS_1013_TRY_AGAIN_LATER)
        return

    # Check if the name-token basket combo exists:
    async with postgres.pool.acquire() as connection:
        basket = await connection.fetchrow(
            """
            SELECT id
            FROM baskets
            WHERE name = $1 AND token = $2
            """,
            name,
            basket_token,
        )
    if basket is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Upgrade the connection to WebSocket, and register the connection to watchers:
    await websocket.accept()
    watchers.setdefault(name, set()).add(websocket)

    try:
        # Reload immediately, in case a message was received between the initial fetch
        # and the WebSocket upgrade.
        await websocket.send_json(refresh_message(name))
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                break

    except WebSocketDisconnect:
        pass

    finally:
        connections = watchers.get(name)

        if connections is not None:
            connections.discard(websocket)

            if not connections:
                del watchers[name]


@router.api_route("/ws/{name}", methods=HTTP_METHODS, include_in_schema=False)
async def ws_upgrade_required(name: str) -> None:
    """If any plain HTTP request to the WebSocket path fails to upgrade, 
    respond with 426 (Upgrade Required).

    A real WebSocket never reaches this: Starlette matches routes on the ASGI
    scope type, so the websocket route above claims every successful upgrade.
    But when an upgrade *fails* - nginx missing the Upgrade/Connection headers, a
    proxy stripping them, someone pasting the URL into a browser - the request
    arrives as ordinary HTTP. Without this route it would fall through to the
    ingest catch-all in webhooks.py, which would read the basket name as "ws" and
    store the failed upgrade as a webhook. Only 'baskets' is reserved in the
    schema, so a basket named "ws" is possible and would collect that garbage.
    """
    raise HTTPException(
        status_code=status.HTTP_426_UPGRADE_REQUIRED,
        detail="This endpoint requires a WebSocket upgrade",
    )


async def broadcast_refresh(name: str) -> None:
    """Notify every browser connected to this basket to reload.
    - To be called by the webhook route after the request is successfully
      persisted to Postgres.
    """
    connections = watchers.get(name)

    if not connections:
        return

    message = refresh_message(name)

    # Iterate a copy of connections so we aren't mutating connection mid-iteration.
    for connection in list(connections):
        try:
            await asyncio.wait_for(
                connection.send_json(message),
                timeout=SEND_TIMEOUT_SECONDS,
            )

        except Exception:
            logger.debug("Dropping unreachable watcher for basket %s", name)
            connections.discard(connection)

    # The identity check is not paranoia. There are awaits in the loop above, so
    # while we were sending, the last watcher could have disconnected (its finally
    # block deleting this key) and a new one connected, putting a brand-new set at
    # watchers[name]. Deleting on the strength of our now-orphaned local reference
    # would silently unregister that live connection.

    # De-register the current basket from watchers ONLY if it has no active connections
    # and has not already been discarded while waiting for a network call to resolve.
    if not connections and watchers.get(name) is connections:
        del watchers[name]
