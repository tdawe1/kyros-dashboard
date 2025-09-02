# Railway Deployment Setup Guide

This guide will help you deploy your Kyros Dashboard backend to Railway.

## 🚀 Quick Setup

### 1. Create Railway Project

1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose `tdawe1/kyros-dashboard`
6. Select the `api` folder as the root directory

### 2. Configure Environment Variables

In your Railway project settings, add these environment variables:

#### Required Variables:
```bash
OPENAI_API_KEY=your_openai_api_key_here
REDIS_URL=redis://localhost:6379  # Railway will provide this
```

#### Optional Variables (with defaults):
```bash
ENVIRONMENT=production
API_MODE=real
DEFAULT_MODEL=gpt-4o-mini
MAX_INPUT_CHARACTERS=100000
MAX_TOKENS_PER_JOB=50000
TOKEN_ESTIMATION_FACTOR=1.3
DAILY_JOB_LIMIT=10
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
RATE_LIMIT_BURST=10
REDIS_SECURITY_MODE=fail_closed
```

### 3. Add Redis Service

1. In your Railway project, click "New Service"
2. Select "Database" → "Add Redis"
3. Railway will automatically set the `REDIS_URL` environment variable

### 4. Deploy

Railway will automatically deploy when you push to your main branch.

## 🔧 Configuration Files

### `railway.json`
Located in `api/railway.json`, this file configures:
- Build settings (using Nixpacks)
- Start command (uvicorn with proper host/port)
- Health check endpoint (`/api/health`)
- Restart policy
- Environment-specific variables

### Environment Variables
- Copy from `api/railway.env.example`
- Set in Railway project settings
- Required: `OPENAI_API_KEY`, `REDIS_URL`

## 📊 Monitoring

### Health Check
Railway will monitor your app at: `https://your-app.railway.app/api/health`

### Logs
View logs in Railway dashboard or via CLI:
```bash
railway logs
```

## 🔐 Security

- Uses fail-closed Redis security mode in production
- Rate limiting enabled
- Input validation and sanitization
- Secure error handling

## 🚀 CI/CD Integration

The GitHub Actions workflow will automatically deploy to Railway when you push to main branch.

Required secrets in GitHub:
- `RAILWAY_TOKEN` - Your Railway API token
- `RAILWAY_PROJECT_ID` - Your Railway project ID

## 📝 Getting Project ID

1. Go to your Railway project
2. Click on "Settings"
3. Copy the "Project ID" (UUID format)

## 🔑 Getting Railway Token

1. Go to Railway dashboard
2. Click your profile → "Account Settings"
3. Go to "Tokens" tab
4. Click "New Token"
5. Give it a name like "GitHub Actions"
6. Copy the token

## 🧪 Testing Deployment

After deployment, test your API:

```bash
# Health check
curl https://your-app.railway.app/api/health

# Test endpoint
curl https://your-app.railway.app/api/generate \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"content": "test", "channel": "blog"}'
```

## 🆘 Troubleshooting

### Common Issues:

1. **Build fails**: Check Python version in `requirements.txt`
2. **Redis connection fails**: Ensure Redis service is added
3. **OpenAI errors**: Verify `OPENAI_API_KEY` is set correctly
4. **Health check fails**: Check if `/api/health` endpoint exists

### Debug Commands:
```bash
# View logs
railway logs

# Connect to service
railway shell

# Check environment variables
railway variables
```
