#!/bin/bash

# Library Analytics Project - Phase 2 Integration Script
# This script starts both the Complex API and Streamlit Dashboard

echo "🚀 Library Analytics - Phase 2 Integration"
echo "============================================="

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

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    pkill -f "python.*app.api" 2>/dev/null
    pkill -f "streamlit run" 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

echo ""
echo "🌐 Starting Complex Flask API..."
./env/bin/python -c "
from app.api import LibraryAnalyticsAPI
import threading
import time

api = LibraryAnalyticsAPI()
app = api.app
print('✅ Complex API started on http://localhost:5001')
print('📋 Available endpoints:')
print('   🔐 POST /api/auth/login - Authentication')
print('   💚 GET  /api/health - Health check') 
print('   📊 GET  /api/dashboard/stats - Dashboard stats')
print('   🔮 POST /api/predictions/overdue - Overdue predictions')
print('   👥 POST /api/predictions/churn - Churn predictions')
print('   📚 GET  /api/recommendations/{member_id} - Book recommendations')
print('   👤 GET  /api/members - Members list')
print('   🤖 GET  /api/models/status - Models status')
print('')
app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
" &

API_PID=$!

# Wait for API to start
echo "⏳ Waiting for API to initialize..."
sleep 5

# Test if API is running
if curl -s http://localhost:5001/api/health > /dev/null; then
    echo "✅ Complex API is running successfully!"
else
    echo "❌ Failed to start Complex API"
    kill $API_PID 2>/dev/null
    exit 1
fi

echo ""
echo "📊 Starting Streamlit Dashboard..."

# Start Streamlit dashboard
echo "" | ./env/bin/python -m streamlit run dashboard/library_dashboard.py --server.port 8501 > /dev/null 2>&1 &
DASHBOARD_PID=$!

# Wait for dashboard to start
echo "⏳ Waiting for dashboard to initialize..."
sleep 8

# Test if dashboard is running
if curl -s http://localhost:8501 > /dev/null; then
    echo "✅ Streamlit Dashboard is running successfully!"
else
    echo "❌ Failed to start Streamlit Dashboard"
    kill $API_PID 2>/dev/null
    kill $DASHBOARD_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎉 Phase 2 Integration Complete!"
echo "================================="
echo ""
echo "📋 Services Running:"
echo "   🌐 Complex API:      http://localhost:5001"
echo "   📊 Dashboard:        http://localhost:8501" 
echo "   🧪 API Test Page:    file://$PWD/complex_api_test.html"
echo ""
echo "🔐 Demo Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📖 How to Use:"
echo "   1. Open dashboard at http://localhost:8501"
echo "   2. Login with demo credentials"
echo "   3. Explore ML predictions and analytics"
echo "   4. Use API test page to test individual endpoints"
echo ""
echo "💡 Features Available:"
echo "   ✅ JWT Authentication"
echo "   ✅ Real-time ML Predictions" 
echo "   ✅ Interactive Dashboard"
echo "   ✅ Book Recommendations"
echo "   ✅ User Churn Analysis"
echo "   ✅ Overdue Predictions"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Keep script running and wait for user to stop
wait
