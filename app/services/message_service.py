from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat
from app.models.message import Message
from app.services.title_service import TitleService


class MessageService:
    @staticmethod
    async def create_user_message(
        db: AsyncSession,
        *,
        chat: Chat,
        content: str,
    ) -> Message:
        message = Message(
            chat_id=chat.id,
            role="user",
            content=content,
        )

        db.add(message)

        if not chat.title or chat.title in {"New Chat", "{}"}:
            chat.title = TitleService.generate_fallback_title(
                content,
            )

        await db.commit()
        await db.refresh(message)
        await db.refresh(chat)

        return message