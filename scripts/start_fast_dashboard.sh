#!/bin/bash

# Fast Library Dashboard - No API Dependencies
# Instant login, no waiting times!

echo "🚀 Starting Fast Library Dashboard..."
echo "📍 URL: http://localhost:8501"
echo "⚡ Features: Instant login, offline authentication"
echo ""
echo "👤 Quick Login Credentials:"
echo "   Admin:     admin / admin123"
echo "   Librarian: librarian / lib123" 
echo "   Member:    member / member123"
echo ""

# Activate virtual environment
source env/bin/activate

# Start the fast dashboard
streamlit run dashboard/fast_dashboard.py --server.port 8501 --server.address localhost
