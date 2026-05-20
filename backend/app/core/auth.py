"""Auth dependency.

Verifies bearer tokens issued by `auth_service.issue_token`. When
`AUTH_DEV_MODE` is on, also accepts the static `DEV_AUTH_TOKEN` for local dev
and tests so the rest of the codebase doesn't need a real user during smoke runs.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    sub: str
    email: str | None = None
    is_superuser: bool = False
    is_dev: bool = False

    @property
    def user_id(self) -> uuid.UUID | None:
        try:
            return uuid.UUID(self.sub)
        except (ValueError, TypeError):
            return None


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = creds.credentials

    if settings.auth_dev_mode and token == settings.dev_auth_token:
        return CurrentUser(sub="dev-user", email="dev@local", is_dev=True)

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token claims")

    return CurrentUser(
        sub=sub,
        email=payload.get("email"),
        is_superuser=bool(payload.get("is_superuser", False)),
    )
