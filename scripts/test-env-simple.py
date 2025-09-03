#!/usr/bin/env python3
"""
Simple test script to verify environment variables are available.
This doesn't require the full backend dependencies.
"""

import os


def test_environment_variables():
    """Test if environment variables are loaded correctly."""
    print("🔍 Testing Environment Variables...")
    print("=" * 50)

    # Test required variables
    required_vars = ["JWT_SECRET_KEY", "DATABASE_URL", "REDIS_URL", "OPENAI_API_KEY"]

    print("📋 Required Variables:")
    for var in required_vars:
        value = os.getenv(var)
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
    optional_vars = [
        "SENTRY_DSN",
        "ADMIN_PASSWORD",
        "API_MODE",
        "ENVIRONMENT",
        "DEBUG",
        "LINEAR_API_TOKEN",
        "RAILWAY_TOKEN",
        "VERCEL_TOKEN",
        "GITHUB_TOKEN",
    ]

    for var in optional_vars:
        value = os.getenv(var)
        if value:
            if (
                "dsn" in var.lower()
                or "password" in var.lower()
                or "token" in var.lower()
            ):
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚠️  {var}: Not set (will use default)")

    print("\n🌐 Environment Info:")
    print(f"  Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"  Debug Mode: {os.getenv('DEBUG', 'false')}")
    print(f"  API Mode: {os.getenv('API_MODE', 'demo')}")

    print("\n" + "=" * 50)
    print("🎉 Environment test complete!")

    # Count how many variables are set
    all_vars = required_vars + optional_vars
    set_count = sum(1 for var in all_vars if os.getenv(var))
    print(f"📊 {set_count}/{len(all_vars)} environment variables are set")


if __name__ == "__main__":
    test_environment_variables()
