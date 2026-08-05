from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    """Validate the account details required to register a user."""

    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    date_of_birth: date | None = None


class UserResponse(BaseModel):
    """Serialize public account details without exposing credentials."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    date_of_birth: date | None
    is_active: bool
    created_at: datetime

class UserLogin(BaseModel):
    """Validate credentials submitted for authentication."""

    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Serialize a bearer access token returned after authentication."""

    access_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    """Validate a refresh token submitted for rotation or logout."""

    refresh_token: str
