"""Password hashing + JWT issuance/verification for session auth."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User
from app.schemas.auth import SignupRequest


class AuthError(Exception):
    pass


class EmailAlreadyTaken(AuthError):
    pass


class InvalidCredentials(AuthError):
    pass


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def issue_token(user: User) -> tuple[str, int]:
    """Returns (jwt, expires_in_seconds)."""

    ttl = settings.access_token_expire_minutes * 60
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl)).timestamp()),
        "is_superuser": user.is_superuser,
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token, ttl


def decode_token(token: str) -> dict:
    """Raises jwt.PyJWTError subclasses on any verification failure."""

    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])


async def signup(db: AsyncSession, payload: SignupRequest) -> User:
    existing = (
        await db.execute(select(User).where(User.email == payload.email.lower()))
    ).scalar_one_or_none()
    if existing is not None:
        raise EmailAlreadyTaken(payload.email)

    user = User(
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate(
    db: AsyncSession, email: str, password: str
) -> User:
    user = (
        await db.execute(select(User).where(User.email == email.lower()))
    ).scalar_one_or_none()
    if user is None or not user.is_active:
        raise InvalidCredentials("user not found or inactive")
    if not verify_password(password, user.hashed_password):
        raise InvalidCredentials("bad password")
    return user


async def get_user_by_id(
    db: AsyncSession, user_id: uuid.UUID
) -> Optional[User]:
    return (
        await db.execute(select(User).where(User.id == user_id))
    ).scalar_one_or_none()
