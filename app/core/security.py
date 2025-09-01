from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from passlib.context import CryptContext

from app.core.constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_HOURS,
    SECRET_KEY,
)
from app.schemas.token import TokenPair

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(data: Dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, str]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as e:
        raise ValueError("Invalid token") from e


def create_token_pair(data: Dict[str, Any]) -> TokenPair:
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(data, access_token_expires)

    refresh_token_expires = timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)
    refresh_token = create_token(data, refresh_token_expires)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        # Converted to Unix time
        access_expires_at=access_token_expires.total_seconds(),
        refresh_expires_at=refresh_token_expires.total_seconds(),
        token_type="Bearer",
    )
