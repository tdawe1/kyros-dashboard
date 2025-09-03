"""
Input validation and sanitization for Kyros Dashboard.
Implements comprehensive input validation, sanitization, and security checks.
"""

import re
import bleach
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator
import logging

logger = logging.getLogger(__name__)

# Security patterns
SQL_INJECTION_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
    r"(--|#|/\*|\*/)",
    r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
    r"(\b(OR|AND)\s+'.*'\s*=\s*'.*')",
]

XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe[^>]*>",
    r"<object[^>]*>",
    r"<embed[^>]*>",
]

# Allowed HTML tags for content
ALLOWED_HTML_TAGS = [
    "p",
    "br",
    "strong",
    "em",
    "u",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "blockquote",
    "a",
    "code",
    "pre",
]

# Allowed HTML attributes
ALLOWED_HTML_ATTRIBUTES = {"a": ["href", "title"], "code": ["class"], "pre": ["class"]}


class InputValidator:
    """Comprehensive input validation and sanitization."""

    @staticmethod
    def sanitize_text(text: str, max_length: int = 100000) -> str:
        """Sanitize text input by removing dangerous content."""
        if not isinstance(text, str):
            raise ValueError("Input must be a string")

        # Check length
        if len(text) > max_length:
            raise ValueError(f"Input exceeds maximum length of {max_length} characters")

        # Remove null bytes
        text = text.replace("\x00", "")

        # Check for SQL injection patterns
        for pattern in SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {pattern}")
                raise ValueError("Invalid input detected")

        # Check for XSS patterns
        for pattern in XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Potential XSS detected: {pattern}")
                raise ValueError("Invalid input detected")

        # Clean HTML using bleach (handles escaping internally)
        text = bleach.clean(
            text, tags=ALLOWED_HTML_TAGS, attributes=ALLOWED_HTML_ATTRIBUTES
        )

        return text.strip()

    @staticmethod
    def validate_username(username: str) -> str:
        """Validate and sanitize username."""
        if not username or not isinstance(username, str):
            raise ValueError("Username is required")

        username = username.strip()

        # Check length
        if len(username) < 3 or len(username) > 50:
            raise ValueError("Username must be between 3 and 50 characters")

        # Check format (alphanumeric, underscore, hyphen only)
        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )

        return username.lower()

    @staticmethod
    def validate_email(email: str) -> str:
        """Validate and sanitize email address."""
        if not email or not isinstance(email, str):
            raise ValueError("Email is required")

        email = email.strip().lower()

        # Basic email regex
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")

        # Check length
        if len(email) > 254:
            raise ValueError("Email address too long")

        return email

    @staticmethod
    def validate_url(url: str) -> str:
        """Validate and sanitize URL."""
        if not url or not isinstance(url, str):
            raise ValueError("URL is required")

        url = url.strip()

        # Parse URL using urllib.parse for robust validation
        try:
            parsed = urlparse(url)
        except Exception:
            raise ValueError("Invalid URL format")

        # Check if scheme and netloc are present
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")

        # Check for allowed protocols
        allowed_schemes = {"http", "https"}
        if parsed.scheme.lower() not in allowed_schemes:
            raise ValueError("Only HTTP and HTTPS URLs are allowed")

        # Check for dangerous protocols
        if parsed.scheme.lower() in {"javascript", "data", "vbscript", "file"}:
            raise ValueError("Dangerous URL protocol detected")

        return url


# Pydantic models with validation
class SecureGenerateRequest(BaseModel):
    """Secure version of GenerateRequest with validation."""

    input_text: str = Field(..., min_length=100, max_length=100000)
    channels: List[str] = Field(..., min_items=1, max_items=10)
    tone: str = Field(..., min_length=1, max_length=50)
    preset: str = Field(default="default", max_length=100)
    model: Optional[str] = Field(None, max_length=100)

    @field_validator("input_text")
    def validate_input_text(cls, v):
        return InputValidator.sanitize_text(v)

    @field_validator("channels")
    def validate_channels(cls, v):
        valid_channels = ["linkedin", "twitter", "newsletter", "blog"]
        for channel in v:
            if channel not in valid_channels:
                raise ValueError(f"Invalid channel: {channel}")
        return v

    @field_validator("tone")
    def validate_tone(cls, v):
        valid_tones = ["professional", "casual", "engaging", "formal", "friendly"]
        if v not in valid_tones:
            raise ValueError(f"Invalid tone: {v}")
        return v

    @field_validator("model")
    def validate_model(cls, v):
        if v is not None:
            valid_models = ["gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini"]
            if v not in valid_models:
                raise ValueError(f"Invalid model: {v}")
        return v


class SecureUserCreate(BaseModel):
    """Secure version of UserCreate with validation."""

    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(default="user", max_length=20)

    @field_validator("username")
    def validate_username(cls, v):
        return InputValidator.validate_username(v)

    @field_validator("email")
    def validate_email(cls, v):
        return InputValidator.validate_email(v)

    @field_validator("password")
    def validate_password(cls, v):
        # Check password strength
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Check for common weak passwords
        weak_passwords = ["password", "123456", "admin", "user", "test"]
        if v.lower() in weak_passwords:
            raise ValueError("Password is too weak")

        return v

    @field_validator("role")
    def validate_role(cls, v):
        valid_roles = ["admin", "user", "readonly"]
        if v not in valid_roles:
            raise ValueError(f"Invalid role: {v}")
        return v


def validate_and_sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize input data dictionary."""
    sanitized = {}

    for key, value in data.items():
        if isinstance(value, str):
            # Sanitize string values
            try:
                sanitized[key] = InputValidator.sanitize_text(value)
            except ValueError as e:
                logger.warning(f"Input validation failed for {key}: {e}")
                raise ValueError(f"Invalid input for {key}: {e}")
        elif isinstance(value, list):
            # Sanitize list items
            sanitized[key] = []
            for item in value:
                if isinstance(item, str):
                    sanitized[key].append(InputValidator.sanitize_text(item))
                else:
                    sanitized[key].append(item)
        else:
            sanitized[key] = value

    return sanitized
