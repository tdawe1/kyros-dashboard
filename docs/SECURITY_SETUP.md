# Security Setup Guide

This guide covers the security hardening implemented for the Kyros Dashboard to ensure production readiness.

## Overview

The security setup includes:
- Secrets management and detection
- Pre-commit hooks for code quality
- Automated security scanning
- Environment variable management
- Cost controls and rate limiting

## Quick Start

### 1. Run the Setup Script

```bash
./setup-dev.sh
```

This script will:
- Create a Python virtual environment
- Install all dependencies
- Set up pre-commit hooks
- Initialize secrets detection
- Create environment files

### 2. Configure Environment Variables

Copy the example environment file and update with your secrets:

```bash
cp .env.example .env
# Edit .env with your actual API keys and secrets
```

### 3. Verify Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Run pre-commit hooks manually
pre-commit run --all-files

# Check for secrets
detect-secrets scan
```

## Security Features

### Pre-commit Hooks

The following hooks are automatically run before each commit:

- **Black**: Python code formatting
- **Ruff**: Python linting and formatting
- **detect-secrets**: Prevents committing secrets
- **ESLint**: JavaScript/TypeScript linting
- **Bandit**: Python security scanning
- **General hooks**: Trailing whitespace, YAML validation, etc.

### Secrets Detection

The `detect-secrets` tool scans for:
- API keys (OpenAI, AWS, GitHub, etc.)
- Passwords and tokens
- Private keys
- Database credentials
- Other sensitive information

### Environment Management

- `.env.example`: Template with placeholder values
- `.env`: Local environment file (gitignored)
- `.gitignore`: Comprehensive ignore patterns
- CI/CD secrets: Documented in `CI_SECRETS.md`

## Cost Controls

### OpenAI Rate Limiting

The system includes multiple layers of cost protection:

1. **Token Limits**: Maximum tokens per request
2. **Rate Limiting**: Requests per minute/hour
3. **Cost Monitoring**: Daily cost thresholds
4. **Automatic Shutdown**: Stop processing on overruns

### Configuration

```python
# In your .env file
MAX_TOKENS_PER_REQUEST=4000
MAX_REQUESTS_PER_HOUR=100
MAX_COST_PER_DAY=50.00
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

## Monitoring & Analytics

### Sentry Integration

Error tracking and performance monitoring:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

### PostHog Analytics

User behavior and product analytics:

```python
import posthog

posthog.api_key = os.getenv("POSTHOG_API_KEY")
posthog.host = os.getenv("POSTHOG_HOST")
```

## Database Security

### Connection Security

- Encrypted connections (SSL/TLS)
- Connection pooling
- Query parameterization
- Access controls

### Redis Security

- Authentication enabled
- Network isolation
- Memory limits
- Persistence controls

## Authentication & Authorization

### JWT Implementation

```python
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

## File Storage Security

### AWS S3 Configuration

- Bucket encryption
- Access logging
- Versioning
- Lifecycle policies
- CORS configuration

## Email Security

### SMTP Configuration

- TLS encryption
- Authentication
- Rate limiting
- Spam protection

## Development Workflow

### Before Committing

1. **Run pre-commit hooks**:
   ```bash
   pre-commit run --all-files
   ```

2. **Check for secrets**:
   ```bash
   detect-secrets scan
   ```

3. **Run security scan**:
   ```bash
   bandit -r api/
   ```

### Code Review Checklist

- [ ] No hardcoded secrets
- [ ] Environment variables used correctly
- [ ] Input validation implemented
- [ ] Error handling in place
- [ ] Security headers configured
- [ ] Rate limiting applied
- [ ] Logging implemented

## Production Deployment

### Environment Variables

Ensure all required secrets are set in your production environment:

```bash
# Core API Keys
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
JWT_SECRET=...

# Monitoring
SENTRY_DSN=https://...
POSTHOG_API_KEY=phc-...

# Cost Controls
MAX_COST_PER_DAY=50.00
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

### Security Headers

```python
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

# Security headers
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.yourdomain.com"])
app.add_middleware(HTTPSRedirectMiddleware)
```

### Health Checks

```python
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

## Troubleshooting

### Common Issues

1. **Pre-commit hooks failing**:
   ```bash
   pre-commit run --all-files --verbose
   ```

2. **Secrets detected**:
   ```bash
   detect-secrets scan --baseline .secrets.baseline
   ```

3. **Environment variables not loading**:
   ```bash
   python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
   ```

### Security Incidents

If you suspect a security incident:

1. **Immediately rotate affected secrets**
2. **Check logs for unauthorized access**
3. **Review recent commits for exposed secrets**
4. **Update security baselines**
5. **Notify the team**

## Best Practices

### Secret Management

- Use environment variables for all secrets
- Rotate secrets regularly
- Use different secrets for different environments
- Monitor secret usage

### Code Security

- Validate all inputs
- Use parameterized queries
- Implement proper error handling
- Log security events

### Infrastructure Security

- Use HTTPS everywhere
- Implement proper firewall rules
- Regular security updates
- Monitor access logs

## Support

For security-related questions or issues:

1. Check this documentation
2. Review the CI_SECRETS.md file
3. Contact the development team
4. Report security issues privately

## Updates

This security setup is regularly updated. Check for updates:

```bash
git pull origin main
./setup-dev.sh
```
