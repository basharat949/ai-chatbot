from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=20_000,
    )


class MessageResponse(BaseModel):
    id: int
    chat_id: int
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )