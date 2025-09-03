#!/bin/bash

# ==============================================================================
# Kyros Dashboard - Agent Development Environment Setup Script
# ==============================================================================
#
# This script automates the setup of a complete development environment for
# AI agents working on the Kyros Dashboard project.
#
# It performs the following steps:
#   1. Sets up the Python backend environment using a virtual environment.
#   2. Installs all required Python dependencies.
#   3. Sets up the Node.js frontend environment.
#   4. Installs all required npm packages.
#   5. Creates .env files for both backend and frontend for demo mode.
#   6. Provides instructions for activating the environment.
#
# Usage:
#   ./setup.sh
#
# ==============================================================================

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Helper Functions ---
echo_green() {
  echo -e "\033[0;32m$1\033[0m"
}

echo_bold() {
  echo -e "\033[1m$1\033[0m"
}

# --- Backend Setup ---
echo_bold "Setting up the Python backend..."

# Check if python3 is available
if ! command -v python3 &> /dev/null
then
    echo "Error: python3 could not be found. Please install Python 3.11+."
    exit 1
fi

# Create a virtual environment
if [ ! -d "backend/venv" ]; then
  echo "Creating Python virtual environment in backend/venv..."
  python3 -m venv backend/venv
else
  echo "Python virtual environment already exists."
fi

# Activate the virtual environment and install dependencies
echo "Installing Python dependencies from backend/requirements.txt..."
source backend/venv/bin/activate
pip install -r backend/requirements.txt
deactivate

echo_green "Backend setup complete."
echo ""


# --- Frontend Setup ---
echo_bold "Setting up the Node.js frontend..."

# Check if npm is available
if ! command -v npm &> /dev/null
then
    echo "Error: npm could not be found. Please install Node.js and npm."
    exit 1
fi

# Install npm packages
echo "Installing npm dependencies in frontend/..."
(cd frontend && npm install)

echo_green "Frontend setup complete."
echo ""


# --- Environment Configuration ---
echo_bold "Configuring environment for Demo Mode..."

# Create backend .env file
echo "Creating backend/.env file..."
cat << EOF > backend/.env
# Backend Environment Variables
# This file is configured for agent-friendly demo mode.

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Security (use placeholder keys for demo mode)
SECRET_KEY=super-secret-key-for-agents
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database (using a local SQLite DB for simplicity)
DATABASE_URL=sqlite:///./test.db

# Redis (mocked in tests, but set for local dev)
REDIS_URL=redis://localhost:6379
REDIS_SECURITY_MODE=fail_open

# OpenAI (not required for demo mode)
OPENAI_API_KEY=
EOF

# Create frontend .env file
echo "Creating frontend/.env.local file..."
cat << EOF > frontend/.env.local
# Frontend Environment Variables
# This file is configured for agent-friendly demo mode.

# The backend API URL
VITE_API_URL=http://localhost:8000
EOF

echo_green "Environment configuration complete."
echo ""


# --- Final Instructions ---
echo_bold "🎉 Setup is complete! 🎉"
echo ""
echo "To activate the development environment, run the following command:"
echo_green "source backend/venv/bin/activate"
echo ""
echo "Once activated, you can run the backend and frontend servers:"
echo "- To run the backend: uvicorn main:app --reload --app-dir backend"
echo "- To run the frontend: cd frontend && npm run dev"
echo ""
echo "Happy coding!"
