from jose import JWTError, jwt as jose_jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.auth_core import ALGORITHM, SECRET_KEY
from app import db


def _is_protected_path(path: str) -> bool:
    if path.startswith("/workouts"):
        return True
    if path.startswith("/users/me"):
        return True
    return False


def _is_public_path(path: str) -> bool:
    if path in ("/", "/health", "/token", "/openapi.json", "/auth/login"):
        return True
    if path.startswith("/docs") or path.startswith("/redoc"):
        return True
    if path.startswith("/users/by-login/") or path == "/users/search":
        return True
    if path == "/users" or path.startswith("/exercises"):
        return True
    return False


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if request.method == "OPTIONS":
            return await call_next(request)
        if _is_public_path(path) or not _is_protected_path(path):
            return await call_next(request)
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Требуется аутентификация"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = auth[7:].strip()
        try:
            payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            login = payload.get("sub")
            if not login or not db.user_exists(login):
                raise JWTError()
        except JWTError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Неверный токен"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        return await call_next(request)
