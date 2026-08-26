from datetime import datetime, timedelta, timezone
import secrets
import os
import hashlib
import jwt
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set"
    )

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    password: str,
    hashed_password: str
) -> bool:
    return password_hash.verify(
        password,
        hashed_password
    )


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=30
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise ValueError("Missing user ID")

        return int(user_id)

    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")

    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def get_refresh_token_expiry() -> datetime:
    return datetime.utcnow() + timedelta(days=7)

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()