from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from app.api import health
from app.main import create_app


def test_health_check() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_database_health_check(monkeypatch) -> None:
    sqlite_engine = create_engine("sqlite+pysqlite:///:memory:")
    monkeypatch.setattr(health, "engine", sqlite_engine)
    client = TestClient(create_app())

    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "reachable"}
