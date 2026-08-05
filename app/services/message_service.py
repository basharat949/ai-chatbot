from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat
from app.models.message import Message
from app.services.title_service import TitleService


MessageRole = Literal[
    "user",
    "assistant",
    "system",
]


class MessageService:
    """Coordinate message persistence and fallback chat-title generation."""

    @staticmethod
    async def save_message(
        db: AsyncSession,
        *,
        chat: Chat,
        role: MessageRole,
        content: str,
    ) -> Message:
        """Persist a message and initialize the chat title when appropriate."""

        message = Message(
            chat_id=chat.id,
            role=role,
            content=content,
        )

        db.add(message)

        if role == "user" and chat.title == "New Chat":
            chat.title = TitleService.generate_fallback_title(
                content,
            )

        await db.commit()
        await db.refresh(message)
        await db.refresh(chat)

        return message
