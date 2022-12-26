import bcrypt

from constants.default import UTF_8


def create_random_salt() -> bytes:
    return bcrypt.gensalt()


def create_password_hash(password: bytes | str, salt: bytes) -> str:
    if isinstance(password, str):
        password = password.encode(UTF_8)

    return bcrypt.hashpw(password, salt).decode(UTF_8)


def check_password_hash(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(UTF_8), hashed_password.encode(UTF_8))
