"""
Auth API Router — Register, Login, Refresh, Me
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token, decode_token
)
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import (
    UserRegister, UserLogin, AuthTokens, UserResponse,
    TokenRefresh, MessageResponse
)
from app.utils.logger import logger

router = APIRouter()


@router.post("/register", response_model=AuthTokens, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account."""
    clean_email = payload.email.strip().lower()
    existing = db.query(User).filter(User.email.ilike(clean_email)).first()
    if existing:
        logger.warning(f"Registration attempted for existing email: {clean_email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    # Create user
    user = User(
        email=clean_email,
        full_name=payload.full_name.strip(),
        hashed_password=get_password_hash(payload.password),
        organization=payload.organization.strip() if payload.organization else None,
        is_verified=True,  # Auto-verify for now (no email flow)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"New user registered: {user.email} (ID: {user.id})")

    # Issue tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return AuthTokens(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=AuthTokens)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    clean_email = payload.email.strip().lower()
    user = db.query(User).filter(User.email.ilike(clean_email)).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        logger.warning(f"Invalid login attempt for email: {clean_email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        logger.warning(f"Login attempt for deactivated user: {clean_email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated.",
        )

    logger.info(f"Successful login for user: {user.email} (ID: {user.id})")
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return AuthTokens(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=AuthTokens)
def refresh_token(payload: TokenRefresh, db: Session = Depends(get_db)):
    """Refresh access token using a valid refresh token."""
    token_data = decode_token(payload.refresh_token)

    if not token_data or token_data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    user_id = token_data.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated.",
        )

    access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    return AuthTokens(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return current_user


@router.post("/logout", response_model=MessageResponse)
def logout():
    """Logout endpoint — logs out user."""
    return MessageResponse(message="Successfully logged out.")
