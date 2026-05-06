import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://fitness_user:fitness_password@127.0.0.1:5433/fitness_tracker",
)
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6380/0")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

from app import db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as c:
        db.truncate_all()
        yield c
