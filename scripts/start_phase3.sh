#!/bin/bash

# Library Analytics Project - Phase 3 Complete System Startup
# Advanced multi-role authentication and analytics platform

echo "🚀 Library Analytics - Phase 3: Advanced Features"
echo "=================================================="

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
    echo "🛑 Shutting down all services..."
    pkill -f "python.*advanced_api" 2>/dev/null
    pkill -f "streamlit run.*advanced_dashboard" 2>/dev/null
    pkill -f "python.*app.api" 2>/dev/null
    pkill -f "streamlit run.*library_dashboard" 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Setup Phase 3 database if needed
echo ""
echo "🔧 Setting up Phase 3 database tables..."
./env/bin/python setup_phase3_db.py

echo ""
echo "🌐 Starting Advanced API (Phase 3)..."
./env/bin/python app/advanced_api.py &
ADVANCED_API_PID=$!

# Wait for advanced API to start
echo "⏳ Waiting for Advanced API to initialize..."
sleep 6

# Test if advanced API is running
if curl -s http://localhost:5002/api/health > /dev/null; then
    echo "✅ Advanced API is running successfully!"
    
    # Get API info
    API_INFO=$(curl -s http://localhost:5002/api/health | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Version: {data[\"version\"]}, Features: {', '.join(data[\"features\"])}')
" 2>/dev/null || echo "Advanced API")
    echo "   📋 $API_INFO"
else
    echo "❌ Failed to start Advanced API"
    kill $ADVANCED_API_PID 2>/dev/null
    exit 1
fi

echo ""
echo "📊 Starting Advanced Dashboard..."

# Start Advanced Streamlit dashboard
echo "" | ./env/bin/python -m streamlit run dashboard/advanced_dashboard.py --server.port 8502 > /dev/null 2>&1 &
ADVANCED_DASHBOARD_PID=$!

# Wait for dashboard to start
echo "⏳ Waiting for Advanced Dashboard to initialize..."
sleep 10

# Test if dashboard is running
if curl -s http://localhost:8502 > /dev/null; then
    echo "✅ Advanced Dashboard is running successfully!"
else
    echo "❌ Failed to start Advanced Dashboard"
    kill $ADVANCED_API_PID 2>/dev/null
    kill $ADVANCED_DASHBOARD_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎉 Phase 3: Advanced Features - COMPLETE!"
echo "=========================================="
echo ""
echo "📋 Services Running:"
echo "   🚀 Advanced API:          http://localhost:5002"
echo "   📊 Advanced Dashboard:    http://localhost:8502"
echo "   🧪 Phase 3 Test Suite:   file://$PWD/phase3_test.html"
echo ""
echo "👥 User Accounts Available:"
echo "   👑 Admin:      admin / admin123 (Full system access)"
echo "   📚 Librarian:  librarian / librarian123 (Library operations)" 
echo "   👤 Member:     member / member123 (Personal features)"
echo ""
echo "🎯 Phase 3 Features:"
echo "   ✅ Multi-Role Authentication (Admin, Librarian, Member)"
echo "   ✅ Permission-Based Access Control"
echo "   ✅ User Registration System"
echo "   ✅ Advanced Analytics Dashboard"
echo "   ✅ User Activity Logging"
echo "   ✅ Role-Specific Interfaces"
echo "   ✅ User Management (Admin)"
echo "   ✅ System Monitoring"
echo ""
echo "📖 How to Use:"
echo "   1. Open Advanced Dashboard: http://localhost:8502"
echo "   2. Try different user roles with provided credentials"
echo "   3. Explore role-specific features and permissions"
echo "   4. Use Phase 3 Test Suite for API testing"
echo "   5. Admin can manage users and view system analytics"
echo ""
echo "🔄 Comparison with Previous Phases:"
echo "   Phase 1: Basic API + Simple Dashboard"
echo "   Phase 2: Enhanced API + Integrated Dashboard"  
echo "   Phase 3: Multi-Role System + Advanced Analytics ⭐"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Keep script running and wait for user to stop
wait
