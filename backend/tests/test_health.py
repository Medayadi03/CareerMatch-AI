import json
import logging

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.core.logging import JsonFormatter
from app.main import create_app


def test_health_lifecycle() -> None:
    app = create_app(Settings(app_env="test"))
    with TestClient(app) as client:
        assert client.get("/api/v1/health/live").json() == {"status": "alive"}
        response = client.get("/api/v1/health/ready")
        assert response.status_code == 200
        assert response.json() == {"status": "ready"}
        app.state.ready = False
        assert client.get("/api/v1/health/ready").status_code == 503
        assert client.get("/api/v1/health/live").status_code == 200
    assert app.state.ready is False


def test_openapi() -> None:
    with TestClient(create_app()) as client:
        assert "/api/v1/health/ready" in client.get("/openapi.json").json()["paths"]
        assert client.get("/docs").status_code == 200


@pytest.mark.parametrize(
    "origin,allowed", [("http://localhost:5173", True), ("https://untrusted.example", False)]
)
def test_cors(origin: str, allowed: bool) -> None:
    with TestClient(create_app(Settings(cors_origins=["http://localhost:5173"]))) as client:
        response = client.options(
            "/api/v1/health/ready",
            headers={"Origin": origin, "Access-Control-Request-Method": "GET"},
        )
        assert response.status_code == (200 if allowed else 400)
        assert (response.headers.get("access-control-allow-origin") == origin) is allowed


def test_reject_wildcard_cors() -> None:
    with pytest.raises(ValidationError):
        Settings(cors_origins=["*"])


def test_environment_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("CORS_ORIGINS", '["https://careermatch.example"]')
    settings = Settings()
    assert settings.app_env == "test"
    assert settings.cors_origins == ["https://careermatch.example"]


def test_json_logging() -> None:
    record = logging.LogRecord("careermatch", logging.INFO, "", 0, "application_started", (), None)
    payload = json.loads(JsonFormatter().format(record))
    assert payload["event"] == "application_started"
    assert payload["level"] == "INFO"
