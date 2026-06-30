import bcrypt

BCRYPT_MAX_BYTES = 72


def hash_password(plain: str) -> str:
    payload = plain.encode("utf-8")
    if len(payload) > BCRYPT_MAX_BYTES:
        raise ValueError("senha muito longa")
    return bcrypt.hashpw(payload, bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8")[:BCRYPT_MAX_BYTES], hashed.encode())
    except (TypeError, ValueError):
        return False


def validate_password(plain: str) -> bool:
    return bool(plain) and len(plain.encode("utf-8")) <= BCRYPT_MAX_BYTES

