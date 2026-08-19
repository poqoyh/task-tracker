import bcrypt


def hash_password(
    password: str,
) -> str:
    return bcrypt.hashpw(
        password.encode(),
        salt=bcrypt.gensalt(),
    ).decode()


def validate_password(
    password: str,
    hashed_password: str,
) -> bool:
    return bcrypt.checkpw(
        password.encode(),
        hashed_password.encode(),
    )
