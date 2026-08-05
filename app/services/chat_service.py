from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat


class ChatService:
    """Provide persistence operations for user-owned chat records."""

    @staticmethod
    async def create_chat(
        db: AsyncSession,
        user_id: int,
        title: str,
    ) -> Chat:
        """Create and persist a chat for the specified user."""

        chat = Chat(
            user_id=user_id,
            title=title,
        )

        db.add(chat)
        await db.commit()
        await db.refresh(chat)

        return chat

    @staticmethod
    async def get_user_chats(
        db: AsyncSession,
        user_id: int,
    ) -> list[Chat]:
        """Return a user's chats ordered by most recent activity."""

        result = await db.execute(
            select(Chat)
            .where(Chat.user_id == user_id)
            .order_by(Chat.updated_at.desc())
        )

        return list(result.scalars().all())

    @staticmethod
    async def get_chat_by_id(
        db: AsyncSession,
        chat_id: int,
        user_id: int,
    ) -> Chat | None:
        """Return a chat only when it exists and belongs to the specified user."""

        result = await db.execute(
            select(Chat).where(
                Chat.id == chat_id,
                Chat.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_chat(
        db: AsyncSession,
        chat: Chat,
        title: str,
    ) -> Chat:
        """Update and persist the title of an existing chat."""

        chat.title = title

        await db.commit()
        await db.refresh(chat)

        return chat

    @staticmethod
    async def delete_chat(
        db: AsyncSession,
        chat: Chat,
    ) -> None:
        """Delete a chat and commit the transaction."""

        await db.delete(chat)
        await db.commit()
