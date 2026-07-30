from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import (
    hash_password,
    verify_password,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
)

from app.models import User
from app.schemas.user import (
    UserLogin,
    UserRegister,
    UserResponse,
    TokenResponse,
)
from datetime import datetime
from app.core.security import hash_token
from app.models.refresh_token import RefreshToken


async def register_user(
    db: AsyncSession,
    user_data: UserRegister,
) -> User:
    result = await db.execute(
        select(User).where(
            or_(
                User.email == user_data.email,
                User.username == user_data.username,
            )
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        if existing_user.email == user_data.email:
            raise ValueError("Email is already registered")

        raise ValueError("Username is already taken")

    user = User(
        email=user_data.email,
        username=user_data.username,
        date_of_birth=user_data.date_of_birth,
        hashed_password=hash_password(user_data.password),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user

async def authenticate_user(
    db: AsyncSession,
    login_data: UserLogin,
) -> User:
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise ValueError("Invalid email or password")

    if not verify_password(
        login_data.password,
        user.hashed_password,
    ):
        raise ValueError("Invalid email or password")

    if not user.is_active:
        raise ValueError("User account is inactive")

    return user

async def save_refresh_token(
    db: AsyncSession,
    *,
    user_id: int,
    token: str,
    jti: str,
    expires_at: datetime,
) -> RefreshToken:
    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=hash_token(token),
        jti=jti,
        expires_at=expires_at,
    )

    db.add(refresh_token)
    await db.commit()
    await db.refresh(refresh_token)

    return refresh_token

async def login_user(
    db: AsyncSession,
    *,
    email: str,
    password: str,
) -> dict[str, str]:
    login_data = UserLogin(
        email=email,
        password=password,
    )

    user = await authenticate_user(
        db=db,
        login_data=login_data,
    )

    access_token = create_access_token(
        subject=str(user.id),
    )

    refresh_token, jti, expires_at = create_refresh_token(
        subject=str(user.id),
    )

    await save_refresh_token(
        db,
        user_id=user.id,
        token=refresh_token,
        jti=jti,
        expires_at=expires_at,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
    user = await authenticate_user(
        db=db,
        email=email,
        password=password,
    )

    access_token = create_access_token(
        subject=str(user.id),
    )

    refresh_token, jti, expires_at = create_refresh_token(
        subject=str(user.id),
    )

    await save_refresh_token(
        db,
        user_id=user.id,
        token=refresh_token,
        jti=jti,
        expires_at=expires_at,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }