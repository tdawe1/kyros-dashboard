#!/usr/bin/env python3
"""
Test script that loads .env files and verifies environment configuration.
This script actually loads the .env files to test if they're working correctly.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


def load_env_file(env_path):
    """Load environment variables from a .env file."""
    if not os.path.exists(env_path):
        return {}

    env_vars = {}
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                # Remove quotes if present
                value = value.strip("\"'")
                env_vars[key] = value
    return env_vars


def test_environment_configuration():
    """Test environment configuration by loading .env files."""
    print("🔍 Testing Environment Configuration with .env files...")
    print("=" * 60)

    # Load backend .env file
    backend_env_path = Path(__file__).parent.parent / "backend" / ".env"
    frontend_env_path = Path(__file__).parent.parent / "frontend" / ".env"

    print(f"📁 Backend .env: {backend_env_path}")
    print(f"📁 Frontend .env: {frontend_env_path}")
    print()

    # Load environment variables
    backend_env = load_env_file(backend_env_path)
    frontend_env = load_env_file(frontend_env_path)

    # Test required variables
    required_vars = ["JWT_SECRET_KEY", "DATABASE_URL", "REDIS_URL", "OPENAI_API_KEY"]

    print("📋 Required Variables:")
    for var in required_vars:
        value = backend_env.get(var)
        if value and value != f"your-{var.lower().replace('_', '-')}-here":
            # Mask sensitive values
            if "key" in var.lower() or "token" in var.lower():
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: NOT SET or using placeholder")

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
        value = backend_env.get(var)
        if value and value != f"your-{var.lower().replace('_', '-')}-here":
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
            print(f"  ⚠️  {var}: Not set or using placeholder")

    print("\n🌐 Frontend Variables:")
    frontend_vars = [
        "VITE_API_BASE_URL",
        "VITE_DEBUG",
        "VITE_ENVIRONMENT",
        "VITE_SENTRY_DSN",
    ]

    for var in frontend_vars:
        value = frontend_env.get(var)
        if value and value != f"your-{var.lower().replace('_', '-')}-here":
            if "dsn" in var.lower():
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"  ✅ {var}: {masked}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚠️  {var}: Not set or using placeholder")

    print("\n🌐 Environment Info:")
    print(f"  Environment: {backend_env.get('ENVIRONMENT', 'development')}")
    print(f"  Debug Mode: {backend_env.get('DEBUG', 'false')}")
    print(f"  API Mode: {backend_env.get('API_MODE', 'demo')}")
    print(f"  Database: {backend_env.get('DATABASE_URL', 'sqlite:///./kyros.db')}")
    print(f"  Redis: {backend_env.get('REDIS_URL', 'redis://localhost:6379')}")

    print("\n" + "=" * 60)

    # Count how many variables are properly set
    all_vars = required_vars + optional_vars + frontend_vars
    set_count = 0
    for var in all_vars:
        if var in frontend_vars:
            value = frontend_env.get(var)
        else:
            value = backend_env.get(var)

        if value and value != f"your-{var.lower().replace('_', '-')}-here":
            set_count += 1

    print(
        f"📊 {set_count}/{len(all_vars)} environment variables are properly configured"
    )

    # Check for placeholder values
    placeholder_count = 0
    for var in all_vars:
        if var in frontend_vars:
            value = frontend_env.get(var)
        else:
            value = backend_env.get(var)

        if value and value == f"your-{var.lower().replace('_', '-')}-here":
            placeholder_count += 1

    if placeholder_count > 0:
        print(f"⚠️  {placeholder_count} variables still have placeholder values")
        print(
            "   Please update these with your actual values from Cursor Background Agents settings"
        )

    print("🎉 Environment test complete!")


if __name__ == "__main__":
    test_environment_configuration()
