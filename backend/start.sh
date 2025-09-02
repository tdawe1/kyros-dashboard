#!/bin/bash

# Exit on any error
set -e

echo "Starting Kyros Dashboard backend..."

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT
