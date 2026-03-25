"""In-memory хранилище (списки, словари) — по заданию ДЗ 02."""
from typing import Optional

users_db: dict[str, dict] = {}
exercises_db: list[dict] = []
workouts_db: list[dict] = []


def reset_storage() -> None:
    """Для тестов."""
    users_db.clear()
    exercises_db.clear()
    workouts_db.clear()
