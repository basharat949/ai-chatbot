from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat


class ChatService:
    @staticmethod
    async def create_chat(
        db: AsyncSession,
        user_id: int,
        title: str,
    ) -> Chat:
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
        chat.title = title

        await db.commit()
        await db.refresh(chat)

        return chat

    @staticmethod
    async def delete_chat(
        db: AsyncSession,
        chat: Chat,
    ) -> None:
        await db.delete(chat)
        await db.commit()