import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("uvicorn.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        start = time.perf_counter()

        try:
            response: Response = await call_next(request)
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            # Logging apenas após call_next para capturar status
            # response.status_code pode não existir se call_next levantar erro.
            # Nesse caso, a exceção será tratada pelo handler padrão do FastAPI.

        # Se call_next falhou com exceção, essa linha não roda.
        response.headers["X-Request-Id"] = request_id
        logger.info(
            "%s %s status=%s request_id=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            request_id,
            duration_ms,
        )
        return response