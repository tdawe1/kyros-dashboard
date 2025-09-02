#!/bin/bash

# Exit on any error
set -e

echo "Starting Kyros Dashboard backend..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Port: $PORT"

# Check if alembic is available
if command -v alembic &> /dev/null; then
    echo "Running database migrations..."
    alembic upgrade head
else
    echo "Alembic not found, skipping migrations"
fi

# Start the application
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT
