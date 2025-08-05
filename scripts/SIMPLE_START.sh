#!/bin/bash

# SIMPLIFIED STARTUP - Just the essential commands
echo "🚀 Ultra Fast Library Dashboard"
echo "==============================="

# Navigate to project
cd /Users/rishikagour/library_analytics_project

# Activate environment  
source env/bin/activate

# Start dashboard
streamlit run dashboard/ultra_fast_dashboard.py --server.port 8501
