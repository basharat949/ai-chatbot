from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.chat import ChatCreate, ChatResponse, ChatUpdate
from app.services.chat_service import ChatService


router = APIRouter(
    prefix="/chats",
    tags=["Chats"],
)


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_chat(
    chat_data: ChatCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    title = chat_data.title

    if title is None or not title.strip() or title.strip() == "{}":
        title = "New Chat"
    else:
        title = title.strip()

    chat = await ChatService.create_chat(
        db=db,
        user_id=current_user.id,
        title=title,
    )

    return chat


@router.get(
    "",
    response_model=list[ChatResponse],
)
async def get_user_chats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ChatService.get_user_chats(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{chat_id}",
    response_model=ChatResponse,
)
async def get_chat_by_id(
    chat_id: int,
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

    return chat
    
@router.patch(
    "/{chat_id}",
    response_model=ChatResponse,
)
async def update_chat(
    chat_id: int,
    chat_data: ChatUpdate,
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

    return await ChatService.update_chat(
        db=db,
        chat=chat,
        title=chat_data.title,
    )

@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_chat(
    chat_id: int,
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

    await ChatService.delete_chat(
        db=db,
        chat=chat,
    )  