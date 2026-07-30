from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas import UserRegister, UserResponse
from app.services.auth_service import register_user

from app.core.security import create_access_token
from app.schemas import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)

from app.services.auth_service import (
    authenticate_user,
    register_user,
)

from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await register_user(db, user_data)
        return user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    db: AsyncSession = Depends(get_db),
):
    try:
        login_data = UserLogin(
            email=form_data.username,
            password=form_data.password,
        )

        user = await authenticate_user(db, login_data)

        access_token = create_access_token(
            subject=str(user.id),
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        ) from error