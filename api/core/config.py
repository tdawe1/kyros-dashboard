"""
Centralized configuration management for Kyros Dashboard.
Implements secure configuration loading with validation and environment-specific settings.
"""

import logging
from typing import List, Optional
from pydantic import field_validator, Field
from pydantic_settings import BaseSettings
from enum import Enum

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Application environments."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class SecurityMode(str, Enum):
    """Security operation modes."""

    FAIL_CLOSED = "fail_closed"
    FAIL_OPEN = "fail_open"
    GRACEFUL = "graceful"


class Settings(BaseSettings):
    """Application settings with validation."""

    # Application settings
    app_name: str = Field(default="Kyros Dashboard", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # API settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_prefix: str = Field(default="/api", env="API_PREFIX")

    # Security settings
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )
    admin_password: str = Field(default="admin123", env="ADMIN_PASSWORD")

    # Database settings
    database_url: str = Field(default="sqlite:///./kyros.db", env="DATABASE_URL")
    db_pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    db_pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")
    db_echo: bool = Field(default=False, env="DB_ECHO")

    # Redis settings
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_security_mode: SecurityMode = Field(
        default=SecurityMode.FAIL_CLOSED, env="REDIS_SECURITY_MODE"
    )

    # Rate limiting settings
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")
    rate_limit_burst: int = Field(default=10, env="RATE_LIMIT_BURST")

    # Quota settings
    daily_job_limit: int = Field(default=10, env="DAILY_JOB_LIMIT")
    max_input_characters: int = Field(default=100000, env="MAX_INPUT_CHARACTERS")
    max_tokens_per_job: int = Field(default=50000, env="MAX_TOKENS_PER_JOB")
    token_estimation_factor: float = Field(default=1.3, env="TOKEN_ESTIMATION_FACTOR")

    # OpenAI settings
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    api_mode: str = Field(default="demo", env="API_MODE")
    default_model: str = Field(default="gpt-4o-mini", env="DEFAULT_MODEL")

    # CORS settings
    allowed_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        env="ALLOWED_ORIGINS",
    )

    # Monitoring settings
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    release_version: str = Field(default="1.0.0", env="RELEASE_VERSION")

    # Circuit breaker settings
    circuit_breaker_failure_threshold: int = Field(
        default=5, env="CIRCUIT_BREAKER_FAILURE_THRESHOLD"
    )
    circuit_breaker_recovery_timeout: int = Field(
        default=60, env="CIRCUIT_BREAKER_RECOVERY_TIMEOUT"
    )



    @field_validator("environment", mode="before")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment setting."""
        if isinstance(v, str):
            try:
                return Environment(v.lower())
            except ValueError:
                logger.warning(f"Invalid environment '{v}', using development")
                return Environment.DEVELOPMENT
        return v

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v):
        """Validate JWT secret key."""
        if not v or len(v) < 32:
            logger.warning("JWT secret key is too short, generating a secure one")
            import secrets

            return secrets.token_urlsafe(32)
        return v

    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, v):
        """Validate OpenAI API key format."""
        if v and not v.startswith("sk-"):
            logger.warning("OpenAI API key format appears invalid")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def is_production() -> bool:
    """Check if running in production."""
    return settings.environment == Environment.PRODUCTION


def is_development() -> bool:
    """Check if running in development."""
    return settings.environment == Environment.DEVELOPMENT


def is_testing() -> bool:
    """Check if running in testing."""
    return settings.environment == Environment.TESTING


def get_database_url() -> str:
    """Get database URL with environment-specific modifications."""
    if is_testing():
        # Use in-memory database for testing
        return "sqlite:///:memory:"
    return settings.database_url


def get_redis_url() -> str:
    """Get Redis URL with environment-specific modifications."""
    if is_testing():
        # Use mock Redis for testing
        return "redis://localhost:6379/15"  # Use different DB for testing
    return settings.redis_url


def get_cors_origins() -> List[str]:
    """Get CORS origins based on environment."""
    # Parse comma-separated origins
    origins = [origin.strip() for origin in settings.allowed_origins.split(",")]
    
    if is_production():
        # In production, only allow specific domains
        return origins
    else:
        # In development, allow localhost origins
        return origins + [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]


def get_log_level() -> str:
    """Get log level based on environment."""
    if is_production():
        return "INFO"
    elif is_development():
        return "DEBUG"
    else:
        return "WARNING"


def validate_configuration() -> bool:
    """Validate all configuration settings."""
    try:
        # Check required settings
        if not settings.jwt_secret_key:
            logger.error("JWT secret key is required")
            return False

        # Check database URL
        if not settings.database_url:
            logger.error("Database URL is required")
            return False

        # Check Redis URL
        if not settings.redis_url:
            logger.error("Redis URL is required")
            return False

        # Validate numeric settings
        if settings.daily_job_limit <= 0:
            logger.error("Daily job limit must be positive")
            return False

        if settings.max_input_characters <= 0:
            logger.error("Max input characters must be positive")
            return False

        logger.info("Configuration validation passed")
        return True

    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False


# Initialize configuration
if not validate_configuration():
    logger.error(
        "Configuration validation failed, some features may not work correctly"
    )
