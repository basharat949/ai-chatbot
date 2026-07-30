from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    hash_token,
    verify_password,
    verify_token_hash,
)
from app.models import User
from app.models.refresh_token import RefreshToken
from app.schemas.user import (
    UserLogin,
    UserRegister,
)


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
        select(User).where(
            User.email == login_data.email,
        )
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


async def refresh_access_token(
    db: AsyncSession,
    *,
    token: str,
) -> dict[str, str]:
    payload = decode_refresh_token(token)

    user_id = payload.get("sub")
    jti = payload.get("jti")

    if not user_id:
        raise ValueError("Refresh token missing subject")

    if not jti:
        raise ValueError("Refresh token missing jti")

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.jti == jti,
        )
    )

    stored_token = result.scalar_one_or_none()

    if stored_token is None:
        raise ValueError("Refresh session not found")

    if stored_token.revoked_at is not None:
        raise ValueError("Refresh token has been revoked")

    if stored_token.expires_at <= datetime.now(timezone.utc):
        raise ValueError("Refresh token has expired")

    if stored_token.user_id != int(user_id):
        raise ValueError("Invalid refresh token owner")

    if not verify_token_hash(
        token,
        stored_token.token_hash,
    ):
        raise ValueError("Invalid refresh token")

    new_access_token = create_access_token(
        subject=str(user_id),
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }