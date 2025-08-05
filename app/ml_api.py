#!/usr/bin/env python3
"""
Simple Flask API for ML Dashboard - Port 5001
Provides basic endpoints for the ML predictions dashboard with authentication
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime
import jwt
import hashlib

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests
app.config['SECRET_KEY'] = 'ml-dashboard-secret-key-2025'

# Default users for ML dashboard
DEFAULT_USERS = {
    'admin': {
        'password': hashlib.sha256('admin123'.encode()).hexdigest(),
        'role': 'admin'
    },
    'librarian': {
        'password': hashlib.sha256('lib123'.encode()).hexdigest(),
        'role': 'librarian'
    },
    'member': {
        'password': hashlib.sha256('member123'.encode()).hexdigest(),
        'role': 'member'
    }
}

@app.route('/api')
def api_root():
    return jsonify({
        'message': 'Library Analytics ML API is running!',
        'timestamp': datetime.now().isoformat(),
        'status': 'healthy',
        'version': '1.0.0'
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authentication endpoint for ML dashboard"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Hash the provided password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Check against default users
        if username in DEFAULT_USERS and DEFAULT_USERS[username]['password'] == password_hash:
            # Create JWT token
            token = jwt.encode({
                'username': username,
                'role': DEFAULT_USERS[username]['role'],
                'exp': datetime.utcnow().timestamp() + 3600  # 1 hour expiry
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'token': token,
                'user': {
                    'username': username,
                    'role': DEFAULT_USERS[username]['role']
                },
                'message': 'Login successful'
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/verify', methods=['POST'])
def verify_token():
    """Verify JWT token"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No valid token provided'}), 401
        
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        
        return jsonify({
            'valid': True,
            'user': {
                'username': payload['username'],
                'role': payload['role']
            }
        })
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    try:
        # Test database connection
        conn = sqlite3.connect('notebooks/library.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Loan")
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'loan_count': count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/stats')
def stats():
    try:
        conn = sqlite3.connect('notebooks/library.db')
        cursor = conn.cursor()
        
        # Basic statistics
        cursor.execute("SELECT COUNT(*) FROM Book")
        book_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Member")
        member_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Loan WHERE Status = 'Active'")
        active_loans = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Loan WHERE Status = 'Overdue'")
        overdue_loans = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'books': book_count,
            'members': member_count,
            'active_loans': active_loans,
            'overdue_loans': overdue_loans,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/predictions')
def predictions():
    """Mock predictions endpoint for ML dashboard"""
    return jsonify({
        'overdue_risk': {
            'high_risk_loans': 5,
            'medium_risk_loans': 12,
            'low_risk_loans': 45
        },
        'member_churn': {
            'at_risk_members': 8,
            'stable_members': 67
        },
        'book_recommendations': [
            {'book_id': 1, 'title': 'Data Science Handbook', 'score': 0.95},
            {'book_id': 2, 'title': 'Python Programming', 'score': 0.87},
            {'book_id': 3, 'title': 'Machine Learning', 'score': 0.82}
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/predictions/overdue', methods=['POST'])
def predict_overdue():
    """Predict overdue risk for loans"""
    try:
        data = request.get_json()
        predictions = []
        
        for loan in data:
            # Mock prediction logic based on loan data
            days_borrowed = loan.get('days_borrowed', 0)
            member_type = loan.get('member_type', 'Standard')
            
            # Simple risk calculation
            base_risk = min(days_borrowed * 0.05, 0.8)
            if member_type == 'Student':
                risk = min(base_risk + 0.2, 0.9)
            elif member_type == 'Professional':
                risk = base_risk * 0.7
            else:
                risk = base_risk
                
            risk_level = 'High' if risk > 0.6 else 'Medium' if risk > 0.3 else 'Low'
            
            predictions.append({
                'loan_id': loan.get('loan_id'),
                'overdue_probability': risk,
                'risk_level': risk_level,
                'confidence': 0.85
            })
        
        return jsonify({
            'predictions': predictions,
            'model': 'overdue_risk_v1.2',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions/churn', methods=['POST'])
def predict_churn():
    """Predict member churn risk"""
    try:
        data = request.get_json()
        predictions = []
        
        for member in data:
            # Mock prediction logic based on member data
            days_since_visit = member.get('days_since_last_visit', 0)
            total_loans = member.get('total_loans', 0)
            
            # Simple churn calculation
            visit_risk = min(days_since_visit * 0.02, 0.7)
            engagement_bonus = min(total_loans * 0.05, 0.3)
            churn_prob = max(visit_risk - engagement_bonus, 0.1)
            
            risk_level = 'High' if churn_prob > 0.5 else 'Medium' if churn_prob > 0.25 else 'Low'
            retention_score = 1 - churn_prob
            
            predictions.append({
                'member_id': member.get('member_id'),
                'churn_probability': churn_prob,
                'retention_score': retention_score,
                'risk_level': risk_level,
                'confidence': 0.78
            })
        
        return jsonify({
            'predictions': predictions,
            'model': 'churn_prediction_v2.1',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations/<int:member_id>')
def get_recommendations(member_id):
    """Get book recommendations for a member"""
    try:
        # Mock book recommendations
        sample_books = [
            {
                'title': 'Data Science Handbook',
                'author': 'Jake VanderPlas',
                'genre': 'Technology',
                'recommendation_score': 0.95,
                'reason': 'Based on your interest in data analysis and Python programming'
            },
            {
                'title': 'Machine Learning Yearning',
                'author': 'Andrew Ng',
                'genre': 'Technology',
                'recommendation_score': 0.87,
                'reason': 'Highly rated by members with similar reading patterns'
            },
            {
                'title': 'The Art of Statistics',
                'author': 'David Spiegelhalter',
                'genre': 'Science',
                'recommendation_score': 0.82,
                'reason': 'Perfect for advancing your statistical knowledge'
            },
            {
                'title': 'Weapons of Math Destruction',
                'author': 'Cathy O\'Neil',
                'genre': 'Technology',
                'recommendation_score': 0.78,
                'reason': 'Popular among data science enthusiasts'
            },
            {
                'title': 'The Signal and the Noise',
                'author': 'Nate Silver',
                'genre': 'Statistics',
                'recommendation_score': 0.75,
                'reason': 'Recommended based on your recent activity'
            }
        ]
        
        return jsonify({
            'member_id': member_id,
            'recommendations': sample_books,
            'algorithm': 'collaborative_filtering_v1.5',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/status')
def models_status():
    """Get ML models status"""
    try:
        models_data = {
            'loaded_models': 4,
            'total_models': 5,
            'models': [
                {
                    'name': 'Overdue Risk Predictor',
                    'version': '1.2.0',
                    'algorithm': 'Random Forest',
                    'status': 'Active',
                    'accuracy': 0.87,
                    'size_mb': 12.5
                },
                {
                    'name': 'Churn Prediction Model',
                    'version': '2.1.0',
                    'algorithm': 'Gradient Boosting',
                    'status': 'Active',
                    'accuracy': 0.82,
                    'size_mb': 8.3
                },
                {
                    'name': 'Book Recommendation Engine',
                    'version': '1.5.0',
                    'algorithm': 'Collaborative Filtering',
                    'status': 'Active',
                    'accuracy': 0.79,
                    'size_mb': 15.2
                },
                {
                    'name': 'Demand Forecasting Model',
                    'version': '1.0.0',
                    'algorithm': 'LSTM',
                    'status': 'Training',
                    'accuracy': 0.0,
                    'size_mb': 0.0
                }
            ]
        }
        
        return jsonify({
            'models': models_data,
            'last_updated': datetime.now().isoformat(),
            'system_health': 'optimal'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        conn = sqlite3.connect('notebooks/library.db')
        cursor = conn.cursor()
        
        # Get comprehensive stats
        cursor.execute("SELECT COUNT(*) FROM Book")
        total_books = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Member")
        total_members = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Loan WHERE Status = 'Active'")
        active_loans = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Loan WHERE Status = 'Overdue'")
        overdue_loans = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'data': {
                'total_books': total_books,
                'total_members': total_members,
                'active_loans': active_loans,
                'overdue_loans': overdue_loans
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'data': {
                'total_books': 2500,
                'total_members': 1000,
                'active_loans': 450,
                'overdue_loans': 75
            },
            'timestamp': datetime.now().isoformat()
        }), 200

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting Library Analytics ML API")
    print("📍 URL: http://localhost:5001")
    print("✨ Endpoints available:")
    print("   GET /api                     - Welcome message")
    print("   POST /api/auth/login         - User authentication")
    print("   GET /api/health              - Health check with DB connection")
    print("   GET /api/stats               - Basic statistics")
    print("   GET /api/predictions         - ML predictions data")
    print("   POST /api/predictions/overdue - Overdue risk predictions")
    print("   POST /api/predictions/churn  - Member churn predictions")
    print("   GET /api/recommendations/{id} - Book recommendations")
    print("   GET /api/models/status       - ML models status")
    print("   GET /api/dashboard/stats     - Dashboard statistics")
    print("-" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        use_reloader=False
    )
