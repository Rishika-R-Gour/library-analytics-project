#!/bin/bash

# Ultra Fast Dashboard Startup
# No dependencies, instant loading

echo "⚡ Starting Ultra Fast Library Dashboard..."
echo "=========================================="
echo ""
echo "🎯 Features:"
echo "  ✅ No API dependencies"
echo "  ✅ Instant login (< 2 seconds)"
echo "  ✅ Sample data pre-loaded"
echo "  ✅ All core functionality"
echo ""

# Navigate to project
cd /Users/rishikagour/library_analytics_project

# Activate environment
source env/bin/activate

# Start ultra fast dashboard
echo "🚀 Launching dashboard on http://localhost:8501..."
streamlit run dashboard/ultra_fast_dashboard.py \
    --server.port 8501 \
    --server.address localhost \
    --server.headless true \
    --browser.gatherUsageStats false

echo ""
echo "⚡ Ultra Fast Dashboard should load instantly!"
