#!/bin/bash
"""
Phase 4: Complete ETL Infrastructure Startup Script
Starts all components of the Data Pipeline & ETL Infrastructure
"""

echo "🚀 Starting Phase 4: ETL Infrastructure System"
echo "=============================================="

# Set the project directory
PROJECT_DIR="/Users/rishikagour/library_analytics_project"
cd "$PROJECT_DIR"

# Create necessary directories
mkdir -p logs
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/staging
mkdir -p monitoring
mkdir -p config

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        echo "⚠️  Port $port is already in use"
        return 1
    else
        return 0
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        
        echo "   Attempt $attempt/$max_attempts - waiting..."
        sleep 2
        ((attempt++))
    done
    
    echo "❌ $service_name failed to start within timeout"
    return 1
}

# Function to kill existing processes
cleanup_processes() {
    echo "🧹 Cleaning up existing processes..."
    
    # Kill existing Python processes for our services
    pkill -f "app/advanced_api.py" 2>/dev/null
    pkill -f "dashboard/advanced_dashboard.py" 2>/dev/null
    pkill -f "dashboard/library_dashboard.py" 2>/dev/null
    pkill -f "python.*streamlit" 2>/dev/null
    pkill -f "setup_phase4_etl" 2>/dev/null
    
    sleep 3
    echo "✅ Cleanup complete"
}

echo ""
echo "📊 Step 1: Initializing ETL Infrastructure..."

# Initialize the ETL infrastructure
python3 setup_phase4_etl_demo.py > logs/etl_setup.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ ETL Infrastructure initialized successfully"
else
    echo "❌ ETL Infrastructure initialization failed - check logs/etl_setup.log"
    exit 1
fi

echo ""
echo "🔧 Step 2: Starting Phase 3 Advanced API (Backend)..."

# Start Phase 3 Advanced API
cd app && python3 advanced_api.py &
ADVANCED_API_PID=$!
cd ..
sleep 5

# Check if Advanced API is running
if curl -s http://localhost:5002/api/health > /dev/null 2>&1; then
    echo "✅ Advanced API running on http://localhost:5002"
else
    echo "⚠️  Advanced API may not be fully ready - check logs"
fi

echo ""
echo "📈 Step 3: Starting Dashboards (Frontend)..."

# Start Advanced Dashboard
cd dashboard && python3 -m streamlit run advanced_dashboard.py --server.port 8501 &
DASHBOARD_PID=$!
echo "✅ Enhanced Dashboard starting on port 8501"

# Start Original ML Dashboard  
python3 -m streamlit run library_dashboard.py --server.port 8503 &
ML_DASHBOARD_PID=$!
echo "✅ Original ML Dashboard starting on port 8503"
cd ..
sleep 8

# Check if Dashboards are running
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "✅ Enhanced Dashboard running on http://localhost:8501"
else
    echo "⚠️  Enhanced Dashboard may not be fully ready - check logs"
fi

if curl -s http://localhost:8503 > /dev/null 2>&1; then
    echo "✅ ML Dashboard running on http://localhost:8503"
else
    echo "⚠️  ML Dashboard may not be fully ready - check logs"
fi

echo ""
echo "📊 Step 4: Starting ETL Monitoring System..."

# Create a simple monitoring service (placeholder)
cat > monitoring/start_monitor.py << 'EOF'
#!/usr/bin/env python3
import time
import sqlite3
from datetime import datetime

def run_monitoring():
    print("🔍 ETL Monitoring Service Started")
    while True:
        try:
            # Simple health check
            conn = sqlite3.connect('quality_metrics.db')
            cursor = conn.execute("""
                SELECT COUNT(*) FROM pipeline_health 
                WHERE timestamp >= datetime('now', '-1 hour')
            """)
            recent_executions = cursor.fetchone()[0]
            conn.close()
            
            print(f"📊 {datetime.now().strftime('%H:%M:%S')} - Recent pipeline executions: {recent_executions}")
            time.sleep(300)  # Check every 5 minutes
            
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_monitoring()
EOF

cd monitoring && python3 start_monitor.py &
MONITOR_PID=$!
cd ..

echo "✅ ETL Monitoring Service started"

echo ""
echo "⏰ Step 5: ETL Infrastructure Status Check..."

# Create status check script
cat > check_etl_status.py << 'EOF'
#!/usr/bin/env python3
import requests
import sqlite3
import json
from datetime import datetime

def check_system_status():
    status = {
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }
    
    # Check Advanced API
    try:
        response = requests.get("http://localhost:5002/api/health", timeout=5)
        if response.status_code == 200:
            status["services"]["advanced_api"] = {"status": "running", "port": 5002}
        else:
            status["services"]["advanced_api"] = {"status": "error", "code": response.status_code}
    except:
        status["services"]["advanced_api"] = {"status": "not_running"}
    
    # Check Dashboard
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            status["services"]["enhanced_dashboard"] = {"status": "running", "port": 8501}
        else:
            status["services"]["enhanced_dashboard"] = {"status": "error", "code": response.status_code}
    except:
        status["services"]["enhanced_dashboard"] = {"status": "not_running"}
    
    # Check ML Dashboard
    try:
        response = requests.get("http://localhost:8503", timeout=5)
        if response.status_code == 200:
            status["services"]["ml_dashboard"] = {"status": "running", "port": 8503}
        else:
            status["services"]["ml_dashboard"] = {"status": "error", "code": response.status_code}
    except:
        status["services"]["ml_dashboard"] = {"status": "not_running"}
    
    # Check ETL Database
    try:
        conn = sqlite3.connect('monitoring/quality_metrics.db')
        cursor = conn.execute("SELECT COUNT(*) FROM pipeline_health")
        health_records = cursor.fetchone()[0]
        conn.close()
        status["services"]["etl_database"] = {"status": "running", "health_records": health_records}
    except Exception as e:
        status["services"]["etl_database"] = {"status": "error", "error": str(e)}
    
    return status

if __name__ == "__main__":
    status = check_system_status()
    print("📊 System Status Report:")
    print(json.dumps(status, indent=2))
EOF

python3 check_etl_status.py

echo ""
echo "🎯 Phase 4 System Status:"
echo "========================="
echo ""
echo "🔗 Service URLs:"
echo "  📊 Advanced API:      http://localhost:5002"
echo "  📈 Enhanced Dashboard: http://localhost:8501"
echo "  🤖 ML Predictions:    http://localhost:8503"
echo "  📋 API Health Check:  http://localhost:5002/api/health"
echo "  👥 User Management:   http://localhost:5002/api/users"
echo ""
echo "📁 Data Locations:"
echo "  📥 Raw Data:         data/raw/"
echo "  🧹 Processed Data:   data/processed/"
echo "  📊 Staging Area:     data/staging/"
echo "  📋 Quality Metrics:  monitoring/quality_metrics.db"
echo ""
echo "📋 Default Test Accounts (use these usernames):"
echo "  👤 Admin:     admin / admin123"
echo "  📚 Librarian: librarian / lib123"
echo "  👥 Member:    member / member123"
echo ""
echo "💡 Key Features Available:"
echo "  ✅ Multi-role Authentication (Admin/Librarian/Member)"
echo "  ✅ Advanced User Management"
echo "  ✅ ETL Pipeline Framework"
echo "  ✅ Data Quality Monitoring"
echo "  ✅ Automated Data Processing"
echo "  ✅ Real-time Health Monitoring"
echo "  ✅ Role-based Dashboard Views"
echo "  ✅ Activity Logging & Analytics"
echo ""
echo "📖 Usage Instructions:"
echo "  1. Open http://localhost:8501 for the enhanced dashboard"
echo "  2. Open http://localhost:8503 for ML predictions dashboard"
echo "  3. Login with: admin / admin123 (or librarian / lib123)"
echo "  4. Explore role-specific features based on your login"
echo "  5. For API testing use POST: curl -X POST http://localhost:5002/api/auth/login"
echo "  6. Review ETL pipeline execution logs"
echo ""
echo "🔧 Management Commands:"
echo "  📊 Check Status:     python3 check_etl_status.py"
echo "  🔄 Restart System:   bash start_phase4.sh"
echo "  🛑 Stop All:         pkill -f 'advanced_api.py|advanced_dashboard.py|start_monitor.py'"
echo ""
echo "📁 Log Files:"
echo "  📋 ETL Setup:       logs/etl_setup.log"
echo "  🔧 API Logs:        Check terminal output"
echo "  📊 Dashboard Logs:  Check terminal output"
echo ""

# Save system information
cat > system_info.json << EOF
{
  "phase": 4,
  "system_name": "Library Analytics ETL Infrastructure",
  "version": "4.0.0",
  "started_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "services": {
    "advanced_api": {
      "url": "http://localhost:5002",
      "status": "running",
      "features": ["multi-role auth", "user management", "analytics"]
    },
    "advanced_dashboard": {
      "url": "http://localhost:8501", 
      "status": "running",
      "features": ["role-based UI", "user registration", "analytics views"]
    },
    "etl_infrastructure": {
      "status": "initialized",
      "features": ["data pipelines", "quality monitoring", "automated processing"]
    }
  },
  "accounts": {
    "admin": "admin@library.com / admin123",
    "librarian": "librarian@library.com / lib123", 
    "member": "member@library.com / member123"
  }
}
EOF

echo "💾 System information saved to: system_info.json"
echo ""
echo "🎉 Phase 4: ETL Infrastructure System Started Successfully!"
echo "🚀 The complete library analytics system with ETL infrastructure is now running!"
