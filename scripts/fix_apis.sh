#!/bin/bash

# Fix API Startup Issues
echo "🔧 Fixing API Connection Issues..."

# Set paths
PROJECT_ROOT="/Users/rishikagour/library_analytics_project"
PYTHON_PATH="$PROJECT_ROOT/env/bin/python"

cd "$PROJECT_ROOT"

# Create logs directory
mkdir -p logs

# Kill existing processes
echo "🛑 Stopping existing API processes..."
pkill -f "advanced_api.py" 2>/dev/null || true
pkill -f "simple_library_api.py" 2>/dev/null || true
sleep 2

# Check if Python virtual environment works
echo "🐍 Testing Python environment..."
if ! $PYTHON_PATH --version > /dev/null 2>&1; then
    echo "❌ Virtual environment Python not working, using system Python"
    PYTHON_PATH="python3"
fi

echo "✅ Using Python: $PYTHON_PATH"

# Start Advanced API (Port 5002)
echo "🚀 Starting Advanced API on port 5002..."
cd app
nohup $PYTHON_PATH advanced_api.py > ../logs/advanced_api.log 2>&1 &
ADVANCED_PID=$!
echo "✅ Advanced API started with PID: $ADVANCED_PID"

# Start Library API (Port 5003)
echo "🚀 Starting Library API on port 5003..."
nohup $PYTHON_PATH simple_library_api.py > ../logs/library_api.log 2>&1 &
LIBRARY_PID=$!
echo "✅ Library API started with PID: $LIBRARY_PID"

cd ..

# Wait a moment for services to start
echo "⏳ Waiting for APIs to initialize..."
sleep 5

# Test the APIs
echo "🔍 Testing API connections..."

# Test Advanced API
if curl -s http://localhost:5002/api/health > /dev/null 2>&1; then
    echo "✅ Advanced API (Port 5002) - Working!"
else
    echo "❌ Advanced API (Port 5002) - Not responding"
    echo "📋 Checking logs..."
    tail -n 10 logs/advanced_api.log 2>/dev/null || echo "No logs found"
fi

# Test Library API
if curl -s http://localhost:5003/api/health > /dev/null 2>&1; then
    echo "✅ Library API (Port 5003) - Working!"
else
    echo "❌ Library API (Port 5003) - Not responding"
    echo "📋 Checking logs..."
    tail -n 10 logs/library_api.log 2>/dev/null || echo "No logs found"
fi

echo ""
echo "🔗 API URLs:"
echo "   🔧 Advanced API:  http://localhost:5002/api/health"
echo "   📚 Library API:   http://localhost:5003/api/health"
echo ""
echo "📋 Check logs:"
echo "   Advanced API: tail -f logs/advanced_api.log"
echo "   Library API:  tail -f logs/library_api.log"
