#!/bin/bash

# Comprehensive System Status and Startup
echo "🚀 Library Analytics System - Complete Setup"
echo "============================================"

# Check current directory
echo "📁 Current Directory: $(pwd)"

# Check if we're in the right place
if [ ! -d "/Users/rishikagour/library_analytics_project" ]; then
    echo "❌ Project directory not found!"
    exit 1
fi

cd /Users/rishikagour/library_analytics_project

# Check virtual environment
if [ -f "env/bin/activate" ]; then
    echo "✅ Virtual environment found"
    source env/bin/activate
    echo "🐍 Python: $(which python)"
else
    echo "❌ Virtual environment not found!"
    exit 1
fi

# Check for required files
echo ""
echo "📋 Checking required files..."
files=(
    "dashboard/ultra_fast_dashboard.py"
    "dashboard/advanced_dashboard.py"
    "app/advanced_api.py"
    "app/library_management_api.py"
    "scripts/ultra_fast_start.sh"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - MISSING"
    fi
done

# Check port availability
echo ""
echo "🔍 Checking port availability..."
ports=(5002 5003 8501 8503)
for port in "${ports[@]}"; do
    if lsof -i ":$port" >/dev/null 2>&1; then
        echo "🔴 Port $port: OCCUPIED"
    else
        echo "✅ Port $port: FREE"
    fi
done

# Create logs directory
mkdir -p logs

echo ""
echo "🎯 READY TO START!"
echo "==================="
echo ""
echo "🚀 Quick Start Options:"
echo ""
echo "1. ⚡ ULTRA FAST (Recommended):"
echo "   ./scripts/ultra_fast_start.sh"
echo ""
echo "2. 🔧 MANUAL START (if script fails):"
echo "   streamlit run dashboard/ultra_fast_dashboard.py --server.port 8501"
echo ""
echo "3. 🌟 FULL SYSTEM:"
echo "   ./scripts/start_all_services.sh"
echo ""
echo "👤 Default Login: Any role (Admin/Librarian/Member) or Demo Mode"
echo "🌐 URL: http://localhost:8501"
