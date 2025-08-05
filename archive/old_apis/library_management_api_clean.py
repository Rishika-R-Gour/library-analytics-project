#!/usr/bin/env python3
"""
Phase 5: Library Management API
Real library management system with book catalog, loans, and search
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from functools import wraps
import jwt
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

class LibraryManagementAPI:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'library-management-secret-key-2024'
        CORS(self.app)
        
        # Rate limiting
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"]
        )
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('api.log'),
                logging.StreamHandler()
            ]
        )
        
        self.setup_routes()
        
    def get_db_connection(self):
        """Get database connection"""
        try:
            # Use the correct path from app directory
            conn = sqlite3.connect('../notebooks/library.db')
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logging.error(f"Database connection error: {e}")
            return None
    
    def token_required(self, f):
        """JWT token validation decorator"""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            
            if not token:
                return jsonify({'error': 'Token is missing'}), 401
                
            try:
                if token.startswith('Bearer '):
                    token = token.split(' ')[1]
                
                data = jwt.decode(token, self.app.config['SECRET_KEY'], algorithms=['HS256'])
                current_user = data['user']
                
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token has expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Token is invalid'}), 401
                
            return f(current_user, *args, **kwargs)
        return decorated
    
    def setup_routes(self):
        """Setup all API routes"""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """API health check"""
            return jsonify({
                'status': 'healthy',
                'service': 'Library Management API',
                'version': '5.0.0',
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/books', methods=['GET'])
        def get_books():
            """Get all books in catalog"""
            try:
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                
                books = conn.execute('''
                SELECT book_id, title, author, isbn, genre, 
                       total_copies, available_copies, publication_year,
                       description, NULL as rating
                FROM Library_Books
                ORDER BY title
                ''').fetchall()
                
                conn.close()
                
                books_list = []
                for book in books:
                    books_list.append({
                        'book_id': book[0],
                        'title': book[1],
                        'author': book[2],
                        'isbn': book[3],
                        'genre': book[4],
                        'total_copies': book[5],
                        'available_copies': book[6],
                        'publication_year': book[7],
                        'description': book[8],
                        'rating': book[9]
                    })
                
                return jsonify({'books': books_list, 'total': len(books_list)})
                
            except Exception as e:
                logging.error(f"Error getting books: {e}")
                return jsonify({'error': 'Failed to retrieve books'}), 500
        
        @self.app.route('/api/books/<int:book_id>', methods=['GET'])
        def get_book(book_id):
            """Get specific book details"""
            try:
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                
                book = conn.execute('''
                SELECT * FROM Library_Books WHERE book_id = ?
                ''', (book_id,)).fetchone()
                
                if not book:
                    conn.close()
                    return jsonify({'error': 'Book not found'}), 404
                
                # Get reviews for this book
                reviews = conn.execute('''
                SELECT reviewer_name, rating, review_text, review_date
                FROM Book_Reviews
                WHERE book_id = ?
                ORDER BY review_date DESC
                ''', (book_id,)).fetchall()
                
                conn.close()
                
                book_data = {
                    'book_id': book[0],
                    'title': book[1],
                    'author': book[2],
                    'isbn': book[3],
                    'category': book[4],
                    'total_copies': book[5],
                    'available_copies': book[6],
                    'publication_year': book[7],
                    'description': book[8],
                    'rating': book[9],
                    'reviews': []
                }
                
                for review in reviews:
                    book_data['reviews'].append({
                        'reviewer': review[0],
                        'rating': review[1],
                        'text': review[2],
                        'date': review[3]
                    })
                
                return jsonify(book_data)
                
            except Exception as e:
                logging.error(f"Error getting book: {e}")
                return jsonify({'error': 'Failed to retrieve book'}), 500
        
        @self.app.route('/api/search', methods=['GET'])
        def search_catalog():
            """Search book catalog"""
            try:
                query = request.args.get('q', '')
                search_type = request.args.get('type', 'all')
                
                if not query:
                    return jsonify({'error': 'Search query required'}), 400
                
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                
                search_term = f'%{query}%'
                
                if search_type == 'title':
                    where_clause = 'title LIKE ?'
                    params = [search_term]
                elif search_type == 'author':
                    where_clause = 'author LIKE ?'
                    params = [search_term]
                elif search_type == 'isbn':
                    where_clause = 'isbn LIKE ?'
                    params = [search_term]
                else:  # search all
                    where_clause = 'title LIKE ? OR author LIKE ? OR isbn LIKE ? OR category LIKE ?'
                    params = [search_term, search_term, search_term, search_term]
                
                books = conn.execute(f'''
                SELECT book_id, title, author, isbn, category,
                       total_copies, available_copies, rating
                FROM Library_Books
                WHERE {where_clause}
                ORDER BY title
                ''', params).fetchall()
                
                conn.close()
                
                results = []
                for book in books:
                    results.append({
                        'book_id': book[0],
                        'title': book[1],
                        'author': book[2],
                        'isbn': book[3],
                        'category': book[4],
                        'total_copies': book[5],
                        'available_copies': book[6],
                        'rating': book[7]
                    })
                
                return jsonify({
                    'results': results,
                    'total': len(results),
                    'query': query,
                    'search_type': search_type
                })
                
            except Exception as e:
                logging.error(f"Error searching catalog: {e}")
                return jsonify({'error': 'Search failed'}), 500
        
        @self.app.route('/api/loans', methods=['POST'])
        @self.token_required
        def create_loan(current_user):
            """Create a new book loan"""
            try:
                data = request.get_json()
                if not data or 'book_id' not in data or 'member_id' not in data:
                    return jsonify({'error': 'book_id and member_id required'}), 400
                
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                
                # Check book availability
                book = conn.execute('''
                SELECT title, available_copies FROM Library_Books 
                WHERE book_id = ?
                ''', (data['book_id'],)).fetchone()
                
                if not book:
                    conn.close()
                    return jsonify({'error': 'Book not found'}), 404
                
                if book[1] <= 0:
                    conn.close()
                    return jsonify({'error': 'No copies available'}), 400
                
                # Create loan
                loan_date = datetime.now().date()
                due_date = loan_date + timedelta(days=14)  # 2 week loan period
                
                cursor = conn.execute('''
                INSERT INTO Library_Loans 
                (book_id, member_id, loan_date, due_date, status)
                VALUES (?, ?, ?, ?, 'active')
                ''', (data['book_id'], data['member_id'], loan_date, due_date))
                
                loan_id = cursor.lastrowid
                
                # Update available copies
                conn.execute('''
                UPDATE Library_Books 
                SET available_copies = available_copies - 1 
                WHERE book_id = ?
                ''', (data['book_id'],))
                
                conn.commit()
                conn.close()
                
                return jsonify({
                    'message': 'Loan created successfully',
                    'loan_id': loan_id,
                    'book_title': book[0],
                    'loan_date': loan_date.isoformat(),
                    'due_date': due_date.isoformat()
                }), 201
                
            except Exception as e:
                logging.error(f"Error creating loan: {e}")
                return jsonify({'error': 'Failed to create loan'}), 500
        
        @self.app.route('/api/loans/<int:loan_id>/return', methods=['POST'])
        @self.token_required
        def return_book(current_user, loan_id):
            """Process book return"""
            try:
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                
                # Get loan details
                loan = conn.execute('''
                SELECT l.book_id, l.member_id, l.due_date, b.title
                FROM Library_Loans l
                JOIN Library_Books b ON l.book_id = b.book_id
                WHERE l.loan_id = ? AND l.status = 'active'
                ''', (loan_id,)).fetchone()
                
                if not loan:
                    conn.close()
                    return jsonify({'error': 'Active loan not found'}), 404
                
                return_date = datetime.now().date()
                due_date = datetime.strptime(loan[2], '%Y-%m-%d').date()
                
                # Calculate fine if overdue
                fine_amount = 0
                if return_date > due_date:
                    overdue_days = (return_date - due_date).days
                    fine_amount = overdue_days * 0.50  # $0.50 per day
                
                # Update loan record
                conn.execute('''
                UPDATE Library_Loans 
                SET return_date = ?, status = 'returned', fine_amount = ?
                WHERE loan_id = ?
                ''', (return_date, fine_amount, loan_id))
                
                # Update available copies
                conn.execute('''
                UPDATE Library_Books 
                SET available_copies = available_copies + 1 
                WHERE book_id = ?
                ''', (loan[0],))
                
                conn.commit()
                conn.close()
                
                response_data = {
                    'message': 'Book returned successfully',
                    'book_title': loan[3],
                    'return_date': return_date.isoformat(),
                    'was_overdue': return_date > due_date,
                    'fine_amount': fine_amount
                }
                
                if fine_amount > 0:
                    response_data['fine_message'] = f'Overdue fine: ${fine_amount:.2f}'
                
                return jsonify(response_data)
                
            except Exception as e:
                logging.error(f"Error returning book: {e}")
                return jsonify({'error': 'Failed to process return'}), 500
        
        @self.app.route('/api/dashboard/library-stats', methods=['GET'])
        def get_library_stats():
            """Get library statistics for dashboard"""
            try:
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                
                # Total books
                total_books = conn.execute('SELECT COUNT(*) FROM Library_Books').fetchone()[0]
                
                # Available books
                available_books = conn.execute('''
                SELECT SUM(available_copies) FROM Library_Books
                ''').fetchone()[0] or 0
                
                # Active loans
                active_loans = conn.execute('''
                SELECT COUNT(*) FROM Library_Loans WHERE status = 'active'
                ''').fetchone()[0]
                
                # Overdue loans
                today = datetime.now().date()
                overdue_loans = conn.execute('''
                SELECT COUNT(*) FROM Library_Loans 
                WHERE status = 'active' AND due_date < ?
                ''', (today,)).fetchone()[0]
                
                # Popular categories
                popular_categories = conn.execute('''
                SELECT category, COUNT(*) as count
                FROM Library_Books
                GROUP BY category
                ORDER BY count DESC
                LIMIT 5
                ''').fetchall()
                
                # Recent loans
                recent_loans = conn.execute('''
                SELECT b.title, l.loan_date, l.member_id
                FROM Library_Loans l
                JOIN Library_Books b ON l.book_id = b.book_id
                ORDER BY l.loan_date DESC
                LIMIT 10
                ''').fetchall()
                
                conn.close()
                
                stats = {
                    'total_books': total_books,
                    'available_books': available_books,
                    'active_loans': active_loans,
                    'overdue_loans': overdue_loans,
                    'popular_categories': [
                        {'category': cat[0], 'count': cat[1]} 
                        for cat in popular_categories
                    ],
                    'recent_activity': [
                        {
                            'book_title': loan[0],
                            'loan_date': loan[1],
                            'member_id': loan[2]
                        }
                        for loan in recent_loans
                    ]
                }
                
                return jsonify(stats)
                
            except Exception as e:
                logging.error(f"Error getting library stats: {e}")
                return jsonify({'error': 'Failed to retrieve statistics'}), 500

def main():
    """Main function to start the API"""
    try:
        print("🚀 Starting Library Management API...")
        print("📚 Initializing library services...")
        
        api = LibraryManagementAPI()
        
        print("✅ Library Management API initialized successfully!")
        print("🔗 Available endpoints:")
        print("   📚 GET  /api/books - Get all books")
        print("   🔍 GET  /api/search?q=<query> - Search catalog")
        print("   📖 GET  /api/books/<id> - Get book details")
        print("   📋 POST /api/loans - Create loan")
        print("   📤 POST /api/loans/<id>/return - Return book")
        print("   📊 GET  /api/dashboard/library-stats - Library statistics")
        print("   ❤️  GET  /api/health - Health check")
        print("")
        print("🌐 Starting server on http://localhost:5003")
        print("📊 Real library management features active!")
        
        api.app.run(host='0.0.0.0', port=5003, debug=False)
        
    except Exception as e:
        logging.error(f"Failed to start Library Management API: {e}")
        print(f"❌ Error starting API: {e}")

if __name__ == '__main__':
    main()
