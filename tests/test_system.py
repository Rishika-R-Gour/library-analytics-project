#!/usr/bin/env python3
"""
Quick System Test - Verify all Phase 4 components are working
"""

import requests
import json
import sys
from datetime import datetime

class SystemTester:
    def __init__(self):
        self.api_base = "http://localhost:5002"
        self.dashboard_url = "http://localhost:8502"
        self.test_results = []
        
    def test_api_health(self):
        """Test API health endpoint"""
        try:
            response = requests.get(f"{self.api_base}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.test_results.append({
                    "test": "API Health Check",
                    "status": "✅ PASS",
                    "details": f"Version: {data.get('version', 'unknown')}"
                })
                return True
            else:
                self.test_results.append({
                    "test": "API Health Check", 
                    "status": "❌ FAIL",
                    "details": f"HTTP {response.status_code}"
                })
                return False
        except Exception as e:
            self.test_results.append({
                "test": "API Health Check",
                "status": "❌ FAIL", 
                "details": str(e)
            })
            return False
    
    def test_authentication(self):
        """Test user authentication"""
        try:
            # Test admin login
            login_data = {"username": "admin", "password": "admin123"}
            response = requests.post(f"{self.api_base}/api/auth/login", json=login_data, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                user = data.get('user', {})
                
                self.test_results.append({
                    "test": "Authentication (Admin Login)",
                    "status": "✅ PASS",
                    "details": f"User: {user.get('username')} ({user.get('role')})"
                })
                return token
            else:
                self.test_results.append({
                    "test": "Authentication (Admin Login)",
                    "status": "❌ FAIL",
                    "details": f"HTTP {response.status_code}: {response.text}"
                })
                return None
        except Exception as e:
            self.test_results.append({
                "test": "Authentication (Admin Login)",
                "status": "❌ FAIL",
                "details": str(e)
            })
            return None
    
    def test_protected_endpoint(self, token):
        """Test protected endpoint with authentication"""
        if not token:
            self.test_results.append({
                "test": "Protected Endpoint (Users)",
                "status": "⏭️  SKIP",
                "details": "No authentication token"
            })
            return False
            
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{self.api_base}/api/users", headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                self.test_results.append({
                    "test": "Protected Endpoint (Users)",
                    "status": "✅ PASS",
                    "details": f"Retrieved {len(users)} users"
                })
                return True
            else:
                self.test_results.append({
                    "test": "Protected Endpoint (Users)",
                    "status": "❌ FAIL",
                    "details": f"HTTP {response.status_code}"
                })
                return False
        except Exception as e:
            self.test_results.append({
                "test": "Protected Endpoint (Users)",
                "status": "❌ FAIL",
                "details": str(e)
            })
            return False
    
    def test_dashboard(self):
        """Test dashboard accessibility"""
        try:
            response = requests.get(self.dashboard_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                if "streamlit" in content.lower() or "library" in content.lower():
                    self.test_results.append({
                        "test": "Dashboard Accessibility",
                        "status": "✅ PASS",
                        "details": "Dashboard is responding"
                    })
                    return True
                else:
                    self.test_results.append({
                        "test": "Dashboard Accessibility",
                        "status": "⚠️  WARN",
                        "details": "Unexpected content"
                    })
                    return False
            else:
                self.test_results.append({
                    "test": "Dashboard Accessibility",
                    "status": "❌ FAIL",
                    "details": f"HTTP {response.status_code}"
                })
                return False
        except Exception as e:
            self.test_results.append({
                "test": "Dashboard Accessibility",
                "status": "❌ FAIL",
                "details": str(e)
            })
            return False
    
    def test_etl_infrastructure(self):
        """Test ETL infrastructure components"""
        import os
        
        # Check for ETL files
        etl_components = [
            ("ETL Framework", "pipelines/etl_framework.py"),
            ("Data Extractors", "pipelines/extractors/data_extractors.py"),
            ("Data Transformers", "pipelines/transformers/data_transformers.py"),
            ("Data Loaders", "pipelines/loaders/data_loaders.py"),
            ("Quality Monitor", "monitoring/quality_monitor.py"),
            ("Pipeline Scheduler", "schedulers/pipeline_scheduler.py")
        ]
        
        etl_status = []
        for name, path in etl_components:
            if os.path.exists(path):
                etl_status.append(f"✅ {name}")
            else:
                etl_status.append(f"❌ {name}")
        
        self.test_results.append({
            "test": "ETL Infrastructure Files",
            "status": "✅ PASS" if all("✅" in s for s in etl_status) else "⚠️  PARTIAL",
            "details": ", ".join(etl_status)
        })
        
        # Check for monitoring database
        if os.path.exists("monitoring/quality_metrics.db"):
            self.test_results.append({
                "test": "ETL Monitoring Database",
                "status": "✅ PASS",
                "details": "Quality metrics database exists"
            })
        else:
            self.test_results.append({
                "test": "ETL Monitoring Database",
                "status": "❌ FAIL",
                "details": "Quality metrics database not found"
            })
    
    def run_all_tests(self):
        """Run all system tests"""
        print("🧪 Running Phase 4 System Tests")
        print("=" * 50)
        
        # Test API
        print("\n📡 Testing API Components...")
        api_healthy = self.test_api_health()
        
        if api_healthy:
            token = self.test_authentication()
            self.test_protected_endpoint(token)
        
        # Test Dashboard
        print("\n📊 Testing Dashboard...")
        self.test_dashboard()
        
        # Test ETL Infrastructure
        print("\n🔄 Testing ETL Infrastructure...")
        self.test_etl_infrastructure()
        
        # Print results
        print("\n" + "=" * 50)
        print("📋 Test Results Summary")
        print("=" * 50)
        
        passed = 0
        total = len(self.test_results)
        
        for result in self.test_results:
            print(f"{result['status']:<12} {result['test']}")
            if result['details']:
                print(f"              └─ {result['details']}")
            if "✅" in result['status']:
                passed += 1
        
        print("\n" + "=" * 50)
        print(f"📊 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All systems are working perfectly!")
            return True
        elif passed >= total * 0.8:
            print("⚠️  Most systems are working (minor issues)")
            return True
        else:
            print("❌ Multiple system failures detected")
            return False

def main():
    """Main test function"""
    print(f"🚀 Phase 4 System Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = SystemTester()
    success = tester.run_all_tests()
    
    print("\n" + "=" * 50)
    print("🔗 Quick Access Links:")
    print("  📊 API Health:     http://localhost:5002/api/health")
    print("  📈 Dashboard:      http://localhost:8502")
    print("  👥 API Users:      http://localhost:5002/api/users (requires auth)")
    print("\n🔐 Test Login Credentials:")
    print("  Admin:      admin / admin123")
    print("  Librarian:  librarian / lib123")
    print("  Member:     member / member123")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
