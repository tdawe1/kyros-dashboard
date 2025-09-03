#!/bin/bash
# Setup script for local development environment variables
# Run this script to set up your local environment

echo "🔧 Setting up local development environment..."

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating backend/.env file..."
    cat > backend/.env << 'EOF'
# Kyros Dashboard Local Development Environment
# Copy values from your Cursor Background Agents settings

# Required Variables
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///./kyros.db
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your-openai-api-key-here

# Optional Variables
SENTRY_DSN=your-sentry-dsn-here
ADMIN_PASSWORD=admin123
API_MODE=demo
ENVIRONMENT=development
DEBUG=true

# External Service Tokens
LINEAR_API_TOKEN=your-linear-token-here
RAILWAY_TOKEN=your-railway-token-here
VERCEL_TOKEN=your-vercel-token-here
GITHUB_TOKEN=your-github-token-here

# Frontend Variables
VITE_API_BASE_URL=http://localhost:8000
VITE_DEBUG=true
VITE_SENTRY_DSN=your-sentry-dsn-here
VITE_ENVIRONMENT=development
EOF
    echo "✅ Created backend/.env file"
else
    echo "⚠️  backend/.env already exists"
fi

echo ""
echo "📋 Next steps:"
echo "1. Edit backend/.env and replace placeholder values with your actual secrets"
echo "2. Copy the values from your Cursor Background Agents settings"
echo "3. Run: python scripts/test-env-simple.py to verify"
echo ""
echo "🔒 Security reminder:"
echo "- Never commit .env files to version control"
echo "- Use different values for development vs production"
echo "- Keep your secrets secure"
