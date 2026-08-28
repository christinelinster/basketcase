import os
import json
import secrets

from starlette.middleware.base import BaseHTTPMiddleware

# this is now depricated, switching to JWT for basketcase project
# i think
SESSION_COOKIE_NAME = "capstone"
SESSION_MAX_AGE = 60 * 60 * 24 * 7
SESSION_PREFIX = "sess:"

SESSION_COOKIE_SECURE = (
    os.getenv("NODE_ENV") == "production"
)


class RedisSessionMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.redis_client = redis_client

    async def dispatch(self, request, call_next):

        session_id = request.cookies.get(SESSION_COOKIE_NAME)
        session = {}

        # Load existing session
        if session_id and self.redis_client:

            session_data = await self.redis_client.get(
                f"{SESSION_PREFIX}{session_id}"
            )

            if session_data:
                session = json.loads(session_data)

        request.state.session = session

        #user example: request.state.url = session.get("url")

        response = await call_next(request)

        # Save session
        if request.state.session and self.redis_client:

            if not session_id:
                session_id = secrets.token_urlsafe(32)

            await self.redis_client.set(
                f"{SESSION_PREFIX}{session_id}",
                json.dumps(request.state.session),
                ex=SESSION_MAX_AGE
            )

            response.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=session_id,
                max_age=SESSION_MAX_AGE,
                path="/",
                httponly=True,
                secure=SESSION_COOKIE_SECURE,
                samesite="lax"
            )

        return response    