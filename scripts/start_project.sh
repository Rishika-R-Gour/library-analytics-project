#!/bin/bash

# Library Analytics Project - Quick Start Script
# This script will start the API server and open the test interface

echo "🚀 Starting Library Analytics Project..."
echo "======================================"

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo "❌ Virtual environment not found. Please create it first."
    exit 1
fi

# Check if database exists
if [ ! -f "notebooks/library.db" ]; then
    echo "❌ Database not found at notebooks/library.db"
    exit 1
fi

echo "✅ Virtual environment found"
echo "✅ Database found"

# Start API server in background
echo "🌐 Starting API server on http://localhost:8000..."
./env/bin/python simple_api.py &
API_PID=$!

# Wait a moment for server to start
sleep 3

# Test if API is running
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ API server is running successfully!"
    echo ""
    echo "📊 Available endpoints:"
    echo "   GET /         - Welcome message"
    echo "   GET /health   - Health check with DB connection"
    echo "   GET /stats    - Library statistics"
    echo ""
    echo "🌐 API Base URL: http://localhost:8000"
    echo "📋 Test Interface: file://$PWD/api_test.html"
    echo ""
    echo "To stop the API server, run: kill $API_PID"
    echo "Or press Ctrl+C if running in foreground"
    echo ""
    echo "🎉 Phase 1 Complete! Your Library Analytics API is ready!"
else
    echo "❌ Failed to start API server"
    kill $API_PID 2>/dev/null
    exit 1
fi
