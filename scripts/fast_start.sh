#!/bin/bash

# Fast Phase 5 Startup - No delays
echo "🚀 Fast Phase 5 Startup"

# Use the correct Python path
PYTHON="/Users/rishikagour/library_analytics_project/env/bin/python"

# Kill any existing processes
pkill -f "advanced_api.py|simple_library_api.py" 2>/dev/null || true
sleep 1

echo "Starting APIs..."

# Start Advanced API (Port 5002)
cd /Users/rishikagour/library_analytics_project/app
$PYTHON advanced_api.py &
echo "✅ Advanced API starting on port 5002"

# Start Library API (Port 5003)  
$PYTHON simple_library_api.py &
echo "✅ Library API starting on port 5003"

# Start Streamlit Dashboards
cd /Users/rishikagour/library_analytics_project/dashboard

# Enhanced Dashboard (Port 8501)
$PYTHON -m streamlit run advanced_dashboard.py --server.port 8501 &
echo "✅ Enhanced Dashboard starting on port 8501"

# Original ML Dashboard (Port 8503) 
$PYTHON -m streamlit run library_dashboard.py --server.port 8503 &
echo "✅ Original ML Dashboard starting on port 8503"

cd /Users/rishikagour/library_analytics_project
sleep 5

# Quick test
echo "Testing services..."
curl -s http://localhost:5002/api/health > /dev/null && echo "✅ Port 5002 working" || echo "❌ Port 5002 not ready"
curl -s http://localhost:5003/api/health > /dev/null && echo "✅ Port 5003 working" || echo "❌ Port 5003 not ready"
curl -s http://localhost:8501 > /dev/null && echo "✅ Port 8501 working" || echo "❌ Port 8501 not ready"
curl -s http://localhost:8503 > /dev/null && echo "✅ Port 8503 working" || echo "❌ Port 8503 not ready"

echo ""
echo "🎉 All services ready! Access with:"
echo "   🔧 Advanced API:      http://localhost:5002/"
echo "   📚 Library API:       http://localhost:5003/"
echo "   📊 Enhanced Dashboard: http://localhost:8501"
echo "   🤖 ML Predictions:    http://localhost:8503"
