#!/usr/bin/env python3
"""
Library Analytics - Phase 2 Status Check
Quick script to verify all services are running correctly
"""

import requests
import sys
from datetime import datetime

def check_service(name, url, expected_status=200):
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_status:
            print(f"✅ {name}: Running")
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Not running")
        return False
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False

def main():
    print("🔍 Library Analytics - Service Status Check")
    print("=" * 50)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    all_good = True
    
    # Check Complex API
    all_good &= check_service("Complex API", "http://localhost:5001/api/health")
    
    # Check Streamlit Dashboard
    all_good &= check_service("Streamlit Dashboard", "http://localhost:8501")
    
    print()
    
    if all_good:
        print("🎉 All services are running correctly!")
        print()
        print("📋 Access Points:")
        print("   🌐 Complex API:      http://localhost:5001")
        print("   📊 Dashboard:        http://localhost:8501")
        print("   🧪 API Test Page:    file://$(pwd)/complex_api_test.html")
        print()
        print("🔐 Demo Credentials: admin / admin123")
        return 0
    else:
        print("⚠️  Some services are not running!")
        print("💡 Run './start_phase2.sh' to start all services")
        return 1

if __name__ == "__main__":
    sys.exit(main())
