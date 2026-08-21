from datetime import timedelta, datetime, timezone

import jwt
from core.config import settings

from functools import lru_cache


@lru_cache
def get_private_key() -> str:
    return settings.auth.private_key_path.read_text()


@lru_cache
def get_public_key() -> str:
    return settings.auth.public_key_path.read_text()


def encode_jwt(
    payload: dict,
    algorithm: str = settings.auth.algorithm,
    expire_minutes: int = settings.auth.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
):
    to_encode = payload.copy()

    now = datetime.now(timezone.utc)

    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)

    to_encode.update(
        exp=expire,
        iat=now,
    )

    encoded = jwt.encode(
        to_encode,
        key=get_private_key(),
        algorithm=algorithm,
    )

    return encoded


def decode_jwt(
    token: str | bytes,
    algorithm: str = settings.auth.algorithm,
):
    decoded = jwt.decode(
        jwt=token,
        key=get_public_key(),
        algorithms=[algorithm],
    )

    return decoded


def create_access_token(user):
    return encode_jwt(
        {
            "sub": str(user.id),
            "user": user.username,
            "type": "access",
        },
    )


def create_refresh_token(user):
    return encode_jwt(
        {
            "sub": str(user.id),
            "type": "refresh",
        },
        expire_timedelta=timedelta(days=settings.auth.refresh_token_expire_days),
    )
