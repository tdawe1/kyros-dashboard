# 🔑 API Keys & Tokens Setup Guide

This guide will help you obtain all the necessary API keys and tokens for the Kyros Dashboard project.

## 🚨 **Required Keys (Must Have)**

### 1. **JWT_SECRET_KEY**
- **What it is**: Secret key for JWT token authentication
- **How to get**: Generate your own secure random string
- **Generate command**:
  ```bash
  # Option 1: Using Python
  python -c "import secrets; print(secrets.token_urlsafe(32))"

  # Option 2: Using OpenSSL
  openssl rand -base64 32

  # Option 3: Using Node.js
  node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
  ```
- **Example**: `your-generated-32-character-secret-key-here`

### 2. **DATABASE_URL**
- **What it is**: Database connection string
- **Development**: `sqlite:///./kyros.db` (uses local SQLite file)
- **Production**: Get from your database provider (PostgreSQL recommended)
- **Providers**:
  - [Railway](https://railway.app) - Free PostgreSQL
  - [Supabase](https://supabase.com) - Free PostgreSQL
  - [Neon](https://neon.tech) - Free PostgreSQL
  - [PlanetScale](https://planetscale.com) - MySQL

### 3. **REDIS_URL**
- **What it is**: Redis cache connection string
- **Development**: `redis://localhost:6379` (if you have Redis installed)
- **Production**: Get from Redis provider
- **Providers**:
  - [Railway](https://railway.app) - Free Redis
  - [Redis Cloud](https://redis.com/redis-enterprise-cloud/overview/) - Free tier
  - [Upstash](https://upstash.com) - Free Redis

### 4. **OPENAI_API_KEY**
- **What it is**: OpenAI API key for AI features
- **How to get**:
  1. Go to [OpenAI Platform](https://platform.openai.com)
  2. Sign up/Login
  3. Go to API Keys section
  4. Click "Create new secret key"
  5. Copy the key (starts with `sk-`)
- **Cost**: Pay-per-use, starts with $5 free credit
- **Example**: `sk-proj-abc123...`

## 🔧 **Optional Keys (Nice to Have)**

### 5. **SENTRY_DSN**
- **What it is**: Error monitoring and performance tracking
- **How to get**:
  1. Go to [Sentry.io](https://sentry.io)
  2. Create free account
  3. Create new project
  4. Copy DSN from project settings
- **Cost**: Free tier available
- **Example**: `https://abc123@sentry.io/123456`

### 6. **LINEAR_API_TOKEN**
- **What it is**: Linear project management integration
- **How to get**:
  1. Go to [Linear](https://linear.app)
  2. Sign up/Login
  3. Go to Settings → API
  4. Create Personal API Key
- **Cost**: Free for personal use
- **Example**: `lin_api_abc123...`

### 7. **RAILWAY_TOKEN**
- **What it is**: Railway deployment platform
- **How to get**:
  1. Go to [Railway](https://railway.app)
  2. Sign up/Login
  3. Go to Account Settings → Tokens
  4. Create new token
- **Cost**: Free tier available
- **Example**: `railway_abc123...`

### 8. **VERCEL_TOKEN**
- **What it is**: Vercel deployment platform
- **How to get**:
  1. Go to [Vercel](https://vercel.com)
  2. Sign up/Login
  3. Go to Account Settings → Tokens
  4. Create new token
- **Cost**: Free tier available
- **Example**: `vercel_abc123...`

### 9. **GITHUB_TOKEN**
- **What it is**: GitHub integration for code reviews
- **How to get**:
  1. Go to [GitHub](https://github.com)
  2. Go to Settings → Developer settings → Personal access tokens
  3. Generate new token (classic)
  4. Select scopes: `repo`, `read:user`, `read:org`
- **Cost**: Free
- **Example**: `ghp_abc123...`

## 🚀 **Quick Setup Commands**

### Generate JWT Secret
```bash
# Linux/Mac
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"

# Windows
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

### Create .env file
```bash
# Copy the example file
cp backend/env.example backend/.env

# Edit with your keys
nano backend/.env
```

## 📝 **Environment File Template**

Create `backend/.env` with:
```bash
# Required
JWT_SECRET_KEY=your-generated-secret-here
DATABASE_URL=sqlite:///./kyros.db
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-your-openai-key-here

# Optional
SENTRY_DSN=your-sentry-dsn-here
ADMIN_PASSWORD=admin123
LINEAR_API_TOKEN=your-linear-token-here
RAILWAY_TOKEN=your-railway-token-here
VERCEL_TOKEN=your-vercel-token-here
GITHUB_TOKEN=your-github-token-here
```

## 🔒 **Security Best Practices**

1. **Never commit .env files** to version control
2. **Use different keys** for development/production
3. **Rotate keys regularly** (especially production)
4. **Use environment-specific values** in production
5. **Monitor usage** to avoid unexpected charges

## 💰 **Cost Summary**

| Service | Free Tier | Paid Plans |
|---------|-----------|------------|
| OpenAI | $5 credit | Pay-per-use |
| Sentry | 5K errors/month | $26/month |
| Linear | Personal use | $8/user/month |
| Railway | $5 credit | $5/month |
| Vercel | Free hosting | $20/month |
| GitHub | Free | $4/user/month |

## 🆘 **Need Help?**

- **OpenAI**: [OpenAI Help Center](https://help.openai.com)
- **Sentry**: [Sentry Documentation](https://docs.sentry.io)
- **Linear**: [Linear Help](https://linear.app/help)
- **Railway**: [Railway Docs](https://docs.railway.app)
- **Vercel**: [Vercel Docs](https://vercel.com/docs)
- **GitHub**: [GitHub Docs](https://docs.github.com)

## 🎯 **Minimum Setup for Development**

To get started quickly, you only need:
1. **JWT_SECRET_KEY** (generate locally)
2. **DATABASE_URL** (use SQLite: `sqlite:///./kyros.db`)
3. **REDIS_URL** (use local: `redis://localhost:6379`)
4. **OPENAI_API_KEY** (get from OpenAI)

All other keys are optional and can be added later as needed!
