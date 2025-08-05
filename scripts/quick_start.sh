#!/bin/bash

# Library Analytics Project - Simple Startup Script
echo "📚 Library Analytics Project - Quick Start"
echo "=========================================="

# Project root directory
PROJECT_ROOT="/Users/rishikagour/library_analytics_project"
cd "$PROJECT_ROOT"

# Function to check if services are running
check_services() {
    echo "🔍 Checking Service Status..."
    echo ""
    
    # Check API services
    if curl -s http://localhost:5002/api/health > /dev/null 2>&1; then
        echo "✅ Advanced API (Port 5002) - Running"
        API_RUNNING=true
    else
        echo "❌ Advanced API (Port 5002) - Not Running"
        API_RUNNING=false
    fi
    
    if curl -s http://localhost:5003/api/health > /dev/null 2>&1; then
        echo "✅ Library API (Port 5003) - Running"
        LIB_API_RUNNING=true
    else
        echo "❌ Library API (Port 5003) - Not Running"
        LIB_API_RUNNING=false
    fi
    
    # Check Streamlit services
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        echo "✅ Enhanced Dashboard (Port 8501) - Running"
        DASH_RUNNING=true
    else
        echo "❌ Enhanced Dashboard (Port 8501) - Not Running"
        DASH_RUNNING=false
    fi
    
    if curl -s http://localhost:8503 > /dev/null 2>&1; then
        echo "✅ ML Dashboard (Port 8503) - Running"
        ML_DASH_RUNNING=true
    else
        echo "❌ ML Dashboard (Port 8503) - Not Running"
        ML_DASH_RUNNING=false
    fi
    
    echo ""
}

# Check current status
check_services

# If everything is running, show access info
if [[ "$API_RUNNING" == true && "$DASH_RUNNING" == true && "$ML_DASH_RUNNING" == true ]]; then
    echo "🎉 All services are already running!"
    echo ""
    echo "🔗 Access Your System:"
    echo "   📊 Enhanced Dashboard: http://localhost:8501"
    echo "   🤖 ML Predictions:    http://localhost:8503"
    echo "   🔧 Advanced API:      http://localhost:5002"
    echo "   📚 Library API:       http://localhost:5003"
    echo ""
    echo "👥 Login with: admin/admin123 or librarian/lib123"
    exit 0
fi

# If not everything is running, start the fast startup
echo "🚀 Starting missing services..."
echo ""

# Use the fast startup script
chmod +x scripts/fast_start.sh
./scripts/fast_start.sh

echo ""
echo "✅ Startup complete!"
echo ""
echo "🔗 Access Your System:"
echo "   📊 Enhanced Dashboard: http://localhost:8501"
echo "   🤖 ML Predictions:    http://localhost:8503"
echo "   🔧 Advanced API:      http://localhost:5002"
echo "   📚 Library API:       http://localhost:5003"
echo ""
echo "👥 Login with: admin/admin123 or librarian/lib123"
