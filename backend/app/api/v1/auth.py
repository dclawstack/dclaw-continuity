from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.schemas.auth import (
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserRead,
)
from app.services import auth_service

router = APIRouter()


@router.post(
    "/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    payload: SignupRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await auth_service.signup(db, payload)
    except auth_service.EmailAlreadyTaken:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email already registered",
        )
    token, ttl = auth_service.issue_token(user)
    return TokenResponse(
        access_token=token,
        expires_in=ttl,
        user=UserRead.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await auth_service.authenticate(db, payload.email, payload.password)
    except auth_service.InvalidCredentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password",
        )
    token, ttl = auth_service.issue_token(user)
    return TokenResponse(
        access_token=token,
        expires_in=ttl,
        user=UserRead.model_validate(user),
    )


@router.get("/me", response_model=UserRead)
async def me(
    current: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current.user_id
    if user_id is None:
        # Dev-token user has no DB row — synthesize.
        return UserRead(
            id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            email=current.email or "dev@local",
            is_active=True,
            is_superuser=False,
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
    user = await auth_service.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found"
        )
    return user
