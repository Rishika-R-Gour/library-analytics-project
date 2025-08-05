#!/usr/bin/env python3
"""
Library Analytics API Server
Production-ready Flask application for library analytics system
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
import os
import sys
import logging
from datetime import datetime, timedelta
import jwt
from functools import wraps
import hashlib
import secrets

# Add models directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models.model_manager import ModelManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LibraryAnalyticsAPI:
    """Main Flask application for Library Analytics API"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_config()
        self.setup_extensions()
        self.setup_routes()
        self.model_manager = ModelManager()
        
    def setup_config(self):
        """Configure Flask application settings"""
        self.app.config.update(
            SECRET_KEY=os.environ.get('SECRET_KEY', secrets.token_hex(32)),
            DATABASE_PATH=os.path.join(os.path.dirname(__file__), '..', 'notebooks', 'library.db'),
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32)),
            JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=24),
            RATELIMIT_STORAGE_URL='memory://',
            DEBUG=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        )
        
    def setup_extensions(self):
        """Initialize Flask extensions"""
        # CORS for cross-origin requests
        CORS(self.app, origins=['http://localhost:8501', 'http://localhost:3000'])
        
        # Rate limiting
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"]
        )
        
    def get_db_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect(self.app.config['DATABASE_PATH'])
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            return None
            
    def token_required(self, f):
        """JWT authentication decorator"""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            
            if not token:
                return jsonify({'error': 'Token is missing'}), 401
                
            try:
                if token.startswith('Bearer '):
                    token = token[7:]
                data = jwt.decode(token, self.app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
                current_user = data['user_id']
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token has expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Token is invalid'}), 401
                
            return f(current_user, *args, **kwargs)
        return decorated
        
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """API health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            })
            
        @self.app.route('/api/auth/login', methods=['POST'])
        @self.limiter.limit("5 per minute")
        def login():
            """User authentication endpoint"""
            data = request.get_json()
            
            if not data or not data.get('username') or not data.get('password'):
                return jsonify({'error': 'Username and password required'}), 400
                
            # Simple authentication (in production, use proper user database)
            username = data['username']
            password = data['password']
            
            # Demo credentials
            if username == 'admin' and password == 'admin123':
                token = jwt.encode({
                    'user_id': username,
                    'exp': datetime.utcnow() + self.app.config['JWT_ACCESS_TOKEN_EXPIRES']
                }, self.app.config['JWT_SECRET_KEY'], algorithm='HS256')
                
                return jsonify({
                    'token': token,
                    'user': username,
                    'expires_in': int(self.app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
                })
            else:
                return jsonify({'error': 'Invalid credentials'}), 401
                
        @self.app.route('/api/dashboard/stats', methods=['GET'])
        @self.token_required
        def dashboard_stats(current_user):
            """Get dashboard statistics"""
            try:
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                    
                # Get key statistics
                stats = {}
                
                # Total members
                result = conn.execute('SELECT COUNT(*) as count FROM Member').fetchone()
                stats['total_members'] = result['count']
                
                # Active loans
                result = conn.execute('SELECT COUNT(*) as count FROM Loan WHERE Return_Date IS NULL').fetchone()
                stats['active_loans'] = result['count']
                
                # Overdue loans
                result = conn.execute("""
                    SELECT COUNT(*) as count FROM Loan 
                    WHERE Return_Date IS NULL AND Due_Date < date('now')
                """).fetchone()
                stats['overdue_loans'] = result['count']
                
                # Total books
                result = conn.execute('SELECT COUNT(*) as count FROM Item').fetchone()
                stats['total_books'] = result['count']
                
                conn.close()
                
                return jsonify({
                    'status': 'success',
                    'data': stats,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Dashboard stats error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
                
        @self.app.route('/api/predictions/overdue', methods=['POST'])
        @self.token_required
        @self.limiter.limit("10 per minute")
        def predict_overdue(current_user):
            """Predict overdue probability for loans"""
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({'error': 'Request data required'}), 400
                    
                # Load model and make prediction
                predictions = self.model_manager.predict_overdue(data)
                
                return jsonify({
                    'status': 'success',
                    'predictions': predictions,
                    'model_version': '1.0.0',
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Overdue prediction error: {e}")
                return jsonify({'error': f'Prediction failed: {str(e)}'}), 500
                
        @self.app.route('/api/predictions/churn', methods=['POST'])
        @self.token_required
        @self.limiter.limit("10 per minute")
        def predict_churn(current_user):
            """Predict member churn probability"""
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({'error': 'Request data required'}), 400
                    
                # Load model and make prediction
                predictions = self.model_manager.predict_churn(data)
                
                return jsonify({
                    'status': 'success',
                    'predictions': predictions,
                    'model_version': '1.0.0',
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Churn prediction error: {e}")
                return jsonify({'error': f'Prediction failed: {str(e)}'}), 500
                
        @self.app.route('/api/recommendations/<int:member_id>', methods=['GET'])
        @self.token_required
        def get_recommendations(current_user, member_id):
            """Get book recommendations for a member"""
            try:
                limit = request.args.get('limit', 5, type=int)
                
                # Get recommendations from model
                recommendations = self.model_manager.get_recommendations(member_id, limit)
                
                return jsonify({
                    'status': 'success',
                    'member_id': member_id,
                    'recommendations': recommendations,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Recommendations error: {e}")
                return jsonify({'error': f'Recommendations failed: {str(e)}'}), 500
                
        @self.app.route('/api/members', methods=['GET'])
        @self.token_required
        def get_members(current_user):
            """Get members list with pagination"""
            try:
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 20, type=int)
                search = request.args.get('search', '')
                
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                    
                offset = (page - 1) * per_page
                
                if search:
                    query = """
                        SELECT Member_ID, Name, Email, Member_Type 
                        FROM Member 
                        WHERE Name LIKE ? OR Email LIKE ?
                        LIMIT ? OFFSET ?
                    """
                    members = conn.execute(query, (f'%{search}%', f'%{search}%', per_page, offset)).fetchall()
                else:
                    query = "SELECT Member_ID, Name, Email, Member_Type FROM Member LIMIT ? OFFSET ?"
                    members = conn.execute(query, (per_page, offset)).fetchall()
                
                # Convert to list of dicts
                members_list = [dict(member) for member in members]
                
                # Get total count
                if search:
                    total = conn.execute(
                        "SELECT COUNT(*) as count FROM Member WHERE Name LIKE ? OR Email LIKE ?",
                        (f'%{search}%', f'%{search}%')
                    ).fetchone()['count']
                else:
                    total = conn.execute("SELECT COUNT(*) as count FROM Member").fetchone()['count']
                
                conn.close()
                
                return jsonify({
                    'status': 'success',
                    'data': members_list,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'pages': (total + per_page - 1) // per_page
                    },
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Members list error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
                
        @self.app.route('/api/models/status', methods=['GET'])
        @self.token_required
        def models_status(current_user):
            """Get ML models status"""
            try:
                status = self.model_manager.get_models_status()
                
                return jsonify({
                    'status': 'success',
                    'models': status,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Models status error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        # Error handlers
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Endpoint not found'}), 404
            
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({'error': 'Internal server error'}), 500
            
        @self.app.errorhandler(429)
        def ratelimit_handler(e):
            return jsonify({'error': 'Rate limit exceeded', 'retry_after': str(e.retry_after)}), 429
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application"""
        logger.info(f"Starting Library Analytics API on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

def create_app():
    """Application factory"""
    api = LibraryAnalyticsAPI()
    return api.app

if __name__ == '__main__':
    # Initialize and run the application
    try:
        api = LibraryAnalyticsAPI()
        print("🚀 Starting Library Analytics API on http://localhost:5001")
        api.run(debug=True, port=5001, host='127.0.0.1')
    except Exception as e:
        print(f"❌ Error starting API: {e}")
