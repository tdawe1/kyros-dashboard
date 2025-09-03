# 🚀 Kyros Dashboard Deployment Workflow

This document outlines the complete deployment workflow for your Kyros Dashboard project, including staging and production environments.

## 📋 **Deployment Architecture**

### **Frontend (Vercel)**
- **Development**: Local development server (`npm run dev`)
- **Staging**: Vercel Preview deployments (manual trigger)
- **Production**: Vercel Production (auto-deploy on main branch push)

### **Backend (Railway)**
- **Development**: Local development server (`./start_dev.sh`)
- **Staging**: Railway Staging service (manual trigger)
- **Production**: Railway Production (auto-deploy on main branch push)

## 🔄 **Deployment Workflows**

### **1. Development Workflow**
```bash
# Start local development
./scripts/start-both.sh

# Or start individually
cd backend && ./start_dev.sh
cd frontend && npm run dev
```

### **2. Staging Deployment (Manual)**
```bash
# Deploy to staging
git checkout develop
git merge feature/your-feature
git push origin develop

# This triggers:
# - Frontend: Vercel Preview deployment
# - Backend: Railway Staging deployment
```

### **3. Production Deployment (Automatic)**
```bash
# Create and merge PR to main
git checkout main
git merge develop
git push origin main

# This triggers:
# - Frontend: Vercel Production deployment
# - Backend: Railway Production deployment
```

## 🔧 **Environment Configuration**

### **Required GitHub Secrets**
Add these to your GitHub repository (Settings → Secrets and variables → Actions):

```bash
# Vercel Configuration
VERCEL_TOKEN=your-vercel-token
VERCEL_ORG_ID=your-vercel-org-id
VERCEL_PROJECT_ID=your-vercel-project-id

# Railway Configuration
RAILWAY_TOKEN=your-railway-token
RAILWAY_SERVICE_NAME=kyros-dashboard-api
RAILWAY_STAGING_SERVICE_NAME=kyros-dashboard-api-staging

# Environment URLs
VITE_API_BASE_URL=https://api.kyros-dashboard.com
VITE_API_BASE_URL_STAGING=https://staging-api.kyros-dashboard.com

# Optional: Slack Notifications
SLACK_WEBHOOK=your-slack-webhook-url
```

### **Environment Variables by Environment**

#### **Development (.env)**
```bash
ENVIRONMENT=development
DEBUG=true
API_MODE=demo
DATABASE_URL=sqlite:///./kyros.db
REDIS_URL=redis://localhost:6379
VITE_API_BASE_URL=http://localhost:8000
```

#### **Staging (.env.staging)**
```bash
ENVIRONMENT=staging
DEBUG=false
API_MODE=demo
DATABASE_URL=postgresql://user:pass@staging-db.railway.app:5432/kyros_staging
REDIS_URL=redis://staging-redis.railway.app:6379
VITE_API_BASE_URL=https://staging-api.kyros-dashboard.com
```

#### **Production (.env.production)**
```bash
ENVIRONMENT=production
DEBUG=false
API_MODE=real
DATABASE_URL=postgresql://user:pass@prod-db.railway.app:5432/kyros_production
REDIS_URL=redis://prod-redis.railway.app:6379
VITE_API_BASE_URL=https://api.kyros-dashboard.com
```

## 🛠️ **Setup Instructions**

### **1. Vercel Setup**
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Import your GitHub repository
3. Set Root Directory to `frontend`
4. Configure build settings:
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm ci`
5. Add environment variables in Vercel project settings

### **2. Railway Setup**
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Create new project
3. Connect your GitHub repository
4. Set Root Directory to `backend`
5. Railway will auto-detect Python and use `railway.json` config
6. Add environment variables in Railway project settings

### **3. GitHub Actions Setup**
1. Ensure your repository has Actions enabled
2. Add the required secrets (listed above)
3. The workflows will automatically trigger on:
   - PR to `develop` → Staging deployment
   - Push to `main` → Production deployment

## 🔍 **Monitoring & Observability**

### **Sentry Integration**
- Error tracking and performance monitoring
- Configured in both frontend and backend
- Different DSNs for staging and production

### **Health Checks**
- Backend: `/api/health` endpoint
- Frontend: Vercel built-in health checks
- Railway: Automatic health checks

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Frontend Build Fails**
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### **Backend Deployment Fails**
```bash
# Check Python version
python --version  # Should be 3.12+

# Check dependencies
cd backend
poetry install
poetry run python -m pytest
```

#### **Environment Variables Not Loading**
```bash
# Test environment configuration
python scripts/test-env-simple.py

# Check if .env file exists
ls -la backend/.env
ls -la frontend/.env
```

## 📊 **Deployment Status**

### **Check Deployment Status**
- **Vercel**: [Vercel Dashboard](https://vercel.com/dashboard)
- **Railway**: [Railway Dashboard](https://railway.app/dashboard)
- **GitHub Actions**: [Actions Tab](https://github.com/your-repo/actions)

### **Deployment URLs**
- **Production Frontend**: `https://kyros-dashboard.vercel.app`
- **Production Backend**: `https://kyros-dashboard-api.railway.app`
- **Staging Frontend**: `https://kyros-dashboard-git-develop.vercel.app`
- **Staging Backend**: `https://kyros-dashboard-api-staging.railway.app`

## 🔒 **Security Best Practices**

1. **Environment Variables**
   - Use different secrets for each environment
   - Rotate secrets regularly
   - Never commit .env files

2. **Access Control**
   - Limit who can trigger deployments
   - Use branch protection rules
   - Require PR reviews

3. **Monitoring**
   - Set up alerts for failed deployments
   - Monitor error rates
   - Track performance metrics

## 📝 **Next Steps**

1. **Set up your accounts**:
   - [Vercel](https://vercel.com) for frontend
   - [Railway](https://railway.app) for backend
   - [Sentry](https://sentry.io) for monitoring

2. **Configure secrets**:
   - Add GitHub repository secrets
   - Set up environment variables in Vercel/Railway

3. **Test deployment**:
   - Create a test branch
   - Push to trigger staging deployment
   - Verify everything works

4. **Set up monitoring**:
   - Configure Sentry
   - Set up health checks
   - Add deployment notifications
