from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from jwt import DecodeError, ExpiredSignatureError, InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()


# ------------------------
# Password
# ------------------------

def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


# ------------------------
# Access Token
# ------------------------

def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(
            minutes=settings.access_token_expire_minutes,
        )
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


# ------------------------
# Refresh Token
# ------------------------

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


# ------------------------
# Generic Token Decoder
# ------------------------

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

    except ExpiredSignatureError:
        raise ValueError("Token has expired")

    except DecodeError:
        raise ValueError("Invalid token")

    except InvalidTokenError:
        raise ValueError("Invalid token")


# ------------------------
# Access Token Decoder
# ------------------------

def decode_access_token(
    token: str,
) -> dict:
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise ValueError("Invalid access token")

    return payload


# ------------------------
# Refresh Token Decoder
# ------------------------

def decode_refresh_token(
    token: str,
) -> dict:
    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")

    if not payload.get("jti"):
        raise ValueError("Refresh token missing jti")

    return payload


# ------------------------
# Token Hashing
# ------------------------

def hash_token(
    token: str,
) -> str:
    return password_hash.hash(token)


def verify_token_hash(
    plain_token: str,
    token_hash: str,
) -> bool:
    return password_hash.verify(
        plain_token,
        token_hash,
    )