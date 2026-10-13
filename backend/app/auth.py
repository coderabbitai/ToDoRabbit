"""Signed session cookies for protecting the API."""

import base64
import hashlib
import hmac
import json
import time

from fastapi import Cookie, HTTPException, status

from app.config import settings

SESSION_COOKIE = "todorabbit_session"


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _sign(payload: str) -> str:
    digest = hmac.new(settings.session_secret.encode(), payload.encode(), hashlib.sha256).digest()
    return _b64encode(digest)


def create_session_token(username: str, now: float | None = None) -> str:
    """Create a signed token that expires after ``session_ttl_minutes``."""
    issued_at = time.time() if now is None else now
    claims = {"sub": username, "exp": int(issued_at + settings.session_ttl_minutes * 60)}
    payload = _b64encode(json.dumps(claims, separators=(",", ":")).encode())
    return f"{payload}.{_sign(payload)}"


def verify_session_token(token: str, now: float | None = None) -> str | None:
    """Return the username for a valid, unexpired token, otherwise ``None``."""
    payload, separator, signature = token.partition(".")
    if not separator or not hmac.compare_digest(signature, _sign(payload)):
        return None

    try:
        claims = json.loads(_b64decode(payload))
        expires_at = int(claims["exp"])
        username = str(claims["sub"])
    except (ValueError, KeyError, TypeError):
        return None

    if expires_at <= (time.time() if now is None else now):
        return None
    return username


async def require_session(
    session: str | None = Cookie(None, alias=SESSION_COOKIE),
) -> str:
    """Dependency that rejects requests without a valid session cookie."""
    if not settings.auth_enabled:
        return "anonymous"

    username = verify_session_token(session) if session else None
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return username
