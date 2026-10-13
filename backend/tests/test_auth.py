"""Tests for session-cookie authentication."""

import pytest
from httpx import AsyncClient

from app.auth import SESSION_COOKIE, create_session_token, verify_session_token
from app.config import settings

CREDENTIALS = {"username": "admin", "password": "correct horse battery staple"}


@pytest.fixture
def auth_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "auth_enabled", True)
    monkeypatch.setattr(settings, "auth_username", CREDENTIALS["username"])
    monkeypatch.setattr(settings, "auth_password", CREDENTIALS["password"])
    monkeypatch.setattr(settings, "session_secret", "test-secret")
    monkeypatch.setattr(settings, "session_cookie_secure", False)


def test_token_round_trip():
    token = create_session_token("admin", now=1_000)
    assert verify_session_token(token, now=1_001) == "admin"


def test_expired_token_is_rejected(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "session_secret", "test-secret")
    token = create_session_token("admin", now=1_000)
    assert verify_session_token(token, now=1_000 + settings.session_ttl_minutes * 60) is None


def test_tampered_token_is_rejected(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "session_secret", "test-secret")
    payload, signature = create_session_token("admin", now=1_000).split(".")
    forged = create_session_token("someone-else", now=1_000).split(".")[0]
    assert verify_session_token(f"{forged}.{signature}", now=1_001) is None
    assert verify_session_token(f"{payload}.bad-signature", now=1_001) is None
    assert verify_session_token("not-a-token", now=1_001) is None


@pytest.mark.asyncio
async def test_todos_require_a_session(client: AsyncClient, auth_enabled: None):
    response = await client.get("/api/todos")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_login_sets_a_http_only_session_cookie(client: AsyncClient, auth_enabled: None):
    response = await client.post("/api/auth/login", json=CREDENTIALS)
    assert response.status_code == 200
    assert response.json() == {"username": "admin"}

    set_cookie = response.headers["set-cookie"]
    assert set_cookie.startswith(f"{SESSION_COOKIE}=")
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie

    todos = await client.get("/api/todos")
    assert todos.status_code == 200


@pytest.mark.asyncio
async def test_login_rejects_wrong_password(client: AsyncClient, auth_enabled: None):
    response = await client.post(
        "/api/auth/login", json={**CREDENTIALS, "password": "wrong"}
    )
    assert response.status_code == 401
    assert SESSION_COOKIE not in response.headers.get("set-cookie", "")


@pytest.mark.asyncio
async def test_logout_clears_the_session(client: AsyncClient, auth_enabled: None):
    await client.post("/api/auth/login", json=CREDENTIALS)

    response = await client.post("/api/auth/logout")
    assert response.status_code == 204

    todos = await client.get("/api/todos")
    assert todos.status_code == 401


@pytest.mark.asyncio
async def test_health_check_stays_public(client: AsyncClient, auth_enabled: None):
    response = await client.get("/api/health")
    assert response.status_code == 200
