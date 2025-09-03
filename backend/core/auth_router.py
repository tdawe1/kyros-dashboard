"""
Authentication router for Kyros Dashboard.
Handles login, logout, token refresh, and user management.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .database import get_db
from .auth.schemas import User, UserLogin, Token, UserRole
from .auth.dependencies import get_current_user, require_role
from .auth.service import (
    authenticate_user,
    get_users,
    create_user as create_user_in_db,
    get_user_by_username,
    update_user_active_status,
    delete_user_from_db,
)
from .auth.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
)
from .models import User as UserModel
from .input_validation import SecureUserCreate
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access and refresh tokens.
    """
    user = authenticate_user(
        db, username=user_credentials.username, password=user_credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role}
    )

    logger.info(f"User {user.username} logged in successfully")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends()):
    """
    Refresh access token using refresh token.
    """
    refresh_token = credentials.credentials
    token_data = verify_token(refresh_token, token_type="refresh")

    # Create new access token
    access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": token_data.user_id,
            "username": token_data.username,
            "role": token_data.role,
        },
        expires_delta=access_token_expires,
    )

    # Create new refresh token
    new_refresh_token = create_refresh_token(
        data={
            "sub": token_data.user_id,
            "username": token_data.username,
            "role": token_data.role,
        }
    )

    logger.info(f"Token refreshed for user {token_data.username}")

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=User)
async def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    """
    Get current user information.
    """
    return current_user


@router.post("/logout")
async def logout(current_user: UserModel = Depends(get_current_user)):
    """
    Logout user (client should discard tokens).
    """
    logger.info(f"User {current_user.username} logged out")
    return {"message": "Successfully logged out"}


async def list_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(require_role(UserRole.ADMIN)),
):
    """
    List all users (admin only).
    """
    users = get_users(db, skip=skip, limit=limit)
    return users


@router.post("/users", response_model=User)
async def create_user(
    user_data: SecureUserCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(UserRole.ADMIN)),
):
    """
    Create new user (admin only).
    """
    db_user = get_user_by_username(db, username=user_data.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    new_user = create_user_in_db(db=db, user=user_data)
    logger.info(f"User {new_user.username} created by {current_user.username}")
    return new_user


@router.put("/users/{username}/activate")
async def toggle_user_status(
    username: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(UserRole.ADMIN)),
):
    """
    Toggle user active status (admin only).
    """
    user_to_update = get_user_by_username(db, username=username)
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    updated_user = update_user_active_status(
        db, user=user_to_update, is_active=not user_to_update.is_active
    )

    logger.info(
        f"User {username} status changed to {'active' if updated_user.is_active else 'inactive'} by {current_user.username}"
    )

    return {
        "message": f"User {username} is now {'active' if updated_user.is_active else 'inactive'}"
    }


@router.delete("/users/{username}")
async def delete_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role(UserRole.ADMIN)),
):
    """
    Delete user (admin only).
    """
    user_to_delete = get_user_by_username(db, username=username)
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user_to_delete.username == current_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    delete_user_from_db(db, user=user_to_delete)

    logger.info(f"User {username} deleted by {current_user.username}")

    return {"message": f"User {username} deleted successfully"}
