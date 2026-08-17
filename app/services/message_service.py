from typing import Literal
from unittest import result

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat
from app.models.message import Message
from app.services.title_service import TitleService
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)


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

    @staticmethod
    async def get_chat_messages(
        db: AsyncSession,
        *,
        chat_id: int,
    ) -> list[Message]:
        result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(
            Message.created_at.asc(),
            Message.id.asc(),
        )
    )

        return list(result.scalars().all())

    @staticmethod
    def to_langchain_messages(
    messages: list[Message],
    ) -> list[BaseMessage]:
        langchain_messages: list[BaseMessage] = []
        for message in messages:
            if message.role == "user":
                langchain_messages.append(
                    HumanMessage(content=message.content)
                )

            elif message.role == "assistant":
                langchain_messages.append(
                    AIMessage(content=message.content)
                )

        return langchain_messages
