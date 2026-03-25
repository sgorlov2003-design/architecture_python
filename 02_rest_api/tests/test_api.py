"""Тесты API (успех + ошибки) — ДЗ 02, вариант 14."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import reset_storage

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    reset_storage()
    yield


def test_create_user():
    r = client.post(
        "/users",
        json={"login": "testuser", "password": "pass123", "first_name": "Test", "last_name": "User"},
    )
    assert r.status_code == 201
    assert r.json()["login"] == "testuser"


def test_create_user_duplicate():
    client.post("/users", json={"login": "dup", "password": "p", "first_name": "A", "last_name": "B"})
    r = client.post("/users", json={"login": "dup", "password": "p2", "first_name": "C", "last_name": "D"})
    assert r.status_code == 409


def test_get_user_by_login():
    client.post("/users", json={"login": "findme", "password": "p", "first_name": "Find", "last_name": "Me"})
    r = client.get("/users/by-login/findme")
    assert r.status_code == 200


def test_user_not_found():
    assert client.get("/users/by-login/ghost").status_code == 404


def test_token_oauth2():
    client.post("/users", json={"login": "u1", "password": "s", "first_name": "U", "last_name": "One"})
    r = client.post("/token", data={"username": "u1", "password": "s"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_json():
    client.post("/users", json={"login": "u2", "password": "s", "first_name": "U", "last_name": "Two"})
    r = client.post("/auth/login", json={"login": "u2", "password": "s"})
    assert r.status_code == 200


def test_workout_without_token():
    assert client.post("/workouts", json={"name": "W"}).status_code == 401


def test_workout_with_oauth2_token():
    client.post("/users", json={"login": "wuser", "password": "p", "first_name": "W", "last_name": "U"})
    tr = client.post("/token", data={"username": "wuser", "password": "p"})
    token = tr.json()["access_token"]
    r = client.post(
        "/workouts",
        json={"name": "My workout", "date": "2025-03-18"},
        headers={"Authorization": "Bearer " + token},
    )
    assert r.status_code == 201, r.text


def test_exercise_crud():
    r = client.post("/exercises", json={"name": "Push", "description": "x"})
    assert r.status_code == 201
    eid = r.json()["id"]
    assert client.get(f"/exercises/{eid}").status_code == 200
    assert client.patch(f"/exercises/{eid}", json={"name": "Push-up"}).status_code == 200
    assert client.delete(f"/exercises/{eid}").status_code == 204
    assert client.get(f"/exercises/{eid}").status_code == 404


def test_middleware_blocks_workout():
    """Без Bearer middleware возвращает 401."""
    r = client.post("/workouts", json={"name": "X"})
    assert r.status_code == 401
    assert "middleware" in r.json().get("detail", "").lower() or "аутентификация" in r.json().get("detail", "")
