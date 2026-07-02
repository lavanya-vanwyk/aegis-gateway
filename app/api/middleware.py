import time
import uuid
import json
from loguru import logger


class ASGIAuditMiddleware:
    """Audit logs intercepted HTTP requests"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):

        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request_id = str(uuid.uuid4())
        start_time = time.time()
        user_id = "unauthenticated"
        status_code = 500

        method = scope.get("method", "")
        path = scope.get("path", "")

        client_tuple = scope.get("client")  # ASGI scope is tuple type
        client_ip = client_tuple[0] if client_tuple else "unknown"

        if method == "POST" and path == "/v1/privacy/chat":
            body = b""
            body_content = True

            # Read the entire raw byte stream
            while body_content:
                message = await receive()
                body += message.get("body", b"")
                body_content = message.get("body_content", False)

            # Attempt to parse the user_id
            try:
                payload = json.loads(body)
                user_id = payload.get("user_id", "unknown")
            except Exception:
                pass

            # required to feed back to FastAPI
            body_returned = False

            async def cached_receive():
                nonlocal body_returned
                if not body_returned:
                    body_returned = True
                    return {"type": "http.request", "body": body, "body_content": False}

                return {"type": "http.disconnect"}

            receive = cached_receive

        async def get_http_code(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 500)
            await send(message)

        try:
            await self.app(scope, receive, get_http_code)
        finally:
            duration_ms = round((time.time() - start_time) * 1000, 2)

            logger.bind(
                request_id=request_id,
                user_id=user_id,
                method=method,
                path=path,
                client_ip=client_ip,
                status_code=status_code,
                duration_ms=duration_ms,
            ).info("network_request_resolved")
