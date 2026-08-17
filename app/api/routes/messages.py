from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.message import (
    ConversationResponse,
    MessageCreate,
    MessageResponse 
)
from app.services.agent_service import AgentService
from app.services.chat_service import ChatService
from app.services.message_service import MessageService


router = APIRouter(
    prefix="/chats",
    tags=["Messages"],
)


@router.post(
    "/{chat_id}/messages",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
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

    db_messages = await MessageService.get_chat_messages(
        db=db,
        chat_id=chat.id,
    )

    langchain_messages = MessageService.to_langchain_messages(
        db_messages
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
