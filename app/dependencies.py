from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .security import decode_access_token
from .permissions import PERMISSIONS


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        user_id = decode_access_token(token)

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


def require_roles(*allowed_roles: str):
    def role_checker(
        current_user: User = Depends(get_current_user)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission"
            )

        return current_user

    return role_checker


def require_permission(permission: str):
    def permission_checker(
        current_user: User = Depends(get_current_user)
    ):
        user_permissions = PERMISSIONS.get(
            current_user.role,
            set()
        )

        if permission not in user_permissions:
            raise HTTPException(
                status_code=403,
                detail="You do not have this permission"
            )

        return current_user

    return permission_checker