#!/bin/bash

#!/bin/bash

# Kyros Dashboard - Backend Quick Start Script
echo "🚀 Starting Kyros Dashboard Backend..."

# Ensure we're at repo root and backend exists
if [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

cd backend

# Prefer Poetry if available
if [ -f pyproject.toml ]; then
    if ! command -v poetry >/dev/null 2>&1; then
        echo "⚠️  Poetry not found. Installing Poetry locally..."
        curl -sSL https://install.python-poetry.org | python3 - >/dev/null 2>&1 || true
        export PATH="$HOME/.local/bin:$PATH"
    fi
    if command -v poetry >/dev/null 2>&1; then
        echo "📥 Installing dependencies with Poetry..."
        poetry install --no-interaction --no-ansi
        echo "🌟 Starting FastAPI server on http://localhost:8000"
        echo "📚 API docs: http://localhost:8000/docs"
        poetry run uvicorn main:app --reload --port 8000
    else
        echo "❌ Poetry is required but could not be installed automatically."
        exit 1
    fi
else
    # Fallback to venv + pip if requirements.txt exists
    if [ ! -f requirements.txt ]; then
        echo "❌ No pyproject.toml or requirements.txt found in backend/"
        exit 1
    fi
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    echo "📥 Installing dependencies with pip..."
    pip install -r requirements.txt
    echo "🌟 Starting FastAPI server on http://localhost:8000"
    echo "📚 API docs: http://localhost:8000/docs"
    uvicorn main:app --reload --port 8000
fi
