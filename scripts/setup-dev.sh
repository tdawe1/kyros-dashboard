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

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r api/requirements.txt

# Install Node.js dependencies
echo "📥 Installing Node.js dependencies..."
cd ui
npm install
cd ..

# Install pre-commit hooks
echo "🔒 Setting up pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

# Initialize secrets baseline
echo "🔍 Initializing secrets detection baseline..."
detect-secrets scan --baseline .secrets.baseline

# Create .env file from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your actual secrets before running the application."
fi

# Set up git hooks
echo "🪝 Setting up git hooks..."
git config core.hooksPath .git/hooks

echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your actual API keys and secrets"
echo "2. Run 'source venv/bin/activate' to activate the virtual environment"
echo "3. Start the API server: 'cd api && python main.py'"
echo "4. Start the UI server: 'cd ui && npm run dev'"
echo ""
echo "Security features enabled:"
echo "- Pre-commit hooks for code quality and security"
echo "- Secrets detection to prevent accidental commits"
echo "- Automated code formatting and linting"
echo "- Security scanning with bandit"
