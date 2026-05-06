import json
import os
from typing import Any, Optional

import redis

_r: Optional[redis.Redis] = None

KEY_EXERCISES_LIST = "ft:exercises:list"


def connect() -> None:
    global _r
    if _r is not None:
        return
    url = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
    _r = redis.from_url(url, decode_responses=True)


def close() -> None:
    global _r
    if _r is not None:
        _r.close()
        _r = None


def client() -> redis.Redis:
    if _r is None:
        raise RuntimeError("Redis не подключён")
    return _r


def get_json(key: str) -> Optional[Any]:
    raw = client().get(key)
    return json.loads(raw) if raw else None


def set_json(key: str, value: Any, ttl_seconds: int) -> None:
    client().setex(key, ttl_seconds, json.dumps(value))


def delete(key: str) -> None:
    client().delete(key)


def delete_prefix(prefix: str) -> None:
    if _r is None:
        return
    for k in _r.scan_iter(match=f"{prefix}*"):
        _r.delete(k)


def key_user_login(login: str) -> str:
    return f"ft:user:login:{login}"


def key_stats(user_id: str, start: str, end: str) -> str:
    return f"ft:stats:{user_id}:{start}:{end}"


def invalidate_exercises() -> None:
    delete(KEY_EXERCISES_LIST)


def invalidate_stats(user_id: str) -> None:
    if _r is None:
        return
    p = f"ft:stats:{user_id}:"
    for k in _r.scan_iter(match=f"{p}*"):
        _r.delete(k)
