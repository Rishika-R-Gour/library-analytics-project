#!/bin/bash

# Test API Connectivity
echo "🔍 Testing API Connectivity..."
echo "================================"

echo "Testing Advanced API (Port 5002)..."
if curl -s http://localhost:5002/api/health > /dev/null; then
    echo "✅ Advanced API: ONLINE"
else
    echo "❌ Advanced API: OFFLINE"
fi

echo "Testing Library API (Port 5003)..."
if curl -s http://localhost:5003/api/health > /dev/null; then
    echo "✅ Library API: ONLINE"
else
    echo "❌ Library API: OFFLINE"
fi

echo "Testing Enhanced Dashboard (Port 8501)..."
if curl -s http://localhost:8501 > /dev/null; then
    echo "✅ Enhanced Dashboard: ONLINE"
else
    echo "❌ Enhanced Dashboard: OFFLINE"
fi

echo "Testing ML Dashboard (Port 8503)..."
if curl -s http://localhost:8503 > /dev/null; then
    echo "✅ ML Dashboard: ONLINE"
else
    echo "❌ ML Dashboard: OFFLINE"
fi

echo ""
echo "📊 All services status checked!"
