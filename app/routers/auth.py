from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import User, RefreshToken
from ..schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest
)
from ..security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_refresh_token_expiry,
    hash_refresh_token
)
from ..dependencies import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role="USER"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == login_data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        login_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(user.id)

    refresh_token = create_refresh_token()

    refresh_token_record = RefreshToken(
        token_hash=hash_refresh_token(refresh_token),
        user_id=user.id,
        expires_at=get_refresh_token_expiry()
    )

    db.add(refresh_token_record)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    token_hash = hash_refresh_token(
        data.refresh_token
    )

    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked == False
    ).first()

    if not stored_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    if stored_token.expires_at < datetime.utcnow():
        stored_token.revoked = True
        db.commit()

        raise HTTPException(
            status_code=401,
            detail="Refresh token expired"
        )

    user = db.query(User).filter(
        User.id == stored_token.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    # Revoke old refresh token
    stored_token.revoked = True

    # Create new tokens
    new_access_token = create_access_token(user.id)

    new_refresh_token = create_refresh_token()

    new_refresh_token_record = RefreshToken(
        token_hash=hash_refresh_token(
            new_refresh_token
        ),
        user_id=user.id,
        expires_at=get_refresh_token_expiry()
    )

    db.add(new_refresh_token_record)
    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }