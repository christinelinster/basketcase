import asyncio
import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect, status

from db import postgres


# No prefix: the socket lives at /ws/{name}, not /api/ws/{name}.
router = APIRouter()
logger = logging.getLogger(__name__)

# Which browsers are currently watching which basket.
#
# Keys are basket names, values are the set of open connections for that basket -
# a set because one basket can be open in several tabs, and each tab is its own
# connection. WebSocket compares by identity, so two tabs never collapse into one
# entry and discard() removes exactly the connection that left.
#
# This dict lives in one Python process. With more than one uvicorn worker, a
# browser attached to worker A would never hear a broadcast made by worker B.
# One worker is the deployment plan; broadcast_refresh() is the single place that
# would change if that stops being true.
watchers: dict[str, set[WebSocket]] = {}

# A browser whose receive buffer is full makes send_json() block. Ingest calls
# broadcast_refresh(), so without a bound the webhook response time becomes a
# function of the slowest connected browser.
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
    """The only message this feature sends.

    It carries no request data on purpose. The browser reacts by re-fetching
    GET /api/baskets/{name}, so the request shape stays defined in exactly one
    place, and two signals are indistinguishable from one.
    """
    return {"event": "refresh", "basket_name": name}


@router.websocket("/ws/{name}")
async def watch_basket(
    websocket: WebSocket,
    name: str,
    token: str | None = Query(None),
) -> None:
    """Hold a connection open to a browser viewing one basket, so the server can
    tell it to reload the moment a new request lands there.

    The token arrives in the query string rather than a header because the
    browser's WebSocket constructor cannot set custom headers - X-Basket-Token,
    which the delete routes rely on, is simply not available here.
    """

    # Query(None) rather than Query(...): a required parameter would make FastAPI
    # close the socket with 1008 before this function body ran, splitting
    # rejection behaviour between FastAPI and us. Optional keeps every rejection
    # path in one place - here.
    try:
        basket_token = UUID(token)
    except (ValueError, TypeError):
        # Closing before accept() means the browser sees the handshake itself
        # fail, rather than a socket that opened and immediately died.
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 1013, not 1008: the database being down is our problem, not the client's.
    # A reconnecting client is meant to stop retrying on 1008 (a rejected token
    # will never start working), but should keep retrying through a transient
    # outage - which 1008 here would turn into a permanent disconnect.
    if postgres.pool is None:
        await websocket.close(code=status.WS_1013_TRY_AGAIN_LATER)
        return

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

    # An unknown basket and a wrong token are refused identically, for the same
    # reason the delete routes return 404 for both: reacting differently would
    # tell someone probing names which ones are real.
    if basket is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()

    # Register before sending the first refresh. From this line on the connection
    # is guaranteed to receive anything broadcast, so a request arriving while
    # the browser is still re-reading the list is queued on the socket rather
    # than lost. Sending first would reopen the very gap the refresh closes.
    watchers.setdefault(name, set()).add(websocket)

    try:
        # Tell the browser to reload right now. Without this, requests can slip
        # through: the page fetches the list first and opens the socket second,
        # so anything arriving in between is in neither.
        await websocket.send_json(refresh_message(name))

        # The browser never sends us anything - it only listens. We read anyway,
        # because a read is the only way to learn the connection died. Without
        # this loop the function would return and the socket would close
        # immediately.
        #
        # receive() rather than receive_text(): receive_text() ends in
        # message["text"], so a client sending a binary frame would raise
        # KeyError straight past the except below. receive() handles text,
        # binary and disconnect alike.
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                break

    except WebSocketDisconnect:
        pass

    finally:
        # Always deregister, however the loop ended. Skipping this would grow the
        # dict forever and leave broadcasts trying to reach sockets that are gone.
        connections = watchers.get(name)

        if connections is not None:
            connections.discard(websocket)

            if not connections:
                del watchers[name]


@router.api_route("/ws/{name}", methods=HTTP_METHODS, include_in_schema=False)
async def ws_upgrade_required(name: str) -> None:
    """Answer plain HTTP requests to the socket path with 426.

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
    """Tell every browser watching this basket to reload its request list.

    Called by the ingest handler after the request is committed to Postgres.
    Ordering matters: the signal means "go look", so sending it before the write
    lands would have the browser re-read the list and miss the very request that
    triggered the refresh.
    """
    connections = watchers.get(name)

    if not connections:
        return

    message = refresh_message(name)

    # Iterate a copy: sending can fail on a connection that has already gone
    # away, and we drop those as we go - mutating the set while looping over it
    # directly would raise.
    for connection in list(connections):
        try:
            await asyncio.wait_for(
                connection.send_json(message),
                timeout=SEND_TIMEOUT_SECONDS,
            )

        except Exception:
            # Either the socket is dead and we were never told, or it is too
            # slow to matter. Drop it and keep going, so one bad connection
            # cannot stop the others from being notified - or hold up ingest.
            logger.debug("Dropping unreachable watcher for basket %s", name)
            connections.discard(connection)

    # The identity check is not paranoia. There are awaits in the loop above, so
    # while we were sending, the last watcher could have disconnected (its finally
    # block deleting this key) and a new one connected, putting a brand-new set at
    # watchers[name]. Deleting on the strength of our now-orphaned local reference
    # would silently unregister that live connection.
    if not connections and watchers.get(name) is connections:
        del watchers[name]
