"""
Authentication router for Kyros Dashboard.
Handles login, logout, token refresh, and user management.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from typing import List

from .auth import (
    User,
    UserLogin,
    Token,
    authenticate_user,
    get_current_user,
    require_role,
    UserRole,
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_password,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
)
from .input_validation import SecureUserCreate
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """
    Authenticate user and return access and refresh tokens.
    """
    user = authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(
        data={"sub": user.id, "username": user.username, "role": user.role}
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
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    """
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user (client should discard tokens).
    """
    logger.info(f"User {current_user.username} logged out")
    return {"message": "Successfully logged out"}


@router.get("/users", response_model=List[User])
async def list_users(current_user: User = Depends(require_role(UserRole.ADMIN))):
    """
    List all users (admin only).
    """
    from .auth import _users_db

    return list(_users_db.values())


@router.post("/users", response_model=User)
async def create_user(
    user_data: SecureUserCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Create new user (admin only).
    """
    from .auth import _users_db, _user_credentials

    if user_data.username in _users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    # Hash password
    hashed_password = hash_password(user_data.password)
    _user_credentials[user_data.username] = hashed_password

    # Create user
    new_user = User(
        id=user_data.username,  # Simple ID for demo
        username=user_data.username,
        email=user_data.email,
        role=user_data.role,
        is_active=True,
        created_at=datetime.utcnow(),
    )
    _users_db[user_data.username] = new_user

    logger.info(f"User {user_data.username} created by {current_user.username}")

    return new_user


@router.put("/users/{username}/activate")
async def toggle_user_status(
    username: str, current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Toggle user active status (admin only).
    """
    from .auth import _users_db

    if username not in _users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user = _users_db[username]
    user.is_active = not user.is_active

    logger.info(
        f"User {username} status changed to {'active' if user.is_active else 'inactive'} by {current_user.username}"
    )

    return {
        "message": f"User {username} is now {'active' if user.is_active else 'inactive'}"
    }


@router.delete("/users/{username}")
async def delete_user(
    username: str, current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Delete user (admin only).
    """
    from .auth import _users_db, _user_credentials

    if username not in _users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if username == current_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    del _users_db[username]
    del _user_credentials[username]

    logger.info(f"User {username} deleted by {current_user.username}")

    return {"message": f"User {username} deleted successfully"}
