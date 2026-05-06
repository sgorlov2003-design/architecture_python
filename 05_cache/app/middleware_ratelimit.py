import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app import redis_cache

LIMIT = 60
WINDOW_SEC = 60


def _client_ip(request: Request) -> str:
    xf = request.headers.get("x-forwarded-for")
    if xf:
        return xf.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if request.method == "POST" and path in ("/token", "/auth/login", "/users"):
            ip = _client_ip(request)
            bucket = int(time.time()) // WINDOW_SEC
            key = f"ft:rl:{ip}:{bucket}"
            n = redis_cache.client().incr(key)
            if n == 1:
                redis_cache.client().expire(key, WINDOW_SEC * 2)
            if n > LIMIT:
                return JSONResponse(status_code=429, content={"detail": "Слишком много запросов"})
        return await call_next(request)
