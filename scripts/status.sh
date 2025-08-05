#!/bin/bash

# Simple Status Check
echo "🔍 Library Analytics System Status"
echo "================================="
echo ""

# Check services
if curl -s http://localhost:5002/api/health > /dev/null 2>&1; then
    echo "✅ Advanced API (5002) - Running"
else
    echo "❌ Advanced API (5002) - Down"
fi

if curl -s http://localhost:5003/api/health > /dev/null 2>&1; then
    echo "✅ Library API (5003) - Running"
else
    echo "❌ Library API (5003) - Down"
fi

if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "✅ Enhanced Dashboard (8501) - Running"
else
    echo "❌ Enhanced Dashboard (8501) - Down"
fi

if curl -s http://localhost:8503 > /dev/null 2>&1; then
    echo "✅ ML Dashboard (8503) - Running"
else
    echo "❌ ML Dashboard (8503) - Down"
fi

echo ""
echo "🔗 URLs:"
echo "   📊 http://localhost:8501 (Enhanced Dashboard)"
echo "   🤖 http://localhost:8503 (ML Predictions)"
echo "   🔧 http://localhost:5002 (API)"
echo "   📚 http://localhost:5003 (Library API)"
