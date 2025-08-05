#!/usr/bin/env python3
"""
Library Analytics API Client
Test client for interacting with the Flask API
"""

import requests
import json
from datetime import datetime

class LibraryAPIClient:
    """Client for Library Analytics API"""
    
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.token = None
        
    def login(self, username="admin", password="admin123"):
        """Authenticate with the API"""
        response = requests.post(f"{self.base_url}/api/auth/login", 
                               json={"username": username, "password": password})
        
        if response.status_code == 200:
            data = response.json()
            self.token = data['token']
            print(f"✅ Login successful. Token expires in {data['expires_in']} seconds")
            return True
        else:
            print(f"❌ Login failed: {response.json().get('error', 'Unknown error')}")
            return False
    
    def _make_request(self, endpoint, method="GET", data=None):
        """Make authenticated API request"""
        if not self.token:
            print("❌ Not authenticated. Please login first.")
            return None
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            if method == "GET":
                response = requests.get(f"{self.base_url}/api{endpoint}", headers=headers)
            elif method == "POST":
                response = requests.post(f"{self.base_url}/api{endpoint}", headers=headers, json=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API Error: {response.status_code} - {response.json().get('error', 'Unknown error')}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API server. Is it running?")
            return None
        except Exception as e:
            print(f"❌ Request error: {e}")
            return None
    
    def health_check(self):
        """Check API health"""
        try:
            response = requests.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API is healthy (v{data.get('version', '1.0.0')})")
                return True
            else:
                print("❌ API health check failed")
                return False
        except:
            print("❌ Cannot connect to API")
            return False
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        return self._make_request("/dashboard/stats")
    
    def predict_overdue(self, loan_data):
        """Predict overdue probability"""
        return self._make_request("/predictions/overdue", "POST", loan_data)
    
    def predict_churn(self, member_data):
        """Predict member churn"""
        return self._make_request("/predictions/churn", "POST", member_data)
    
    def get_recommendations(self, member_id, limit=5):
        """Get book recommendations"""
        return self._make_request(f"/recommendations/{member_id}?limit={limit}")
    
    def get_members(self, page=1, per_page=20, search=""):
        """Get members list"""
        endpoint = f"/members?page={page}&per_page={per_page}"
        if search:
            endpoint += f"&search={search}"
        return self._make_request(endpoint)
    
    def get_models_status(self):
        """Get ML models status"""
        return self._make_request("/models/status")

def demo():
    """Demonstrate API functionality"""
    print("🚀 Library Analytics API Demo")
    print("=" * 40)
    
    # Initialize client
    client = LibraryAPIClient()
    
    # Health check
    print("\n1. 🏥 Health Check")
    if not client.health_check():
        print("API server is not running. Please start it first.")
        return
    
    # Login
    print("\n2. 🔐 Authentication")
    if not client.login():
        return
    
    # Dashboard stats
    print("\n3. 📊 Dashboard Statistics")
    stats = client.get_dashboard_stats()
    if stats:
        print(f"   • Total Members: {stats['total_members']:,}")
        print(f"   • Active Loans: {stats['active_loans']:,}")
        print(f"   • Overdue Loans: {stats['overdue_loans']:,}")
        print(f"   • Total Books: {stats['total_books']:,}")
    
    # Overdue predictions
    print("\n4. 🔮 Overdue Predictions")
    sample_loans = [
        {'loan_id': 1, 'member_type': 'Student', 'days_borrowed': 15},
        {'loan_id': 2, 'member_type': 'Professional', 'days_borrowed': 7}
    ]
    
    predictions = client.predict_overdue(sample_loans)
    if predictions:
        for pred in predictions['predictions']:
            risk_emoji = "🔴" if pred['risk_level'] == 'High' else "🟡" if pred['risk_level'] == 'Medium' else "🟢"
            print(f"   {risk_emoji} Loan {pred['loan_id']}: {pred['overdue_probability']:.1%} ({pred['risk_level']} risk)")
    
    # Churn predictions
    print("\n5. 👥 Churn Predictions")
    sample_members = [
        {'member_id': 1, 'days_since_last_visit': 30, 'total_loans': 5},
        {'member_id': 2, 'days_since_last_visit': 90, 'total_loans': 1}
    ]
    
    churn_preds = client.predict_churn(sample_members)
    if churn_preds:
        for pred in churn_preds['predictions']:
            risk_emoji = "🔴" if pred['risk_level'] == 'High' else "🟡" if pred['risk_level'] == 'Medium' else "🟢"
            print(f"   {risk_emoji} Member {pred['member_id']}: {pred['churn_probability']:.1%} churn risk")
    
    # Recommendations
    print("\n6. 📚 Book Recommendations")
    recommendations = client.get_recommendations(1, limit=3)
    if recommendations:
        print(f"   📖 Top recommendations for Member 1:")
        for i, rec in enumerate(recommendations['recommendations'], 1):
            print(f"   {i}. {rec['title']} by {rec['author']} ({rec['recommendation_score']:.1%})")
    
    # Models status
    print("\n7. 🤖 Models Status")
    models = client.get_models_status()
    if models:
        print(f"   • Models Loaded: {models['loaded_models']}/{models['total_models']}")
        for model in models['models']:
            status_emoji = "✅" if model['status'] == 'loaded' else "❌"
            print(f"   {status_emoji} {model['name']} v{model['version']} ({model['size_mb']} MB)")
    
    print("\n🎉 Demo completed successfully!")

if __name__ == "__main__":
    demo()
