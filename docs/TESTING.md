# Testing Guide

This guide covers how to test your Kyros Dashboard application locally and validate the deployment process without actually deploying to production services.

## 🧪 Local Testing Options

### Option 1: Quick Local Test (Recommended)

Run the automated test script to validate everything works:

```bash
./test-local.sh
```

This script will:
- ✅ Test Python environment and dependencies
- ✅ Test Node.js environment and dependencies
- ✅ Run all tests (Python and frontend)
- ✅ Build the frontend application
- ✅ Validate build artifacts
- ✅ Test API startup and health checks
- ✅ Provide a comprehensive summary

### Option 2: Manual Step-by-Step Testing

#### Test Backend (API)
```bash
# Navigate to the backend directory
cd backend

# Install dependencies
poetry install

# Test imports
poetry run python -c "import main; print('API imports successfully')"

# Run tests
poetry run pytest

# Test API startup
poetry run uvicorn main:app --reload
# Visit http://localhost:8000/api/health
```

#### Test Frontend (UI)
```bash
# Install dependencies
cd ui
npm install

# Run tests
npm test

# Build application
npm run build

# Test build output
ls -la dist/
```

### Option 3: Docker Testing

Test the complete application stack using Docker:

```bash
# Build and start test environment
docker-compose -f docker-compose.test.yml up --build

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Health: http://localhost:8000/api/health
```

## 🚀 GitHub Actions Testing

### Test Build Workflow

The `.github/workflows/test-build.yml` workflow runs automatically on:
- Push to any branch
- Pull requests

This workflow:
- ✅ Tests both frontend and backend builds
- ✅ Runs all tests and quality checks
- ✅ Validates build artifacts
- ✅ Tests API health endpoints
- ✅ Uploads build artifacts for inspection
- ❌ **Does NOT deploy anywhere** (safe for testing)

### Trigger the Test Workflow

1. **Push your changes**:
   ```bash
   git add .
   git commit -m "test: validate build process"
   git push origin main
   ```

2. **Check GitHub Actions**:
   - Go to your repository on GitHub
   - Click the "Actions" tab
   - Look for "Test Build and Validation" workflow
   - Click on it to see detailed logs

3. **Download build artifacts**:
   - In the workflow run, scroll to "Upload build artifacts"
   - Download the artifacts to inspect the built files

## 🔍 What Gets Tested

### Backend (API) Tests
- ✅ Python environment setup
- ✅ Dependency installation
- ✅ Code imports and syntax
- ✅ Unit tests (if any)
- ✅ API startup and health checks
- ✅ Security scanning (Bandit)

### Frontend (UI) Tests
- ✅ Node.js environment setup
- ✅ Dependency installation
- ✅ Code compilation
- ✅ Unit tests
- ✅ Build process
- ✅ Asset generation
- ✅ Security scanning (npm audit)

### Integration Tests
- ✅ API health endpoint accessibility
- ✅ Frontend-backend communication setup
- ✅ Build artifact validation
- ✅ Environment variable handling

## 📊 Test Results

### Successful Test Output
When everything works, you'll see:
```
🎉 Local Build Test Summary:
=============================
✅ Python environment setup
✅ Python dependencies installed
✅ API imports successfully
✅ Node.js environment setup
✅ Node.js dependencies installed
✅ Frontend build successful
✅ Build artifacts validated
✅ Frontend tests passed
✅ Python tests passed
✅ API health check passed

🚀 Your application is ready for deployment!
```

### GitHub Actions Success
In GitHub Actions, you'll see:
- ✅ All jobs completed successfully
- ✅ Build artifacts uploaded
- ✅ No deployment errors
- ✅ All quality checks passed

## 🐛 Troubleshooting

### Common Issues

1. **Python Import Errors**:
   ```bash
   # Reinstall dependencies
   cd backend
   poetry install
   ```

2. **Node.js Build Failures**:
   ```bash
   # Clear npm cache
   npm cache clean --force

   # Delete node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **API Health Check Fails**:
   - Check if the `/api/health` endpoint exists in your API
   - Verify the API starts without errors
   - Check if port 8000 is available

4. **Frontend Build Issues**:
   ```bash
   # Check for TypeScript/JavaScript errors
   npm run lint

   # Check build configuration
   cat ui/vite.config.js
   ```

### Debug Commands

```bash
# Check Python environment
python --version
poetry show

# Check Node.js environment
node --version
npm --version

# Check if ports are in use
lsof -i :3000
lsof -i :8000

# Check build output
ls -la ui/dist/
cat ui/dist/index.html
```

## 🎯 Next Steps After Testing

Once your tests pass:

1. **Review the build artifacts** to ensure everything looks correct
2. **Check the GitHub Actions logs** for any warnings or issues
3. **Test the application manually** by running it locally
4. **When ready for real deployment**, set up the production secrets and deploy

## 📝 Test Checklist

Before considering your application ready:

- [ ] Local test script runs without errors
- [ ] GitHub Actions test-build workflow passes
- [ ] Frontend builds successfully
- [ ] Backend starts without errors
- [ ] API health endpoint responds
- [ ] All tests pass
- [ ] No security vulnerabilities found
- [ ] Build artifacts are valid
- [ ] Application runs locally without issues

## 🔧 Customizing Tests

### Adding More Tests
- Add tests to `api/tests/` for backend testing
- Add tests to `ui/src/` for frontend testing
- Update the test scripts to include your new tests

### Modifying Test Workflow
- Edit `.github/workflows/test-build.yml` to add more validation steps
- Add environment variables for testing
- Include additional quality checks

### Local Test Customization
- Modify `test-local.sh` to include your specific test requirements
- Add custom validation steps
- Include additional environment setup
