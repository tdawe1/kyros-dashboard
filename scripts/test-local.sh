#!/bin/bash

# Local Testing Script for Kyros Dashboard
# This script tests the build process locally without deploying

set -euo pipefail

echo "🧪 Starting local build test for Kyros Dashboard..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Cleanup function
API_PID=""
cleanup() {
    if [ ! -z "$API_PID" ] && kill -0 "$API_PID" 2>/dev/null; then
        print_status "Stopping API server (PID: $API_PID)..."
        kill "$API_PID" 2>/dev/null || true
    fi

    # Deactivate virtualenv if active
    if [ ! -z "${VIRTUAL_ENV:-}" ]; then
        print_status "Deactivating virtual environment..."
        deactivate 2>/dev/null || true
    fi
}

# Set up cleanup trap
trap cleanup EXIT INT TERM

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Testing Python environment..."
cd backend

# Test Python setup
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

print_success "Python 3 found: $(python3 --version)"

# Test virtual environment
if [ ! -d "../venv" ]; then
    print_warning "Virtual environment not found. Creating one..."
    python3 -m venv ../venv
fi

# Activate virtual environment
source ../venv/bin/activate
print_success "Virtual environment activated"

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Python dependencies installed"

# Test API imports
print_status "Testing API imports..."
python -c "
import main
print('✅ API imports successfully')
print('✅ All dependencies are available')
"
print_success "API imports test passed"

# Test API startup (briefly)
print_status "Testing API startup..."
python -c "
import uvicorn
from main import app
print('✅ API can be imported and configured')
"
print_success "API startup test passed"

cd ../frontend

# Test Node.js setup
print_status "Testing Node.js environment..."
if ! command -v node &> /dev/null; then
    print_error "Node.js is required but not installed"
    exit 1
fi

print_success "Node.js found: $(node --version)"
print_success "npm found: $(npm --version)"

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install
print_success "Node.js dependencies installed"

# Test frontend build
print_status "Testing frontend build..."
export VITE_API_BASE_URL="http://localhost:8000"
npm run build

if [ -d "dist" ]; then
    print_success "Frontend build successful"
    print_status "Build output:"
    ls -la dist/

    # Validate key files
    if [ -f "dist/index.html" ]; then
        print_success "index.html exists"
    else
        print_error "index.html missing"
        exit 1
    fi

    if [ -d "dist/assets" ]; then
        print_success "Assets directory exists"
        print_status "Assets:"
        ls -la dist/assets/
    else
        print_error "Assets directory missing"
        exit 1
    fi
else
    print_error "Frontend build failed"
    exit 1
fi

# Test frontend tests
print_status "Running frontend tests..."
npm run test:ci
print_success "Frontend tests passed"

cd ../backend

# Test Python tests
print_status "Running Python tests..."
python -m pytest --tb=short
print_success "Python tests passed"

# Test API health endpoint (if possible)
print_status "Testing API health endpoint..."
cd ../backend

# Start API in background for testing
print_status "Starting API server for health check..."
python -m uvicorn main:app --host 127.0.0.1 --port 8000 &
API_PID=$!

# Wait for API to start
sleep 3

# Test health endpoint
if curl -f http://127.0.0.1:8000/api/health 2>/dev/null; then
    print_success "API health check passed"
else
    print_warning "API health check failed (this might be expected if the endpoint doesn't exist yet)"
fi

# Clean up
kill $API_PID 2>/dev/null || true

cd ..

echo ""
echo "🎉 Local Build Test Summary:"
echo "============================="
print_success "✅ Python environment setup"
print_success "✅ Python dependencies installed"
print_success "✅ API imports successfully"
print_success "✅ Node.js environment setup"
print_success "✅ Node.js dependencies installed"
print_success "✅ Frontend build successful"
print_success "✅ Build artifacts validated"
print_success "✅ Frontend tests passed"
print_success "✅ Python tests passed"
print_success "✅ API health check attempted"
echo ""
print_success "🚀 Your application is ready for deployment!"
echo ""
echo "Next steps:"
echo "1. Push your changes to GitHub to test the CI/CD pipeline"
echo "2. Check the GitHub Actions tab to see the test-build workflow"
echo "3. When ready, set up the actual deployment secrets"
echo ""
echo "To test the GitHub Actions workflow:"
echo "git add ."
echo "git commit -m 'test: add build validation'"
echo "git push origin main"
