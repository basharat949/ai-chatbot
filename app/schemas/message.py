from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    """Validate message content submitted by a user."""

    content: str = Field(
        min_length=1,
        max_length=20_000,
    )


class MessageResponse(BaseModel):
    """Serialize a stored conversation message returned by the API."""

    id: int
    chat_id: int
    role: Literal[
        "user",
        "assistant",
        "system",
    ]
    content: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class ConversationResponse(BaseModel):
    """Group the persisted user and assistant messages for one interaction."""

    user_message: MessageResponse
    assistant_message: MessageResponse
