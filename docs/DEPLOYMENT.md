# Deployment Guide

This guide covers the complete deployment setup for the Kyros Dashboard, including automatic deployment after merging to the main branch.

## 🚀 CI/CD Pipeline Overview

The project uses GitHub Actions for CI/CD with the following workflow:

1. **Pull Request Checks**: Comprehensive testing and validation on every PR
2. **Code Review**: Required approval before merging to main
3. **Branch Protection**: Prevents direct pushes to main branch
4. **Staging Deployment**: Automatic deployment to staging environment for feature branches
5. **Production Deployment**: Automatic deployment to production only after PR approval and all checks pass

## 📋 Prerequisites

### Required Accounts
- GitHub repository with Actions enabled
- Vercel account (for frontend deployment)
- Railway or Render account (for backend deployment)
- Slack workspace (optional, for notifications)

### Required Secrets

#### GitHub Repository Secrets
Add these secrets in your GitHub repository under Settings → Secrets and variables → Actions:

```bash
# Vercel Configuration
VERCEL_TOKEN=your-vercel-token
VERCEL_ORG_ID=your-vercel-org-id
VERCEL_PROJECT_ID=your-vercel-project-id

# Railway Configuration (if using Railway)
RAILWAY_TOKEN=your-railway-token
RAILWAY_SERVICE_NAME=your-railway-service-name
RAILWAY_STAGING_SERVICE_NAME=your-railway-staging-service-name

# Render Configuration (if using Render)
RENDER_SERVICE_ID=your-render-service-id
RENDER_API_KEY=your-render-api-key

# Environment URLs
VITE_API_BASE_URL=https://api.kyros-dashboard.com
VITE_API_BASE_URL_STAGING=https://staging-api.kyros-dashboard.com

# Optional: Slack Notifications
SLACK_WEBHOOK=your-slack-webhook-url
```

## 🔧 Setup Instructions

### 1. Frontend Deployment (Vercel)

1. **Connect Repository to Vercel**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Set Root Directory to `ui`
   - Configure build settings:
     - Build Command: `npm run build`
     - Output Directory: `dist`
     - Install Command: `npm ci`

2. **Configure Environment Variables**:
   - In Vercel project settings, add:
     - `VITE_API_BASE_URL`: Your production API URL
     - Any other environment variables from `docs/CI_SECRETS.md`

3. **Get Vercel Credentials**:
   - Go to Vercel Account Settings → Tokens
   - Create a new token
   - Add to GitHub secrets as `VERCEL_TOKEN`
   - Get Org ID and Project ID from Vercel project settings

### 2. Backend Deployment (Railway)

1. **Create Railway Project**:
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Create new project
   - Connect your GitHub repository
   - Set Root Directory to `api`

2. **Configure Service**:
   - Railway will auto-detect Python and use `railway.json` config
   - Add environment variables from `docs/CI_SECRETS.md`
   - Set up custom domain if needed

3. **Get Railway Token**:
   - Go to Railway Account Settings → Tokens
   - Create new token
   - Add to GitHub secrets as `RAILWAY_TOKEN`

### 3. Backend Deployment (Render - Alternative)

1. **Create Render Service**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Create new Web Service
   - Connect your GitHub repository
   - Set Root Directory to `api`
   - Use `render.yaml` configuration

2. **Configure Environment**:
   - Add environment variables from `docs/CI_SECRETS.md`
   - Set up custom domain if needed

3. **Get Render API Key**:
   - Go to Render Account Settings → API Keys
   - Create new API key
   - Add to GitHub secrets as `RENDER_API_KEY`

## 🔄 Deployment Workflows

### Pull Request Process
- **Trigger**: Pull request to `main` or `develop` branches
- **Required Actions**:
  1. **Backend Tests**: Python unit tests, linting, formatting, security scan
  2. **Frontend Tests**: JavaScript/React unit tests, linting, formatting
  3. **E2E Tests**: End-to-end tests with Playwright
  4. **Security Scan**: Vulnerability scanning with Bandit
  5. **Build Verification**: Ensure both frontend and backend build successfully
  6. **Code Review**: Required approval from code owners
- **Result**: PR cannot be merged until all checks pass and review is approved

### Main Branch (Production)
- **Trigger**: Merge to `main` branch (after PR approval and all checks pass)
- **Actions**:
  1. Run all tests and quality checks (already passed in PR)
  2. Deploy frontend to Vercel (production)
  3. Deploy backend to Railway/Render (production)
  4. Send notification (if configured)

### Feature Branches (Staging)
- **Trigger**: Push to `develop` or `feature/*` branches
- **Actions**:
  1. Run quality checks
  2. Deploy to staging environment
  3. Comment on PR with staging URLs

### Branch Protection
- **Direct pushes to main**: ❌ Blocked
- **Required status checks**: ✅ All must pass
- **Required reviews**: ✅ At least 1 approval
- **Required conversation resolution**: ✅ All discussions resolved

## 🛡️ Branch Protection Setup

To enable branch protection and require code review:

1. **Follow the setup guide**: See `.github/BRANCH_PROTECTION_SETUP.md` for detailed instructions
2. **Configure required status checks**:
   - `Backend Tests`
   - `Frontend Tests`
   - `E2E Tests`
   - `Security Scan`
   - `Build Verification`
   - `PR Checks Summary`
3. **Set up code owners**: The `.github/CODEOWNERS` file automatically assigns reviewers

## 📝 Development Workflow

### For Contributors:
1. **Create feature branch**: `git checkout -b feature/your-feature-name`
2. **Make changes**: Commit frequently with clear messages [[memory:7940605]]
3. **Push branch**: `git push origin feature/your-feature-name`
4. **Create pull request**: Target the `main` branch
5. **Wait for checks**: All automated tests must pass
6. **Request review**: Code owners will be automatically assigned
7. **Address feedback**: Make requested changes and push updates
8. **Merge after approval**: Once approved and all checks pass

### For Reviewers:
- Review code quality, logic, and security
- Check that tests cover new functionality
- Ensure documentation is updated
- Approve only when satisfied with the changes

## 🛠️ Workflow Files

The following GitHub Actions workflows are configured:

### `.github/workflows/pr-checks.yml`
- **Purpose**: Comprehensive testing and validation for pull requests
- **Triggers**: Pull requests to `main` or `develop` branches
- **Jobs**:
  - Backend Tests (Python unit tests, linting, security)
  - Frontend Tests (JavaScript/React unit tests, linting)
  - E2E Tests (End-to-end testing with Playwright)
  - Security Scan (Vulnerability scanning)
  - Build Verification (Ensures both frontend and backend build)
  - PR Checks Summary (Overall status summary)

### `.github/workflows/deploy.yml`
- **Purpose**: Production deployment after PR approval
- **Triggers**: Push to `main` branch (after merge)
- **Jobs**:
  - Test (Re-runs all tests for final verification)
  - Deploy Frontend (Vercel production deployment)
  - Deploy Backend (Railway/Render production deployment)
  - Notify (Slack notifications)

### `.github/workflows/quality-checks.yml`
- **Purpose**: Additional quality assurance checks
- **Triggers**: Pull requests and pushes to main/develop
- **Jobs**: Security scanning, linting, build verification, performance checks

### `.github/workflows/test.yml`
- **Purpose**: Comprehensive test suite execution
- **Triggers**: Pull requests and pushes to main/develop/feature branches
- **Jobs**: Backend tests, frontend tests, E2E tests, security scanning

### `.github/workflows/staging.yml`
- **Purpose**: Staging deployment for feature branches
- **Triggers**: Push to develop or feature/* branches
- **Jobs**: Deploy to staging environment, comment on PR with staging URLs

## 🔍 Monitoring and Notifications

### Health Checks
- Frontend: Vercel automatically monitors deployment health
- Backend: Health check endpoint at `/api/health`

### Notifications
- GitHub Actions status updates
- Optional Slack notifications for deployment status
- PR comments with staging URLs

### Logs and Debugging
- GitHub Actions logs for CI/CD issues
- Vercel function logs for frontend issues
- Railway/Render logs for backend issues

## 🚨 Troubleshooting

### Common Issues

1. **Deployment Fails on Tests**:
   - Check test results in GitHub Actions
   - Fix failing tests before deployment
   - Ensure all dependencies are properly installed

2. **Environment Variables Missing**:
   - Verify all required secrets are set in GitHub
   - Check environment variable names match exactly
   - Ensure secrets are available in the correct environment

3. **Build Failures**:
   - Check build logs in GitHub Actions
   - Verify Node.js and Python versions
   - Ensure all dependencies are in package.json or pyproject.toml

4. **Vercel Deployment Issues**:
   - Check Vercel project settings
   - Verify build command and output directory
   - Check environment variables in Vercel dashboard

5. **Railway/Render Issues**:
   - Check service logs
   - Verify start command and port configuration
   - Ensure environment variables are set

### Debug Commands

```bash
# Test local build
cd frontend && npm run build
cd backend && poetry run python -c "import main; print('API imports successfully')"

# Check environment variables
echo $VITE_API_BASE_URL
# Check if OPENAI_API_KEY is set (without exposing the value)
if [ -n "$OPENAI_API_KEY" ]; then
  echo "✅ OPENAI_API_KEY is configured"
else
  echo "❌ OPENAI_API_KEY is not set"
fi

# Test API locally
cd backend && poetry run uvicorn main:app --reload
```

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Render Documentation](https://render.com/docs)
- [CI/CD Secrets Guide](CI_SECRETS.md)
- [Security Setup Guide](SECURITY_SETUP.md)

## 🔐 Security Considerations

- All secrets are stored securely in GitHub repository secrets
- Environment variables are not exposed in build logs
- Pre-commit hooks prevent accidental secret commits
- Security scanning runs on every PR
- Production deployments require main branch merge
- **Important**: VITE_* values are baked into the client bundle and must never contain secrets
- Store sensitive values only on the server or in backend-only environment variables
- Use server-side endpoints, GitHub secrets, or runtime server envs for secrets
- Use .env.local for local development only (never commit to version control)

## 📈 Performance Optimization

- Frontend builds are cached for faster deployments
- Dependencies are cached in GitHub Actions
- Bundle analysis runs on every PR
- Performance budgets can be configured in Vercel

## 🎯 Next Steps

1. Set up monitoring and alerting
2. Configure custom domains
3. Set up database migrations
4. Implement blue-green deployments
5. Add performance monitoring
6. Set up error tracking (Sentry)
