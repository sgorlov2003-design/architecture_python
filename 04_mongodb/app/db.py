import os
from typing import Optional

from pymongo import MongoClient

_client: Optional[MongoClient] = None
_db = None


def open_pool() -> None:
    global _client, _db
    if _client is not None:
        return
    uri = os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017")
    name = os.environ.get("MONGO_DATABASE", "fitness_tracker")
    _client = MongoClient(uri, serverSelectionTimeoutMS=15000)
    _client.admin.command("ping")
    _db = _client[name]
    _db.users.create_index("login", unique=True)


def close_pool() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None


def database():
    if _db is None:
        raise RuntimeError("MongoDB не инициализирован")
    return _db


def get_user_id_by_login(login: str) -> Optional[str]:
    doc = database().users.find_one({"login": login}, {"_id": 1})
    return str(doc["_id"]) if doc else None


def user_exists(login: str) -> bool:
    return database().users.count_documents({"login": login}, limit=1) > 0


def truncate_all() -> None:
    d = database()
    d.workouts.delete_many({})
    d.exercises.delete_many({})
    d.users.delete_many({})
