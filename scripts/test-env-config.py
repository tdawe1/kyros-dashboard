#!/usr/bin/env python3
"""
Test script to verify environment configuration is working correctly.
Run this to check if all your secrets are being loaded properly.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from core.config import settings, validate_configuration  # noqa: E402


def test_environment_config():
    """Test if environment variables are loaded correctly."""
    print("🔍 Testing Environment Configuration...")
    print("=" * 50)

    # Test required variables
    required_vars = ["JWT_SECRET_KEY", "DATABASE_URL", "REDIS_URL", "OPENAI_API_KEY"]

    print("📋 Required Variables:")
    for var in required_vars:
        value = getattr(settings, var.lower(), None)
        if value:
            # Mask sensitive values
            if "key" in var.lower() or "token" in var.lower():
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: NOT SET")

    print("\n🔧 Optional Variables:")
    optional_vars = ["SENTRY_DSN", "ADMIN_PASSWORD", "API_MODE", "ENVIRONMENT", "DEBUG"]

    for var in optional_vars:
        value = getattr(settings, var.lower(), None)
        if value:
            if "dsn" in var.lower() or "password" in var.lower():
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚠️  {var}: Using default")

    print("\n🔍 Configuration Validation:")
    if validate_configuration():
        print("  ✅ Configuration validation passed!")
    else:
        print("  ❌ Configuration validation failed!")

    print("\n🌐 Environment Info:")
    print(f"  Environment: {settings.environment}")
    print(f"  Debug Mode: {settings.debug}")
    print(f"  API Mode: {settings.api_mode}")
    print(f"  Database: {settings.database_url}")
    print(f"  Redis: {settings.redis_url}")

    print("\n" + "=" * 50)
    print("🎉 Environment test complete!")


if __name__ == "__main__":
    test_environment_config()
