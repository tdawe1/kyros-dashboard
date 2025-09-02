#!/bin/bash

# Phase B Development Startup Script

echo "Starting Kyros Dashboard API with Phase B features..."

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Warning: Redis is not running. Some features may not work properly."
    echo "Start Redis with: redis-server"
fi

# Set default environment variables if not set
export REDIS_URL=${REDIS_URL:-"redis://localhost:6379"}
export MAX_INPUT_CHARACTERS=${MAX_INPUT_CHARACTERS:-"100000"}
export MAX_TOKENS_PER_JOB=${MAX_TOKENS_PER_JOB:-"50000"}
export DAILY_JOB_LIMIT=${DAILY_JOB_LIMIT:-"10"}
export RATE_LIMIT_REQUESTS=${RATE_LIMIT_REQUESTS:-"100"}
export RATE_LIMIT_WINDOW=${RATE_LIMIT_WINDOW:-"3600"}
export RATE_LIMIT_BURST=${RATE_LIMIT_BURST:-"10"}

echo "Configuration:"
echo "  Redis URL: $REDIS_URL"
echo "  Max Input Characters: $MAX_INPUT_CHARACTERS"
echo "  Max Tokens Per Job: $MAX_TOKENS_PER_JOB"
echo "  Daily Job Limit: $DAILY_JOB_LIMIT"
echo "  Rate Limit: $RATE_LIMIT_REQUESTS requests per $RATE_LIMIT_WINDOW seconds"
echo ""

# Start the API server
echo "Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
