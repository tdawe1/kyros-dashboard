from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from .models import User as UserModel
from .schemas import UserCreate
from .security import hash_password, verify_password


def get_user_by_username(db: Session, username: str) -> Optional[UserModel]:
    """Get user by username."""
    return db.query(UserModel).filter(UserModel.username == username).first()


def get_user_by_id(db: Session, user_id: UUID) -> Optional[UserModel]:
    """Get user by ID."""
    return db.query(UserModel).filter(UserModel.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserModel]:
    """Get all users."""
    return db.query(UserModel).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> UserModel:
    """Create a new user."""
    try:
        hashed_password = hash_password(user.password)
        db_user = UserModel(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            role=user.role,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        if "username" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
        elif "email" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User creation failed due to constraint violation",
            )


def authenticate_user(db: Session, username: str, password: str) -> Optional[UserModel]:
    """Authenticate user with username and password."""
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user_active_status(
    db: Session, user: UserModel, is_active: bool
) -> UserModel:
    """Update user's active status."""
    user.is_active = is_active
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user_from_db(db: Session, user: UserModel):
    """Delete a user from the database."""
    db.delete(user)
    db.commit()
    return
