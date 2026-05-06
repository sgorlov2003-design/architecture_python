"""Пул соединений PostgreSQL (psycopg 3)."""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator, Optional

from psycopg_pool import ConnectionPool

_pool: Optional[ConnectionPool] = None


def open_pool() -> None:
    global _pool
    if _pool is not None:
        return
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Переменная окружения DATABASE_URL не задана")
    _pool = ConnectionPool(conninfo=url, min_size=1, max_size=10, timeout=30, open=True)


def close_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


def pool() -> ConnectionPool:
    if _pool is None:
        raise RuntimeError("Пул БД не инициализирован (lifespan приложения)")
    return _pool


@contextmanager
def connection() -> Generator:
    with pool().connection() as conn:
        yield conn


def get_user_id_by_login(login: str) -> Optional[str]:
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id::text FROM users WHERE login = %s", (login,))
            row = cur.fetchone()
            return row[0] if row else None


def user_exists(login: str) -> bool:
    return get_user_id_by_login(login) is not None


def truncate_all() -> None:
    with connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "TRUNCATE workout_exercises, workouts, exercises, users RESTART IDENTITY CASCADE"
            )
        conn.commit()
    try:
        from app import redis_cache

        redis_cache.delete_prefix("ft:")
    except Exception:
        pass
