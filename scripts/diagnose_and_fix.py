#!/usr/bin/env python3
"""
Quick System Diagnostic Tool
Identifies and fixes common performance issues
"""

import subprocess
import time
import requests
import os
import sys

def check_port(port, service_name):
    """Check if a port is occupied and by what process"""
    try:
        result = subprocess.run(['lsof', '-i', f':{port}'], 
                              capture_output=True, text=True)
        if result.stdout:
            print(f"🔴 Port {port} ({service_name}) is OCCUPIED:")
            print(result.stdout)
            return True
        else:
            print(f"✅ Port {port} ({service_name}) is FREE")
            return False
    except Exception as e:
        print(f"❌ Error checking port {port}: {e}")
        return False

def kill_processes_on_ports():
    """Kill any existing processes on our target ports"""
    ports = [5002, 5003, 8501, 8503]
    for port in ports:
        try:
            subprocess.run(['lsof', '-ti', f':{port}'], 
                         capture_output=True, text=True, check=True)
            print(f"🔫 Killing processes on port {port}...")
            subprocess.run(['kill', '-9'] + subprocess.run(['lsof', '-ti', f':{port}'], 
                         capture_output=True, text=True).stdout.strip().split('\n'))
        except:
            pass

def check_python_environment():
    """Check if Python environment is properly configured"""
    venv_python = "/Users/rishikagour/library_analytics_project/env/bin/python"
    if not os.path.exists(venv_python):
        print("❌ Virtual environment Python not found!")
        return False
    
    try:
        result = subprocess.run([venv_python, '--version'], 
                              capture_output=True, text=True)
        print(f"✅ Python version: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Python environment error: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    venv_python = "/Users/rishikagour/library_analytics_project/env/bin/python"
    required_packages = ['flask', 'streamlit', 'pandas', 'sqlite3']
    
    for package in required_packages:
        try:
            result = subprocess.run([venv_python, '-c', f'import {package}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {package} is installed")
            else:
                print(f"❌ {package} is MISSING")
        except Exception as e:
            print(f"❌ Error checking {package}: {e}")

def optimize_startup():
    """Create optimized startup sequence"""
    print("\n🚀 Creating optimized startup sequence...")
    
    optimized_script = """#!/bin/bash

# Optimized Library Analytics Startup
# Fixes common performance issues

echo "🔧 Optimizing system for fast startup..."

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "streamlit" 2>/dev/null || true
pkill -f "advanced_api" 2>/dev/null || true
pkill -f "library_management_api" 2>/dev/null || true

# Wait for cleanup
sleep 2

# Navigate to project directory
cd /Users/rishikagour/library_analytics_project

# Activate environment
source env/bin/activate

echo "🚀 Starting services with optimized settings..."

# Start APIs with reduced verbosity
echo "🔧 Starting Advanced API (Port 5002)..."
nohup python app/advanced_api.py > logs/api_5002.log 2>&1 &
API1_PID=$!

echo "📚 Starting Library API (Port 5003)..."
nohup python app/library_management_api.py > logs/api_5003.log 2>&1 &
API2_PID=$!

# Wait for APIs to initialize
echo "⏳ Waiting for APIs..."
sleep 3

# Test API connectivity
echo "🔍 Testing API connectivity..."
if curl -s --max-time 5 http://localhost:5002/api/health > /dev/null; then
    echo "✅ Advanced API: READY"
else
    echo "⚠️ Advanced API: Still starting..."
fi

if curl -s --max-time 5 http://localhost:5003/api/health > /dev/null; then
    echo "✅ Library API: READY"
else
    echo "⚠️ Library API: Still starting..."
fi

# Start Streamlit with optimization flags
echo "📊 Starting Enhanced Dashboard (Port 8501)..."
nohup streamlit run dashboard/advanced_dashboard.py \\
    --server.port 8501 \\
    --server.address localhost \\
    --server.headless true \\
    --server.runOnSave false \\
    --browser.gatherUsageStats false > logs/dashboard_8501.log 2>&1 &
DASH1_PID=$!

echo "🤖 Starting ML Dashboard (Port 8503)..."
nohup streamlit run dashboard/library_dashboard.py \\
    --server.port 8503 \\
    --server.address localhost \\
    --server.headless true \\
    --server.runOnSave false \\
    --browser.gatherUsageStats false > logs/dashboard_8503.log 2>&1 &
DASH2_PID=$!

# Store PIDs for later cleanup
echo "$API1_PID $API2_PID $DASH1_PID $DASH2_PID" > .service_pids

echo ""
echo "✅ All services started in background!"
echo "🌐 Access URLs:"
echo "  • Enhanced Dashboard: http://localhost:8501"
echo "  • ML Dashboard: http://localhost:8503"
echo "  • Advanced API: http://localhost:5002"
echo "  • Library API: http://localhost:5003"
echo ""
echo "📋 Check logs in logs/ directory if needed"
echo "🛑 To stop: pkill -f 'streamlit|python.*api'"
"""
    
    with open('/Users/rishikagour/library_analytics_project/scripts/optimized_start.sh', 'w') as f:
        f.write(optimized_script)
    
    # Make executable
    subprocess.run(['chmod', '+x', '/Users/rishikagour/library_analytics_project/scripts/optimized_start.sh'])
    print("✅ Created optimized_start.sh")

def main():
    print("🔍 Library Analytics System Diagnostic")
    print("=" * 50)
    
    # Check current port usage
    print("\n1. Checking port availability...")
    occupied_ports = []
    if check_port(5002, "Advanced API"): occupied_ports.append(5002)
    if check_port(5003, "Library API"): occupied_ports.append(5003)
    if check_port(8501, "Enhanced Dashboard"): occupied_ports.append(8501)
    if check_port(8503, "ML Dashboard"): occupied_ports.append(8503)
    
    if occupied_ports:
        print(f"\n⚠️ ISSUE FOUND: Ports {occupied_ports} are occupied!")
        response = input("Kill existing processes? (y/n): ")
        if response.lower() == 'y':
            kill_processes_on_ports()
            print("✅ Processes killed")
    
    # Check Python environment
    print("\n2. Checking Python environment...")
    if not check_python_environment():
        print("❌ Python environment issues detected!")
        return
    
    # Check dependencies
    print("\n3. Checking dependencies...")
    check_dependencies()
    
    # Create logs directory
    logs_dir = "/Users/rishikagour/library_analytics_project/logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"✅ Created logs directory: {logs_dir}")
    
    # Create optimized startup
    optimize_startup()
    
    print("\n🎯 RECOMMENDATIONS:")
    print("1. Use the optimized startup script: ./scripts/optimized_start.sh")
    print("2. Check logs in logs/ directory if services fail")
    print("3. Ensure no other applications are using ports 5002, 5003, 8501, 8503")
    print("4. Try restarting your computer if issues persist")

if __name__ == "__main__":
    main()
