from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatCreate(BaseModel):
    """Validate the optional title supplied when creating a chat."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

class ChatUpdate(BaseModel):
    """Validate a title change for an existing chat."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )


class ChatResponse(BaseModel):
    """Serialize chat metadata returned by the API."""

    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
