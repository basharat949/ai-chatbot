from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models import User
from app.schemas import UserRegister


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