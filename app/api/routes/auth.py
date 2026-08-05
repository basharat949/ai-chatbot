from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas import UserRegister, UserResponse
from app.schemas.user import RefreshTokenRequest
from app.services.auth_service import (
    login_user,
    logout_user,
    logout_all_devices,
    refresh_access_token,
    register_user,
)
from app.api.dependencies import get_current_user
from app.models import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """Register a user account and return its public profile."""

    try:
        return await register_user(
            db,
            user_data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Authenticate form credentials and return a bearer token pair."""

    try:
        return await login_user(
            db,
            email=form_data.username,
            password=form_data.password,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.post("/refresh")
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Rotate a valid refresh token and issue a new token pair."""

    try:
        return await refresh_access_token(
            db,
            token=token_data.refresh_token,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Revoke the refresh-token session submitted by the client."""

    try:
        await logout_user(
            db,
            token=token_data.refresh_token,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

@router.post("/logout-all")
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke every active refresh-token session for the current user."""

    revoked_sessions = await logout_all_devices(
        db,
        user_id=current_user.id,
    )

    return {
        "message": "Logged out from all devices",
        "revoked_sessions": revoked_sessions,
    }
