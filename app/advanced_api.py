#!/usr/bin/env python3
"""
Phase 3: Advanced Library Analytics API
Enhanced API with multi-role authentication and advanced features
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
import json

# Add models directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models.model_manager import ModelManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedLibraryAPI:
    """Advanced Flask application with multi-role authentication and analytics"""
    
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
        """Setup Flask extensions"""
        CORS(self.app)
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
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return None
            
    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        try:
            salt, stored_hash = password_hash.split(':')
            pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return pwd_hash.hex() == stored_hash
        except:
            return False
            
    def log_user_activity(self, user_id, action, resource, details=None, ip_address=None, user_agent=None):
        """Log user activity"""
        try:
            conn = self.get_db_connection()
            if conn:
                conn.execute('''
                INSERT INTO User_Activity_Log (user_id, action, resource, details, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, action, resource, details, ip_address, user_agent))
                conn.commit()
                conn.close()
        except Exception as e:
            logger.error(f"Activity logging error: {e}")
            
    def check_permission(self, user_permissions, required_permission):
        """Check if user has required permission"""
        if not user_permissions:
            return False
        permissions = json.loads(user_permissions) if isinstance(user_permissions, str) else user_permissions
        return "all" in permissions or required_permission in permissions
        
    def token_required(self, permission=None):
        """Enhanced token decorator with permission checking"""
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                token = request.headers.get('Authorization')
                
                if not token:
                    return jsonify({'error': 'Token is missing'}), 401
                    
                try:
                    if token.startswith('Bearer '):
                        token = token[7:]
                    data = jwt.decode(token, self.app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
                    current_user_id = data['user_id']
                    current_user_role = data.get('role', 'member')
                    current_user_permissions = data.get('permissions', [])
                    
                    # Check permission if required
                    if permission and not self.check_permission(current_user_permissions, permission):
                        return jsonify({'error': 'Insufficient permissions'}), 403
                        
                    # Log activity
                    self.log_user_activity(
                        current_user_id, 
                        f.__name__, 
                        request.endpoint,
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent')
                    )
                    
                except jwt.ExpiredSignatureError:
                    return jsonify({'error': 'Token has expired'}), 401
                except jwt.InvalidTokenError:
                    return jsonify({'error': 'Token is invalid'}), 401
                    
                return f(current_user_id, current_user_role, *args, **kwargs)
            return decorated
        return decorator
        
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/', methods=['GET'])
        def root():
            """Root endpoint with API information"""
            return jsonify({
                'service': 'Advanced Library API',
                'version': '3.0.0',
                'status': 'running',
                'features': ['multi_role_auth', 'advanced_analytics', 'user_management'],
                'endpoints': [
                    'GET /api/health - Health check',
                    'POST /api/auth/login - User authentication',
                    'GET /api/users - Get users (auth required)',
                    'POST /api/users - Create user',
                    'GET /api/dashboard/user-activity - User activity analytics'
                ],
                'sample_login': {
                    'url': 'POST http://localhost:5002/api/auth/login',
                    'body': {'username': 'admin', 'password': 'admin123'}
                }
            })
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """API health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '3.0.0',
                'features': ['multi_role_auth', 'advanced_analytics', 'user_management']
            })
            
        @self.app.route('/api/auth/login', methods=['POST'])
        @self.limiter.limit("5 per minute")
        def login():
            """Enhanced user authentication endpoint"""
            data = request.get_json()
            
            if not data or not data.get('username') or not data.get('password'):
                return jsonify({'error': 'Username and password required'}), 400
                
            username = data['username']
            password = data['password']
            
            try:
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                    
                # Get user with role information
                user = conn.execute('''
                SELECT u.user_id, u.username, u.email, u.password_hash, u.first_name, u.last_name,
                       u.is_active, r.role_name, r.permissions
                FROM Advanced_Users u
                JOIN User_Roles r ON u.role_id = r.role_id
                WHERE u.username = ? AND u.is_active = 1
                ''', (username,)).fetchone()
                
                if user and self.verify_password(password, user['password_hash']):
                    # Update last login
                    conn.execute('UPDATE Advanced_Users SET last_login = ? WHERE user_id = ?', 
                               (datetime.now(), user['user_id']))
                    conn.commit()
                    
                    # Create token with role and permissions
                    token_data = {
                        'user_id': user['user_id'],
                        'username': user['username'],
                        'role': user['role_name'],
                        'permissions': json.loads(user['permissions']),
                        'exp': datetime.utcnow() + self.app.config['JWT_ACCESS_TOKEN_EXPIRES']
                    }
                    
                    token = jwt.encode(token_data, self.app.config['JWT_SECRET_KEY'], algorithm='HS256')
                    
                    # Log successful login
                    self.log_user_activity(user['user_id'], 'login', 'authentication', 
                                         f"Successful login as {user['role_name']}")
                    
                    conn.close()
                    
                    return jsonify({
                        'token': token,
                        'user': {
                            'id': user['user_id'],
                            'username': user['username'],
                            'email': user['email'],
                            'first_name': user['first_name'],
                            'last_name': user['last_name'],
                            'role': user['role_name']
                        },
                        'expires_in': int(self.app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds())
                    })
                else:
                    # Log failed login attempt
                    if user:
                        self.log_user_activity(user['user_id'], 'login_failed', 'authentication', 
                                             "Invalid password")
                    
                    conn.close()
                    return jsonify({'error': 'Invalid credentials'}), 401
                    
            except Exception as e:
                logger.error(f"Login error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
                
        @self.app.route('/api/auth/register', methods=['POST'])
        @self.limiter.limit("3 per minute")
        def register():
            """User registration endpoint"""
            data = request.get_json()
            required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
            
            if not all(field in data for field in required_fields):
                return jsonify({'error': 'All fields required'}), 400
                
            try:
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                    
                # Check if username or email already exists
                existing = conn.execute('''
                SELECT COUNT(*) as count FROM Advanced_Users 
                WHERE username = ? OR email = ?
                ''', (data['username'], data['email'])).fetchone()
                
                if existing['count'] > 0:
                    conn.close()
                    return jsonify({'error': 'Username or email already exists'}), 409
                    
                # Hash password
                salt = secrets.token_hex(16)
                pwd_hash = hashlib.pbkdf2_hmac('sha256', data['password'].encode('utf-8'), 
                                             salt.encode('utf-8'), 100000)
                password_hash = f"{salt}:{pwd_hash.hex()}"
                
                # Get member role ID (default for new registrations)
                role = conn.execute('SELECT role_id FROM User_Roles WHERE role_name = ?', 
                                  ('member',)).fetchone()
                
                # Insert new user
                cursor = conn.execute('''
                INSERT INTO Advanced_Users 
                (username, email, password_hash, first_name, last_name, role_id)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (data['username'], data['email'], password_hash, 
                      data['first_name'], data['last_name'], role['role_id']))
                
                user_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                return jsonify({
                    'message': 'User registered successfully',
                    'user_id': user_id
                }), 201
                
            except Exception as e:
                logger.error(f"Registration error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
                
        @self.app.route('/api/users', methods=['GET'])
        @self.token_required(permission='read_all')
        def get_users(current_user_id, current_user_role):
            """Get all users (admin/librarian only)"""
            try:
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                    
                users = conn.execute('''
                SELECT u.user_id, u.username, u.email, u.first_name, u.last_name,
                       u.is_active, u.last_login, u.created_at, r.role_name
                FROM Advanced_Users u
                JOIN User_Roles r ON u.role_id = r.role_id
                ORDER BY u.created_at DESC
                ''').fetchall()
                
                users_list = []
                for user in users:
                    users_list.append({
                        'id': user['user_id'],
                        'username': user['username'],
                        'email': user['email'],
                        'first_name': user['first_name'],
                        'last_name': user['last_name'],
                        'role': user['role_name'],
                        'is_active': bool(user['is_active']),
                        'last_login': user['last_login'],
                        'created_at': user['created_at']
                    })
                
                conn.close()
                return jsonify({'users': users_list})
                
            except Exception as e:
                logger.error(f"Get users error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
                
        @self.app.route('/api/users/<int:user_id>', methods=['PUT'])
        @self.token_required(permission='read_all')
        def update_user(current_user_id, current_user_role, user_id):
            """Update user (admin only)"""
            if current_user_role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
                
            data = request.get_json()
            try:
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                    
                # Build update query dynamically
                update_fields = []
                values = []
                
                if 'is_active' in data:
                    update_fields.append('is_active = ?')
                    values.append(data['is_active'])
                    
                if 'role_name' in data:
                    # Get role_id from role_name
                    role = conn.execute('SELECT role_id FROM User_Roles WHERE role_name = ?', 
                                      (data['role_name'],)).fetchone()
                    if role:
                        update_fields.append('role_id = ?')
                        values.append(role['role_id'])
                
                if update_fields:
                    values.append(user_id)
                    query = f"UPDATE Advanced_Users SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?"
                    conn.execute(query, values)
                    conn.commit()
                
                conn.close()
                return jsonify({'message': 'User updated successfully'})
                
            except Exception as e:
                logger.error(f"Update user error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
                
        @self.app.route('/api/analytics/dashboard', methods=['GET'])
        @self.token_required()
        def advanced_dashboard_stats(current_user_id, current_user_role):
            """Advanced dashboard statistics with role-based data"""
            try:
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                    
                stats = {}
                
                # Base statistics (all roles can see)
                result = conn.execute('SELECT COUNT(*) as count FROM Member').fetchone()
                stats['total_members'] = result['count']
                
                result = conn.execute('SELECT COUNT(*) as count FROM Item').fetchone()
                stats['total_books'] = result['count']
                
                result = conn.execute('SELECT COUNT(*) as count FROM Loan WHERE Return_Date IS NULL').fetchone()
                stats['active_loans'] = result['count']
                
                # Role-specific statistics
                if current_user_role in ['admin', 'librarian']:
                    # Advanced stats for staff
                    result = conn.execute('''
                        SELECT COUNT(*) as count FROM Loan 
                        WHERE Return_Date IS NULL AND Due_Date < date('now')
                    ''').fetchone()
                    stats['overdue_loans'] = result['count']
                    
                    # User registration trends (last 30 days)
                    result = conn.execute('''
                        SELECT COUNT(*) as count FROM Advanced_Users 
                        WHERE created_at >= date('now', '-30 days')
                    ''').fetchone()
                    stats['new_users_30_days'] = result['count']
                    
                    # Active users today
                    result = conn.execute('''
                        SELECT COUNT(DISTINCT user_id) as count FROM User_Activity_Log 
                        WHERE date(timestamp) = date('now')
                    ''').fetchone()
                    stats['active_users_today'] = result['count']
                    
                if current_user_role == 'admin':
                    # Admin-only statistics
                    result = conn.execute('SELECT COUNT(*) as count FROM Advanced_Users').fetchone()
                    stats['total_system_users'] = result['count']
                    
                    # System activity summary
                    result = conn.execute('''
                        SELECT COUNT(*) as count FROM User_Activity_Log 
                        WHERE timestamp >= datetime('now', '-24 hours')
                    ''').fetchone()
                    stats['system_activity_24h'] = result['count']
                
                conn.close()
                
                return jsonify({
                    'status': 'success',
                    'data': stats,
                    'user_role': current_user_role,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Advanced dashboard stats error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
                
        @self.app.route('/api/analytics/user-activity', methods=['GET'])
        @self.token_required(permission='read_all')
        def get_user_activity(current_user_id, current_user_role):
            """Get user activity logs (admin/librarian only)"""
            try:
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                    
                # Get query parameters
                limit = request.args.get('limit', 50, type=int)
                user_filter = request.args.get('user_id', type=int)
                
                query = '''
                SELECT l.log_id, l.user_id, l.action, l.resource, l.details, l.timestamp,
                       u.username, u.first_name, u.last_name
                FROM User_Activity_Log l
                JOIN Advanced_Users u ON l.user_id = u.user_id
                '''
                params = []
                
                if user_filter:
                    query += ' WHERE l.user_id = ?'
                    params.append(user_filter)
                    
                query += ' ORDER BY l.timestamp DESC LIMIT ?'
                params.append(limit)
                
                activities = conn.execute(query, params).fetchall()
                
                activity_list = []
                for activity in activities:
                    activity_list.append({
                        'id': activity['log_id'],
                        'user_id': activity['user_id'],
                        'username': activity['username'],
                        'user_name': f"{activity['first_name']} {activity['last_name']}",
                        'action': activity['action'],
                        'resource': activity['resource'],
                        'details': activity['details'],
                        'timestamp': activity['timestamp']
                    })
                
                conn.close()
                return jsonify({'activities': activity_list})
                
            except Exception as e:
                logger.error(f"User activity error: {e}")
                return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    api = AdvancedLibraryAPI()
    app = api.app
    app.run(host='0.0.0.0', port=5002, debug=True)
