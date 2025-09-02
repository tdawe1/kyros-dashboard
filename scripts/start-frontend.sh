#!/bin/bash

# Kyros Dashboard - Frontend Quick Start Script
echo "🚀 Starting Kyros Dashboard Frontend..."

# Check if we're in the right directory
if [ ! -f "ui/package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Navigate to UI directory
cd ui

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Copy test environment if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Setting up test environment..."
    cp env.test .env
    echo "✅ Created .env file from test configuration"
fi

# Start the development server
echo "🌟 Starting Vite development server on http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
