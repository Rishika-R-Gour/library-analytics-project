#!/bin/bash

# Simple API Starter
echo "🚀 Starting APIs manually..."

cd /Users/rishikagour/library_analytics_project

# Kill existing
pkill -f "advanced_api\|simple_library_api" 2>/dev/null

# Create logs directory
mkdir -p logs

echo "Starting Advanced API..."
cd app
nohup ../env/bin/python advanced_api.py > ../logs/api1.log 2>&1 &
echo "Started Advanced API"

echo "Starting Library API..."
nohup ../env/bin/python simple_library_api.py > ../logs/api2.log 2>&1 &
echo "Started Library API"

cd ..
sleep 3

echo "Testing connections..."
curl -s http://localhost:5002/api/health && echo " - Port 5002 OK" || echo " - Port 5002 FAIL"
curl -s http://localhost:5003/api/health && echo " - Port 5003 OK" || echo " - Port 5003 FAIL"

echo "Check logs with: tail -f logs/api1.log logs/api2.log"
