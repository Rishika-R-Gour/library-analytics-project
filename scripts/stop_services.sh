#!/bin/bash

# Stop all Library Analytics services
echo "🛑 Stopping all services..."

if [ -f .pids ]; then
    PIDS=$(cat .pids)
    for pid in $PIDS; do
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            echo "Stopped process $pid"
        fi
    done
    rm .pids
fi

# Kill any remaining processes
pkill -f "streamlit run"
pkill -f "python app/"
pkill -f "ml_api.py"
pkill -f "enhanced_api.py"

echo "✅ All services stopped"
