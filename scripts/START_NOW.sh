#!/bin/bash

# ONE-COMMAND SOLUTION - Ultra Fast Library Dashboard
# This script handles everything automatically

echo "⚡ Starting Ultra Fast Library Dashboard..."
echo "=========================================="

# Navigate to project directory
cd /Users/rishikagour/library_analytics_project || {
    echo "❌ Could not find project directory"
    exit 1
}

# Check if virtual environment exists
if [ ! -f "env/bin/activate" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv env && source env/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source env/bin/activate

# Kill any existing streamlit processes to avoid conflicts
echo "🧹 Cleaning up any existing processes..."
pkill -f "streamlit" 2>/dev/null || true
sleep 2

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if ultra fast dashboard exists
if [ ! -f "dashboard/ultra_fast_dashboard.py" ]; then
    echo "❌ Ultra fast dashboard not found!"
    exit 1
fi

echo "🚀 Launching Ultra Fast Dashboard..."
echo "📍 URL: http://localhost:8501"
echo "⚡ Loading time: < 2 seconds"
echo "👤 Login: Select any role or use Demo Mode"
echo ""

# Start the dashboard with all optimizations
exec streamlit run dashboard/ultra_fast_dashboard.py \
    --server.port 8501 \
    --server.address localhost \
    --server.headless true \
    --server.runOnSave false \
    --browser.gatherUsageStats false \
    --theme.primaryColor "#1f77b4" \
    --theme.backgroundColor "#ffffff"
