#!/bin/bash

# Library Analytics Project - Master Startup Script
echo "📚 Library Analytics Project - Master Control"
echo "=============================================="

# Project root directory
PROJECT_ROOT="/Users/rishikagour/library_analytics_project"
cd "$PROJECT_ROOT"

# Function to show menu
show_menu() {
    echo ""
    echo "🚀 Available Startup Options:"
    echo ""
    echo "1) 🏃‍♂️ Fast Start (Recommended)     - Quick startup, all services"
    echo "2) 🔧 Full ETL Infrastructure      - Complete Phase 4 system"
    echo "3) 📚 Phase 5 Library Management   - Library-focused features"
    echo "4) 📊 Check System Status          - View current service status"
    echo "5) 🛑 Stop All Services            - Shutdown all running services"
    echo "6) 📋 Show Project Structure       - Display file organization"
    echo "7) ❌ Exit"
    echo ""
    echo -n "Select option (1-7): "
}

# Function to check if services are running
check_services() {
    echo "🔍 Checking Service Status..."
    echo ""
    
    # Check API services
    if curl -s http://localhost:5002/api/health > /dev/null 2>&1; then
        echo "✅ Advanced API (Port 5002) - Running"
    else
        echo "❌ Advanced API (Port 5002) - Not Running"
    fi
    
    if curl -s http://localhost:5003/api/health > /dev/null 2>&1; then
        echo "✅ Library API (Port 5003) - Running"
    else
        echo "❌ Library API (Port 5003) - Not Running"
    fi
    
    # Check Streamlit services
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        echo "✅ Enhanced Dashboard (Port 8501) - Running"
    else
        echo "❌ Enhanced Dashboard (Port 8501) - Not Running"
    fi
    
    if curl -s http://localhost:8503 > /dev/null 2>&1; then
        echo "✅ ML Dashboard (Port 8503) - Running"
    else
        echo "❌ ML Dashboard (Port 8503) - Not Running"
    fi
    
    echo ""
    echo "🔗 Service URLs (if running):"
    echo "   📊 Enhanced Dashboard: http://localhost:8501"
    echo "   🤖 ML Predictions:    http://localhost:8503"
    echo "   🔧 Advanced API:      http://localhost:5002"
    echo "   📚 Library API:       http://localhost:5003"
}

# Function to stop all services
stop_services() {
    echo "🛑 Stopping all services..."
    pkill -f "streamlit|advanced_api|simple_library_api" 2>/dev/null || true
    sleep 2
    echo "✅ All services stopped"
}

# Main menu loop
while true; do
    show_menu
    read choice
    
    case $choice in
        1)
            echo "🏃‍♂️ Starting Fast Startup..."
            chmod +x scripts/fast_start.sh
            ./scripts/fast_start.sh
            ;;
        2)
            echo "🔧 Starting Full ETL Infrastructure..."
            chmod +x scripts/start_phase4.sh
            ./scripts/start_phase4.sh
            ;;
        3)
            echo "📚 Starting Phase 5 Library Management..."
            chmod +x scripts/start_phase5.sh
            ./scripts/start_phase5.sh
            ;;
        4)
            check_services
            ;;
        5)
            stop_services
            ;;
        6)
            echo "📋 Project Structure:"
            cat PROJECT_STRUCTURE.md
            ;;
        7)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please select 1-7."
            ;;
    esac
    
    echo ""
    echo "Press Enter to continue..."
    read
done
