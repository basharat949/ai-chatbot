from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from jwt import DecodeError, ExpiredSignatureError, InvalidTokenError
from uuid import uuid4

import jwt

from app.core.config import settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.access_token_expire_minutes)
    )

    payload = {
        "sub": subject,
        "exp": expire,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        if payload.get("type") != "access":
            raise InvalidTokenError("Invalid token type")

        return payload

    except ExpiredSignatureError:
        raise ValueError("Token has expired")

    except DecodeError:
        raise ValueError("Invalid token")

    except InvalidTokenError:
        raise ValueError("Invalid token")

def create_refresh_token(
    subject: str,
) -> tuple[str, str, datetime]:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days,
    )

    jti = str(uuid4())

    payload = {
        "sub": subject,
        "exp": expire,
        "type": "refresh",
        "jti": jti,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return token, jti, expire

def hash_token(token: str) -> str:
    return password_hash.hash(token)


def verify_token_hash(
    plain_token: str,
    token_hash: str,
) -> bool:
    return password_hash.verify(
        plain_token,
        token_hash,
    )