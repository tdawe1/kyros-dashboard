#!/bin/bash

# Kyros Dashboard Test Runner
# This script runs all tests (unit, integration, and E2E) for the project

set -e

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Parse command line arguments
RUN_BACKEND=true
RUN_FRONTEND=true
RUN_E2E=true
RUN_COVERAGE=true
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            RUN_FRONTEND=false
            RUN_E2E=false
            shift
            ;;
        --frontend-only)
            RUN_BACKEND=false
            RUN_E2E=false
            shift
            ;;
        --e2e-only)
            RUN_BACKEND=false
            RUN_FRONTEND=false
            shift
            ;;
        --no-coverage)
            RUN_COVERAGE=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --backend-only    Run only backend tests"
            echo "  --frontend-only   Run only frontend tests"
            echo "  --e2e-only        Run only E2E tests"
            echo "  --no-coverage     Skip coverage reports"
            echo "  --verbose         Verbose output"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_status "Starting Kyros Dashboard Test Suite"

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists python3; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

if ! command_exists node; then
    print_error "Node.js is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    print_error "npm is required but not installed"
    exit 1
fi

# Check if Redis is running (for backend tests)
if [ "$RUN_BACKEND" = true ] || [ "$RUN_E2E" = true ]; then
    if ! command_exists redis-cli; then
        print_warning "Redis CLI not found. Backend tests may fail if Redis is not running."
    else
        if ! redis-cli ping >/dev/null 2>&1; then
            print_warning "Redis is not running. Starting Redis server..."
            if command_exists redis-server; then
                redis-server --daemonize yes
                sleep 2
                if redis-cli ping >/dev/null 2>&1; then
                    print_success "Redis server started"
                else
                    print_error "Failed to start Redis server"
                    exit 1
                fi
            else
                print_error "Redis server not found. Please install and start Redis manually."
                exit 1
            fi
        else
            print_success "Redis is running"
        fi
    fi
fi

# Backend Tests
if [ "$RUN_BACKEND" = true ]; then
    print_status "Running backend tests..."

    cd backend

    # Install Python dependencies
    print_status "Installing Python dependencies..."
    if [ -f requirements.txt ]; then
        # Use virtual environment if it exists, otherwise use system python
        if [ -f "../venv/bin/pip" ]; then
            ../venv/bin/pip install -r requirements.txt
        else
            python3 -m pip install -r requirements.txt
        fi
    else
        print_error "requirements.txt not found in backend directory"
        exit 1
    fi

    # Run linting
    print_status "Running linting checks..."
    if command_exists ruff; then
        ruff check . || print_warning "Linting issues found"
    fi

    if command_exists black; then
        black --check . || print_warning "Formatting issues found"
    fi

    # Run tests
    print_status "Running pytest..."
    if [ "$RUN_COVERAGE" = true ]; then
        if [ -f "../venv/bin/pytest" ]; then
            ../venv/bin/pytest --cov=. --cov-report=term-missing --cov-report=html -v
        else
            pytest --cov=. --cov-report=term-missing --cov-report=html -v
        fi
    else
        if [ -f "../venv/bin/pytest" ]; then
            ../venv/bin/pytest -v
        else
            pytest -v
        fi
    fi

    if [ $? -eq 0 ]; then
        print_success "Backend tests passed"
    else
        print_error "Backend tests failed"
        exit 1
    fi

    cd ..
fi

# Frontend Tests
if [ "$RUN_FRONTEND" = true ]; then
    print_status "Running frontend tests..."

    cd frontend

    # Install Node.js dependencies
    print_status "Installing Node.js dependencies..."
    if [ -f package.json ]; then
        npm ci
    else
        print_error "package.json not found in frontend directory"
        exit 1
    fi

    # Run linting
    print_status "Running ESLint..."
    npm run lint || print_warning "Linting issues found"

    # Run format check
    print_status "Running Prettier format check..."
    npm run format:check || print_warning "Formatting issues found"

    # Run tests
    print_status "Running Vitest..."
    if [ "$RUN_COVERAGE" = true ]; then
        npm run test:coverage
    else
        npm run test:run
    fi

    if [ $? -eq 0 ]; then
        print_success "Frontend tests passed"
    else
        print_error "Frontend tests failed"
        exit 1
    fi

    cd ..
fi

# E2E Tests
if [ "$RUN_E2E" = true ]; then
    print_status "Running E2E tests..."

    # Install API dependencies for E2E
    print_status "Installing API dependencies for E2E tests..."
    cd backend
    if [ -f "../venv/bin/pip" ]; then
        ../venv/bin/pip install -r requirements.txt
    else
        python3 -m pip install -r requirements.txt
    fi
    cd ..

    # Install UI dependencies for E2E
    print_status "Installing UI dependencies for E2E tests..."
    cd frontend
    npm ci || npm install

    # Check if Playwright is installed
    if ! npm list @playwright/test >/dev/null 2>&1; then
        print_status "Installing Playwright..."
        npm install @playwright/test
        npx playwright install
    fi

    # Start backend server in background
    print_status "Starting backend server..."
    cd ../backend
    if port_in_use 8000; then
        print_warning "Port 8000 is already in use. Please stop the service and try again."
        exit 1
    fi

    uvicorn main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    sleep 5

    # Start frontend server in background
    print_status "Starting frontend server..."
    cd ../frontend
    if port_in_use 5173; then
        print_warning "Port 5173 is already in use. Please stop the service and try again."
        kill $BACKEND_PID
        exit 1
    fi

    npm run dev &
    FRONTEND_PID=$!
    sleep 10

    # Run Playwright tests
    print_status "Running Playwright E2E tests..."
    npx playwright test

    if [ $? -eq 0 ]; then
        print_success "E2E tests passed"
    else
        print_error "E2E tests failed"
        # Clean up background processes
        kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
        exit 1
    fi

    # Clean up background processes
    print_status "Stopping test servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true

    cd ..
fi

print_success "All tests completed successfully!"

# Show coverage reports if generated
if [ "$RUN_COVERAGE" = true ]; then
    print_status "Coverage reports generated:"
    if [ "$RUN_BACKEND" = true ] && [ -d "backend/htmlcov" ]; then
        echo "  Backend: backend/htmlcov/index.html"
    fi
    if [ "$RUN_FRONTEND" = true ] && [ -d "frontend/coverage" ]; then
        echo "  Frontend: frontend/coverage/index.html"
    fi
fi
