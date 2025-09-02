# CI/CD Secrets Configuration

This document outlines the required secrets for deploying and running the Kyros Dashboard in production environments.

## Required Secrets

### Core API Keys

| Secret Name | Description | Required For | Example Format |
|-------------|-------------|--------------|----------------|
| `OPENAI_API_KEY` | OpenAI API key for content generation | Production API | `sk-...` |
| `OPENAI_ORG_ID` | OpenAI organization ID (optional) | Production API | `org-...` |

### Database & Storage

| Secret Name | Description | Required For | Example Format |
|-------------|-------------|--------------|----------------|
| `DATABASE_URL` | PostgreSQL connection string | Production API | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection string | Production API | `redis://host:6379` |

### Authentication & Security

| Secret Name | Description | Required For | Example Format |
|-------------|-------------|--------------|----------------|
| `JWT_SECRET` | Secret key for JWT token signing | Production API | 64+ character random string |
| `JWT_EXPIRATION_HOURS` | JWT token expiration time | Production API | `24` |

### Monitoring & Analytics

| Secret Name | Description | Required For | Example Format |
|-------------|-------------|--------------|----------------|
| `SENTRY_DSN` | Sentry error tracking DSN | Production API | `https://...@sentry.io/...` |
| `POSTHOG_API_KEY` | PostHog analytics API key | Production API | `phc-...` |
| `POSTHOG_HOST` | PostHog instance URL | Production API | `https://app.posthog.com` |

### Email Configuration

| Secret Name | Description | Required For | Example Format |
|-------------|-------------|--------------|----------------|
| `SMTP_HOST` | SMTP server hostname | Production API | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | Production API | `587` |
| `SMTP_USER` | SMTP username | Production API | `user@domain.com` |
| `SMTP_PASSWORD` | SMTP password/app password | Production API | `app-password` |

### File Storage (AWS S3)

| Secret Name | Description | Required For | Example Format |
|-------------|-------------|--------------|----------------|
| `AWS_ACCESS_KEY_ID` | AWS access key ID | Production API | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key | Production API | `...` |
| `AWS_S3_BUCKET` | S3 bucket name | Production API | `kyros-dashboard-files` |
| `AWS_REGION` | AWS region | Production API | `us-east-1` |

### Rate Limiting & Cost Controls

| Secret Name | Description | Required For | Example Format |
|-------------|-------------|--------------|----------------|
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | API rate limit | Production API | `60` |
| `RATE_LIMIT_BURST` | Burst limit | Production API | `10` |
| `MAX_TOKENS_PER_REQUEST` | OpenAI token limit | Production API | `4000` |
| `MAX_REQUESTS_PER_HOUR` | Hourly request limit | Production API | `100` |
| `MAX_COST_PER_DAY` | Daily cost limit (USD) | Production API | `50.00` |

### Frontend Configuration

| Secret Name | Description | Required For | Example Format |
|-------------|-------------|--------------|----------------|
| `VITE_API_BASE_URL` | Backend API URL | Production UI | `https://api.kyros.com` |

## GitHub Actions Setup

### Repository Secrets

Add the following secrets to your GitHub repository:

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Add the following repository secrets:

```bash
# Core API Keys
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_ORG_ID=org-your-org-id-here

# Database
DATABASE_URL=postgresql://user:pass@host:5432/kyros_dashboard
REDIS_URL=redis://host:6379

# Authentication
JWT_SECRET=your-super-secret-jwt-key-here
JWT_EXPIRATION_HOURS=24

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
POSTHOG_API_KEY=phc-your-posthog-api-key-here
POSTHOG_HOST=https://app.posthog.com

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# AWS S3
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-s3-bucket-name
AWS_REGION=us-east-1

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_BURST=10
MAX_TOKENS_PER_REQUEST=4000
MAX_REQUESTS_PER_HOUR=100
MAX_COST_PER_DAY=50.00

# Frontend
VITE_API_BASE_URL=https://api.kyros.com
```

## Vercel Setup

### Environment Variables

Add the following environment variables to your Vercel project:

1. Go to your Vercel dashboard
2. Select your project
3. Navigate to Settings → Environment Variables
4. Add the following variables:

```bash
# Core API Keys
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_ORG_ID=org-your-org-id-here

# Database
DATABASE_URL=postgresql://user:pass@host:5432/kyros_dashboard
REDIS_URL=redis://host:6379

# Authentication
JWT_SECRET=your-super-secret-jwt-key-here
JWT_EXPIRATION_HOURS=24

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
POSTHOG_API_KEY=phc-your-posthog-api-key-here
POSTHOG_HOST=https://app.posthog.com

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# AWS S3
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-s3-bucket-name
AWS_REGION=us-east-1

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_BURST=10
MAX_TOKENS_PER_REQUEST=4000
MAX_REQUESTS_PER_HOUR=100
MAX_COST_PER_DAY=50.00

# Frontend
VITE_API_BASE_URL=https://api.kyros.com
```

## Security Best Practices

### Secret Management

1. **Never commit secrets to version control**
   - Use `.env.example` for documentation
   - Ensure `.env` is in `.gitignore`
   - Use pre-commit hooks to prevent accidental commits

2. **Rotate secrets regularly**
   - Set up automated rotation for API keys
   - Monitor for compromised credentials
   - Use different secrets for different environments

3. **Use least privilege principle**
   - Grant minimal required permissions
   - Use separate API keys for different services
   - Implement proper access controls

4. **Monitor secret usage**
   - Set up alerts for unusual API usage
   - Monitor cost thresholds
   - Track authentication failures

### Environment Separation

- **Development**: Use local `.env` files with test credentials
- **Staging**: Use staging-specific secrets with limited permissions
- **Production**: Use production secrets with full monitoring

### Cost Controls

- Set up OpenAI usage alerts
- Implement rate limiting
- Monitor daily/monthly costs
- Set up automatic shutdown for cost overruns

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   - Check that all required secrets are set
   - Verify secret names match exactly
   - Ensure secrets are available in the correct environment

2. **Authentication Failures**
   - Verify API keys are valid and not expired
   - Check organization ID if using OpenAI
   - Ensure proper permissions are granted

3. **Database Connection Issues**
   - Verify connection string format
   - Check network connectivity
   - Ensure database is accessible from deployment environment

### Validation Script

Use this script to validate your environment setup:

```bash
#!/bin/bash
# validate-secrets.sh

required_secrets=(
    "OPENAI_API_KEY"
    "DATABASE_URL"
    "JWT_SECRET"
    "SENTRY_DSN"
    "POSTHOG_API_KEY"
)

missing_secrets=()

for secret in "${required_secrets[@]}"; do
    if [ -z "${!secret}" ]; then
        missing_secrets+=("$secret")
    fi
done

if [ ${#missing_secrets[@]} -eq 0 ]; then
    echo "✅ All required secrets are set"
else
    echo "❌ Missing secrets: ${missing_secrets[*]}"
    exit 1
fi
```

## Support

For issues with secret configuration:

1. Check this documentation first
2. Verify secret formats and values
3. Test with minimal configuration
4. Contact the development team for assistance
