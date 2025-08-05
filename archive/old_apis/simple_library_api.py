#!/usr/bin/env python3
"""
Phase 5: Simple Library Management API
"""

import sqlite3
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

class SimpleLibraryAPI:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        
        self.setup_routes()
        
    def get_db_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect('../notebooks/library.db')
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logging.error(f"Database connection error: {e}")
            return None
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/', methods=['GET'])
        def root():
            """Root endpoint with API information"""
            return jsonify({
                'service': 'Library Management API',
                'version': '5.0.0',
                'status': 'running',
                'endpoints': [
                    'GET /api/health - Health check',
                    'GET /api/books - Get all books',
                    'GET /api/search?q=<query> - Search catalog',
                    'GET /api/dashboard/library-stats - Library statistics'
                ],
                'sample_requests': [
                    'curl http://localhost:5003/api/books',
                    'curl "http://localhost:5003/api/search?q=programming"',
                    'curl http://localhost:5003/api/dashboard/library-stats'
                ]
            })
        
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
                       description
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
                        'description': book[8]
                    })
                
                return jsonify({'books': books_list, 'total': len(books_list)})
                
            except Exception as e:
                logging.error(f"Error getting books: {e}")
                return jsonify({'error': f'Failed to retrieve books: {str(e)}'}), 500
        
        @self.app.route('/api/search', methods=['GET'])
        def search_catalog():
            """Search book catalog"""
            try:
                query = request.args.get('q', '')
                if not query:
                    return jsonify({'error': 'Search query required'}), 400
                
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                
                search_term = f'%{query}%'
                
                books = conn.execute('''
                SELECT book_id, title, author, isbn, genre,
                       total_copies, available_copies
                FROM Library_Books
                WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ? OR genre LIKE ?
                ORDER BY title
                ''', [search_term, search_term, search_term, search_term]).fetchall()
                
                conn.close()
                
                results = []
                for book in books:
                    results.append({
                        'book_id': book[0],
                        'title': book[1],
                        'author': book[2],
                        'isbn': book[3],
                        'genre': book[4],
                        'total_copies': book[5],
                        'available_copies': book[6]
                    })
                
                return jsonify({
                    'results': results,
                    'total': len(results),
                    'query': query
                })
                
            except Exception as e:
                logging.error(f"Error searching catalog: {e}")
                return jsonify({'error': 'Search failed'}), 500
        
        @self.app.route('/api/dashboard/library-stats', methods=['GET'])
        def get_library_stats():
            """Get library statistics"""
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
                
                # Popular genres
                popular_genres = conn.execute('''
                SELECT genre, COUNT(*) as count
                FROM Library_Books
                GROUP BY genre
                ORDER BY count DESC
                LIMIT 5
                ''').fetchall()
                
                conn.close()
                
                stats = {
                    'total_books': total_books,
                    'available_books': available_books,
                    'active_loans': active_loans,
                    'popular_genres': [
                        {'genre': genre[0], 'count': genre[1]} 
                        for genre in popular_genres
                    ]
                }
                
                return jsonify(stats)
                
            except Exception as e:
                logging.error(f"Error getting library stats: {e}")
                return jsonify({'error': 'Failed to retrieve statistics'}), 500

def main():
    """Main function to start the API"""
    try:
        print("🚀 Starting Simple Library Management API...")
        
        api = SimpleLibraryAPI()
        
        print("✅ Library Management API initialized!")
        print("🔗 Available endpoints:")
        print("   📚 GET  /api/books - Get all books")
        print("   🔍 GET  /api/search?q=<query> - Search catalog")
        print("   📊 GET  /api/dashboard/library-stats - Library statistics")
        print("   ❤️  GET  /api/health - Health check")
        print("")
        print("🌐 Starting server on http://localhost:5003")
        
        api.app.run(host='0.0.0.0', port=5003, debug=False)
        
    except Exception as e:
        logging.error(f"Failed to start API: {e}")
        print(f"❌ Error starting API: {e}")

if __name__ == '__main__':
    main()
