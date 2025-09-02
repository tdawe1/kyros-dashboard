"""
Authentication and authorization module for Kyros Dashboard.
Implements JWT-based authentication with role-based access control.
"""

import os
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Security configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing
PASSWORD_SALT_ROUNDS = 12

# Security scheme
security = HTTPBearer()


# User roles
class UserRole:
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"


# Pydantic models
class User(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = UserRole.USER


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None


# Password utilities
def hash_password(password: str) -> str:
    """Hash password using PBKDF2 with salt."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    )
    return f"{salt}:{pwd_hash.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    try:
        salt, pwd_hash = hashed_password.split(":")
        pwd_hash_bytes = bytes.fromhex(pwd_hash)
        new_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return secrets.compare_digest(pwd_hash_bytes, new_hash)
    except (ValueError, TypeError):
        return False


# JWT utilities
def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> TokenData:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        # Verify token type
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        role: str = payload.get("role")

        if user_id is None or username is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenData(user_id=user_id, username=username, role=role)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# User management (in-memory for demo - replace with database in production)
_users_db: Dict[str, User] = {}
_user_credentials: Dict[str, str] = {}  # username -> hashed_password


def create_default_admin():
    """Create default admin user if none exists."""
    admin_username = "admin"
    if admin_username not in _user_credentials:
        admin_password = os.getenv("ADMIN_PASSWORD", secrets.token_urlsafe(16))
        _user_credentials[admin_username] = hash_password(admin_password)
        _users_db[admin_username] = User(
            id="admin",
            username=admin_username,
            email="admin@kyros.com",
            role=UserRole.ADMIN,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        logger.info("Created default admin user")


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password."""
    if username not in _user_credentials:
        return None

    if not verify_password(password, _user_credentials[username]):
        return None

    user = _users_db.get(username)
    if not user or not user.is_active:
        return None

    # Update last login
    user.last_login = datetime.utcnow()

    return user


def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username."""
    return _users_db.get(username)


def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID."""
    for user in _users_db.values():
        if user.id == user_id:
            return user
    return None


# Dependency functions
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    token_data = verify_token(token)

    user = get_user_by_id(token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def require_role(required_role: str):
    """Decorator to require specific role."""

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return role_checker


def require_roles(required_roles: List[str]):
    """Decorator to require one of specific roles."""

    def roles_checker(current_user: User = Depends(get_current_user)) -> User:
        if (
            current_user.role not in required_roles
            and current_user.role != UserRole.ADMIN
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return roles_checker


# Initialize default admin user
create_default_admin()
