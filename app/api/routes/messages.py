import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.database.session import get_db
from app.models.user import User
from app.schemas.message import (
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from app.services.agent_service import AgentService
from app.services.chat_service import ChatService
from app.services.message_service import MessageService


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/chats",
    tags=["Messages"],
)


@router.post(
    "/{chat_id}/messages",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    chat_id: int,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat = await ChatService.get_chat_by_id(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
    )

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    user_message = await MessageService.save_message(
        db=db,
        chat=chat,
        role="user",
        content=message_data.content,
    )

    recent_messages = await MessageService.get_recent_chat_messages(
        db=db,
        chat_id=chat.id,
        limit=settings.chat_history_limit,
    )

    langchain_messages = MessageService.to_langchain_messages(
        recent_messages
    )

    assistant_content = await AgentService.run(
        user_id=current_user.id,
        chat_id=chat.id,
        messages=langchain_messages,
        query=message_data.content,
    )

    assistant_message = await MessageService.save_message(
        db=db,
        chat=chat,
        role="assistant",
        content=assistant_content,
    )

    return ConversationResponse(
        user_message=user_message,
        assistant_message=assistant_message,
    )


@router.post("/{chat_id}/messages/stream")
async def stream_message(
    chat_id: int,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat = await ChatService.get_chat_by_id(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
    )

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    await MessageService.save_message(
        db=db,
        chat=chat,
        role="user",
        content=message_data.content,
    )

    recent_messages = await MessageService.get_recent_chat_messages(
        db=db,
        chat_id=chat.id,
        limit=settings.chat_history_limit,
    )

    langchain_messages = MessageService.to_langchain_messages(
        recent_messages
    )

    async def event_stream():
        chunks: list[str] = []

        try:
            async for chunk in AgentService.stream(
                user_id=current_user.id,
                chat_id=chat.id,
                messages=langchain_messages,
                query=message_data.content,
            ):
                if not chunk:
                    continue

                chunks.append(chunk)

                payload = json.dumps(
                    {"content": chunk},
                    ensure_ascii=False,
                )

                yield f"event: token\ndata: {payload}\n\n"

            assistant_content = "".join(chunks)

            if not assistant_content.strip():
                raise RuntimeError(
                    "Agent returned an empty assistant response"
                )

            assistant_message = await MessageService.save_message(
                db=db,
                chat=chat,
                role="assistant",
                content=assistant_content,
            )

            payload = json.dumps(
                {
                    "message_id": assistant_message.id,
                    "chat_id": chat.id,
                },
                ensure_ascii=False,
            )

            yield f"event: done\ndata: {payload}\n\n"

        except Exception:
            logger.exception(
                "SSE message streaming failed"
            )

            payload = json.dumps(
                {
                    "detail": (
                        "Failed to generate assistant response"
                    )
                },
                ensure_ascii=False,
            )

            yield f"event: error\ndata: {payload}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/{chat_id}/messages",
    response_model=list[MessageResponse],
)
async def get_chat_messages(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MessageResponse]:
    chat = await ChatService.get_chat_by_id(
        db=db,
        chat_id=chat_id,
        user_id=current_user.id,
    )

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    return await MessageService.get_chat_messages(
        db=db,
        chat_id=chat.id,
    )
