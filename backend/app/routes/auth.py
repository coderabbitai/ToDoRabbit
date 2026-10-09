"""Login and logout endpoints."""

import hmac

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel

from app.auth import SESSION_COOKIE, create_session_token
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """Credentials submitted to start a session."""

    username: str
    password: str


class SessionResponse(BaseModel):
    """The user a session belongs to."""

    username: str


def _matches(provided: str, expected: str) -> bool:
    return hmac.compare_digest(provided.encode(), expected.encode())


@router.post("/login", response_model=SessionResponse)
async def login(credentials: LoginRequest, response: Response) -> SessionResponse:
    """Exchange the configured credentials for a session cookie."""
    if not settings.auth_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Authentication is disabled")

    username_ok = _matches(credentials.username, settings.auth_username)
    password_ok = _matches(credentials.password, settings.auth_password)
    if not (username_ok and password_ok):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    response.set_cookie(
        SESSION_COOKIE,
        create_session_token(credentials.username),
        max_age=settings.session_ttl_minutes * 60,
        httponly=True,
        samesite="lax",
        secure=settings.session_cookie_secure,
    )
    return SessionResponse(username=credentials.username)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    """End the current session."""
    response.delete_cookie(SESSION_COOKIE, httponly=True, samesite="lax")
