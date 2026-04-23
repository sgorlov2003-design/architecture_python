import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("MONGO_URI", "mongodb://127.0.0.1:27018")
os.environ.setdefault("MONGO_DATABASE", "fitness_tracker")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

from app import db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as c:
        db.truncate_all()
        yield c
