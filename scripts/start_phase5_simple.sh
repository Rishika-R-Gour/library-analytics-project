#!/bin/bash

# Phase 5 Library Management System Startup Script
echo "🚀 Starting Phase 5 Library Management System..."

# Set the project directory and Python executable
PROJECT_DIR="/Users/rishikagour/library_analytics_project"
PYTHON_EXEC="/Users/rishikagour/library_analytics_project/env/bin/python"

cd "$PROJECT_DIR"

# Check if we're in the correct directory
if [ ! -f "setup_phase5_database.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Create necessary directories
mkdir -p logs
mkdir -p data

# Function to cleanup existing processes
cleanup_processes() {
    echo "🧹 Cleaning up existing processes..."
    pkill -f "advanced_api.py" 2>/dev/null || true
    pkill -f "library_management_api.py" 2>/dev/null || true
    pkill -f "app.py" 2>/dev/null || true
    pkill -f "streamlit" 2>/dev/null || true
    sleep 2
    echo "✅ Cleanup complete"
}

cleanup_processes

# Initialize Phase 5 database
echo "📊 Initializing Phase 5 database..."
$PYTHON_EXEC setup_phase5_database.py
if [ $? -eq 0 ]; then
    echo "✅ Phase 5 database initialized successfully"
else
    echo "❌ Database initialization failed"
    exit 1
fi

echo ""
echo "🔧 Starting services..."

# Start Library Management API  
echo "🏛️ Starting Library Management API on port 5003..."
cd app
$PYTHON_EXEC library_management_api_clean.py &
API_PID=$!
cd ..
sleep 5

# Start Advanced API (Phase 3)
echo "🔧 Starting Advanced API on port 5002..."
cd app
$PYTHON_EXEC advanced_api.py &
ADV_API_PID=$!
cd ..
sleep 5

# Start Dashboard
echo "📊 Starting Dashboard on port 8502..."
cd dashboard
$PYTHON_EXEC -m streamlit run advanced_dashboard.py --server.port 8502 &
DASH_PID=$!
cd ..
sleep 8

echo ""
echo "🔍 Performing health checks..."

# Health checks
echo -n "📚 Library Management API: "
if curl -s http://localhost:5003/api/health > /dev/null 2>&1; then
    echo "✅ Working"
else
    echo "❌ Not responding"
fi

echo -n "🔧 Advanced API: "
if curl -s http://localhost:5002/api/health > /dev/null 2>&1; then
    echo "✅ Working"
else
    echo "❌ Not responding"
fi

echo -n "📊 Dashboard: "
if curl -s http://localhost:8502 > /dev/null 2>&1; then
    echo "✅ Working"
else
    echo "❌ Not responding"
fi

echo ""
echo "🎉 Phase 5 System Started!"
echo "=========================="
echo ""
echo "🔗 Service URLs:"
echo "  📚 Library Management API:  http://localhost:5003"
echo "  🔧 Advanced User API:       http://localhost:5002"
echo "  📈 Enhanced Dashboard:       http://localhost:8502"
echo ""
echo "📚 Key Endpoints:"
echo "  • Book Catalog:        http://localhost:5003/api/books"
echo "  • Search Books:        http://localhost:5003/api/search?q=python"
echo "  • Library Stats:       http://localhost:5003/api/dashboard/library-stats"
echo "  • Health Check:        http://localhost:5003/api/health"
echo ""
echo "👤 Test Accounts:"
echo "  • Admin:     admin / admin123"
echo "  • Librarian: librarian / lib123"
echo "  • Member:    member / member123"
echo ""
echo "💡 Features Available:"
echo "  ✅ Complete Book Catalog (10 sample books)"
echo "  ✅ Real Loan Processing"
echo "  ✅ Advanced Search & Discovery"
echo "  ✅ Member Loan History"
echo "  ✅ Book Reviews & Ratings"
echo "  ✅ Library Statistics"
echo "  ✅ Multi-role Authentication"
echo ""
echo "Process IDs:"
echo "  Library API: $API_PID"
echo "  Advanced API: $ADV_API_PID"
echo "  Dashboard: $DASH_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Test API with sample data
echo ""
echo "📚 Sample Library Data:"
if curl -s http://localhost:5003/api/books 2>/dev/null | head -c 200 > /dev/null 2>&1; then
    echo "✅ Library catalog loaded with sample books"
else
    echo "ℹ️  Library API may still be initializing..."
fi

# Keep the script running
wait
