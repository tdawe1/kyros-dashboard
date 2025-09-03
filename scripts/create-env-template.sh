#!/bin/bash
# Create comprehensive .env template based on project context
# This script creates environment files for different deployment scenarios

echo "🔧 Creating comprehensive .env templates for Kyros Dashboard..."

# Create backend .env template
cat > backend/.env.template << 'EOF'
# =============================================================================
# KYROS DASHBOARD - BACKEND ENVIRONMENT CONFIGURATION
# =============================================================================
# Copy this file to .env and fill in your actual values
# Never commit .env files to version control!

# =============================================================================
# REQUIRED VARIABLES (Must be set for the app to work)
# =============================================================================

# JWT Authentication Secret (Generate a secure random string)
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database Configuration
# Development: SQLite (local file)
# Production: PostgreSQL (Railway/Render)
DATABASE_URL=sqlite:///./kyros.db

# Redis Cache Configuration
# Development: Local Redis
# Production: Railway Redis or Redis Cloud
REDIS_URL=redis://localhost:6379

# OpenAI API Configuration
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-openai-api-key-here

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================

# Environment (development, staging, production)
ENVIRONMENT=development

# Debug mode (true for development, false for production)
DEBUG=true

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api

# Admin password (for initial setup)
ADMIN_PASSWORD=admin123

# =============================================================================
# AI & MODEL CONFIGURATION
# =============================================================================

# API Mode (demo for testing, real for production)
API_MODE=demo

# Default AI model
DEFAULT_MODEL=gpt-4o-mini

# Token limits and quotas
MAX_INPUT_CHARACTERS=100000
MAX_TOKENS_PER_JOB=50000
TOKEN_ESTIMATION_FACTOR=1.3
DAILY_JOB_LIMIT=10

# =============================================================================
# RATE LIMITING & SECURITY
# =============================================================================

# Rate limiting configuration
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
RATE_LIMIT_BURST=10

# Redis security mode
REDIS_SECURITY_MODE=fail_closed

# Circuit breaker settings
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60

# =============================================================================
# MONITORING & OBSERVABILITY
# =============================================================================

# Sentry error tracking (optional)
# Get from: https://sentry.io
SENTRY_DSN=your-sentry-dsn-here

# Release version
RELEASE_VERSION=1.0.0

# =============================================================================
# EXTERNAL SERVICE INTEGRATIONS
# =============================================================================

# Linear Project Management (optional - for MCP integration)
# Get from: https://linear.app/settings/api
LINEAR_API_TOKEN=your-linear-api-token-here

# Railway Deployment (for MCP integration)
# Get from: https://railway.app/account/tokens
RAILWAY_TOKEN=your-railway-token-here
RAILWAY_SERVICE_NAME=kyros-dashboard-api

# Vercel Deployment (for MCP integration)
# Get from: https://vercel.com/account/tokens
VERCEL_TOKEN=your-vercel-token-here
VERCEL_ORG_ID=your-vercel-org-id-here
VERCEL_PROJECT_ID=your-vercel-project-id-here

# GitHub Integration (for MCP integration)
# Get from: https://github.com/settings/tokens
GITHUB_TOKEN=your-github-token-here

# =============================================================================
# CORS & SECURITY
# =============================================================================

# Allowed origins for CORS
ALLOWED_ORIGINS=http://localhost:3001,http://localhost:5173,http://localhost:3000

# =============================================================================
# DATABASE CONFIGURATION (Advanced)
# =============================================================================

# Database pool settings
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_ECHO=false

# =============================================================================
# JWT CONFIGURATION (Advanced)
# =============================================================================

# JWT algorithm
JWT_ALGORITHM=HS256

# Token expiration times
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
EOF

# Create frontend .env template
cat > frontend/.env.template << 'EOF'
# =============================================================================
# KYROS DASHBOARD - FRONTEND ENVIRONMENT CONFIGURATION
# =============================================================================
# Copy this file to .env and fill in your actual values
# Never commit .env files to version control!

# =============================================================================
# API CONFIGURATION
# =============================================================================

# Backend API Base URL
# Development: http://localhost:8000
# Staging: https://staging-api.kyros-dashboard.com
# Production: https://api.kyros-dashboard.com
VITE_API_BASE_URL=http://localhost:8000

# =============================================================================
# DEVELOPMENT SETTINGS
# =============================================================================

# Debug mode (true for development, false for production)
VITE_DEBUG=true

# Environment
VITE_ENVIRONMENT=development

# Release version
VITE_RELEASE_VERSION=1.0.0

# =============================================================================
# MONITORING & OBSERVABILITY
# =============================================================================

# Sentry error tracking (optional)
# Get from: https://sentry.io
VITE_SENTRY_DSN=your-sentry-dsn-here
EOF

# Create staging environment template
cat > backend/.env.staging.template << 'EOF'
# =============================================================================
# KYROS DASHBOARD - STAGING ENVIRONMENT
# =============================================================================
# This file is used for staging deployments
# Copy to .env.staging and configure for your staging environment

# =============================================================================
# STAGING-SPECIFIC CONFIGURATION
# =============================================================================

ENVIRONMENT=staging
DEBUG=false
API_MODE=demo

# Staging Database (PostgreSQL on Railway)
DATABASE_URL=postgresql://user:pass@staging-db.railway.app:5432/kyros_staging

# Staging Redis
REDIS_URL=redis://staging-redis.railway.app:6379

# Staging API URL
VITE_API_BASE_URL=https://staging-api.kyros-dashboard.com

# =============================================================================
# REQUIRED VARIABLES (Same as production but with staging values)
# =============================================================================

JWT_SECRET_KEY=your-staging-jwt-secret-key-here
OPENAI_API_KEY=sk-your-openai-api-key-here
SENTRY_DSN=your-sentry-dsn-here

# =============================================================================
# EXTERNAL SERVICES (Staging tokens)
# =============================================================================

LINEAR_API_TOKEN=your-linear-api-token-here
RAILWAY_TOKEN=your-railway-token-here
VERCEL_TOKEN=your-vercel-token-here
GITHUB_TOKEN=your-github-token-here
EOF

# Create production environment template
cat > backend/.env.production.template << 'EOF'
# =============================================================================
# KYROS DASHBOARD - PRODUCTION ENVIRONMENT
# =============================================================================
# This file is used for production deployments
# Copy to .env.production and configure for your production environment

# =============================================================================
# PRODUCTION-SPECIFIC CONFIGURATION
# =============================================================================

ENVIRONMENT=production
DEBUG=false
API_MODE=real

# Production Database (PostgreSQL on Railway)
DATABASE_URL=postgresql://user:pass@prod-db.railway.app:5432/kyros_production

# Production Redis
REDIS_URL=redis://prod-redis.railway.app:6379

# Production API URL
VITE_API_BASE_URL=https://api.kyros-dashboard.com

# =============================================================================
# REQUIRED VARIABLES (Production values)
# =============================================================================

JWT_SECRET_KEY=your-production-jwt-secret-key-here
OPENAI_API_KEY=sk-your-openai-api-key-here
SENTRY_DSN=your-sentry-dsn-here

# =============================================================================
# EXTERNAL SERVICES (Production tokens)
# =============================================================================

LINEAR_API_TOKEN=your-linear-api-token-here
RAILWAY_TOKEN=your-railway-token-here
VERCEL_TOKEN=your-vercel-token-here
GITHUB_TOKEN=your-github-token-here

# =============================================================================
# PRODUCTION SECURITY SETTINGS
# =============================================================================

# More restrictive rate limiting for production
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW=3600
RATE_LIMIT_BURST=5

# Production CORS origins
ALLOWED_ORIGINS=https://kyros-dashboard.com,https://www.kyros-dashboard.com
EOF

echo "✅ Created environment templates:"
echo "  📁 backend/.env.template"
echo "  📁 frontend/.env.template"
echo "  📁 backend/.env.staging.template"
echo "  📁 backend/.env.production.template"
echo ""
echo "📋 Next steps:"
echo "1. Copy the appropriate template to .env:"
echo "   cp backend/.env.template backend/.env"
echo "   cp frontend/.env.template frontend/.env"
echo ""
echo "2. Fill in your actual values from your Cursor Background Agents settings"
echo ""
echo "3. For deployment, use the staging/production templates"
echo ""
echo "🔒 Security reminder:"
echo "- Never commit .env files to version control"
echo "- Use different secrets for each environment"
echo "- Rotate secrets regularly"
