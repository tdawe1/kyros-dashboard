#!/bin/bash

# Kyros Dashboard - Backend Quick Start Script
echo "🚀 Starting Kyros Dashboard Backend..."

# Check if we're in the right directory
if [ ! -f "api/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Navigate to API directory
cd api

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Copy test environment if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Setting up test environment..."
    cp env.test .env
    echo "✅ Created .env file from test configuration"
fi

# Start the server
echo "🌟 Starting FastAPI server on http://localhost:8000"
echo "📚 API docs available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --reload --port 8000
