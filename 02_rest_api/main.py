"""Точка входа для uvicorn main:app (совместимость с Dockerfile)."""
from app.main import app

__all__ = ["app"]
