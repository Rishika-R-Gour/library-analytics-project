#!/bin/bash

# Start All Library Analytics Services
# Including APIs for full functionality

echo "🚀 Starting Complete Library Analytics System..."
echo "==============================================="

# Activate virtual environment
source env/bin/activate

# Start APIs first
echo "🔧 Starting Advanced API (Port 5002)..."
python app/advanced_api.py &
API1_PID=$!

echo "📚 Starting Library API (Port 5003)..."
python app/library_management_api.py &
API2_PID=$!

# Wait for APIs to initialize
echo "⏳ Waiting for APIs to initialize..."
sleep 3

# Start Streamlit dashboards
echo "📊 Starting Enhanced Dashboard (Port 8501)..."
streamlit run dashboard/advanced_dashboard.py --server.port 8501 --server.address localhost &
DASH1_PID=$!

echo "🤖 Starting ML Predictions Dashboard (Port 8503)..."
streamlit run dashboard/library_dashboard.py --server.port 8503 --server.address localhost &
DASH2_PID=$!

# Wait for services to start
echo "⏳ Initializing services..."
sleep 5

echo ""
echo "✅ All Services Started Successfully!"
echo "==============================================="
echo "🔧 Advanced API:        http://localhost:5002"
echo "📚 Library API:         http://localhost:5003"  
echo "📊 Enhanced Dashboard:  http://localhost:8501"
echo "🤖 ML Predictions:      http://localhost:8503"
echo ""
echo "👤 Login Credentials:"
echo "   Admin:     admin / admin123"
echo "   Librarian: librarian / lib123"
echo "   Member:    member / member123"
echo ""
echo "🛑 To stop all services: pkill -f 'streamlit|python.*api'"

# Store PIDs for cleanup
echo "$API1_PID $API2_PID $DASH1_PID $DASH2_PID" > .service_pids
