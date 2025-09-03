#!/bin/bash

# Kyros Dashboard Development Setup Script
# This script sets up the development environment with security tools

set -e

echo "🚀 Setting up Kyros Dashboard development environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

echo "📥 Installing backend Python dependencies..."
if command -v poetry >/dev/null 2>&1 && [ -f "backend/pyproject.toml" ]; then
    (cd backend && poetry install --no-interaction --no-ansi)
else
    echo "❌ Poetry not found or backend/pyproject.toml missing."
    echo "   Please install Poetry (https://python-poetry.org/docs/#installation) and re-run this script."
    exit 1
fi

# Install Node.js dependencies
echo "📥 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Install pre-commit hooks
echo "🔒 Setting up pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

# Initialize secrets baseline
echo "🔍 Initializing secrets detection baseline..."
detect-secrets scan --baseline .secrets.baseline

# Create backend .env file from example if it doesn't exist
if [ ! -f "backend/.env" ] && [ -f "backend/.env.example" ]; then
    echo "📝 Creating backend .env file from example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please update backend/.env with your actual secrets before running the application."
fi

# Set up git hooks
echo "🪝 Setting up git hooks..."
git config core.hooksPath .git/hooks

echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your actual API keys and secrets"
echo "2. Start the API server: 'cd backend && poetry run uvicorn main:app --reload --port 8000'"
echo "3. Start the Frontend server: 'cd frontend && npm run dev' (default port 3001)"
echo ""
echo "Security features enabled:"
echo "- Pre-commit hooks for code quality and security"
echo "- Secrets detection to prevent accidental commits"
echo "- Automated code formatting and linting"
echo "- Security scanning with bandit"
