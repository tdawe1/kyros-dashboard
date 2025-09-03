#!/bin/bash

# Exit on any error
set -e

echo "Starting Kyros Dashboard backend..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"

# Validate PORT variable
if [ -z "$PORT" ]; then
    echo "Error: PORT environment variable is not set"
    exit 1
fi

# Validate PORT is a number
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "Error: PORT must be a number, got: $PORT"
    exit 1
fi

# Validate PORT is in valid range
if [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
    echo "Error: PORT must be between 1 and 65535, got: $PORT"
    exit 1
fi

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
