import jwt
from core.config import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth.private_key_path.read_text(),
    algorithm: str = settings.auth.algorithm,
):
    encoded = jwt.encode(
        payload=payload,
        key=private_key,
        algorithm=algorithm,
    )

    return encoded


def decode_jwt(
    token: str | bytes,
    public_key=settings.auth.public_key_paths.read_text(),
    algorithm: str = settings.auth.algorithm,
):
    decoded = jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=[algorithm],
    )

    return decoded
