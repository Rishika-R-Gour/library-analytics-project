#!/usr/bin/env python3
"""
Phase 5: Real Library Management API
Complete library management system with real functionality
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import sys
from datetime import datetime, timedelta
import logging

# Add the advanced API for inheritance
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.advanced_api import AdvancedLibraryAPI

class LibraryManagementAPI(AdvancedLibraryAPI):
    """Extended API with real library management features"""
    
    def __init__(self):
        super().__init__()
        self.setup_library_routes()
        
    def setup_library_routes(self):
        """Setup library management specific routes"""
        
        # Book Management Routes
        @self.app.route('/api/books', methods=['GET'])
        def get_books():
            """Get all books with search and filter options"""
            try:
                search = request.args.get('search', '')
                genre = request.args.get('genre', '')
                available_only = request.args.get('available_only', 'false').lower() == 'true'
                page = int(request.args.get('page', 1))
                per_page = int(request.args.get('per_page', 20))
                
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                
                # Build query
                query = '''
                SELECT book_id, isbn, title, author, publisher, publication_year, 
                       genre, pages, description, total_copies, available_copies, location
                FROM Library_Books 
                WHERE 1=1
                '''
                params = []
                
                if search:
                    query += ' AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)'
                    search_term = f'%{search}%'
                    params.extend([search_term, search_term, search_term])
                
                if genre:
                    query += ' AND genre = ?'
                    params.append(genre)
                
                if available_only:
                    query += ' AND available_copies > 0'
                
                query += ' ORDER BY title LIMIT ? OFFSET ?'
                params.extend([per_page, (page - 1) * per_page])
                
                books = conn.execute(query, params).fetchall()
                
                # Get total count
                count_query = query.replace('SELECT book_id, isbn, title, author, publisher, publication_year, genre, pages, description, total_copies, available_copies, location', 'SELECT COUNT(*)')
                count_query = count_query.split(' ORDER BY')[0]  # Remove ORDER BY and LIMIT
                total_books = conn.execute(count_query, params[:-2]).fetchone()[0]
                
                conn.close()
                
                books_list = []
                for book in books:
                    books_list.append({
                        'book_id': book[0],
                        'isbn': book[1],
                        'title': book[2],
                        'author': book[3],
                        'publisher': book[4],
                        'publication_year': book[5],
                        'genre': book[6],
                        'pages': book[7],
                        'description': book[8],
                        'total_copies': book[9],
                        'available_copies': book[10],
                        'location': book[11],
                        'is_available': book[10] > 0
                    })
                
                return jsonify({
                    'books': books_list,
                    'total': total_books,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total_books + per_page - 1) // per_page
                })
                
            except Exception as e:
                logging.error(f"Error getting books: {e}")
                return jsonify({'error': 'Failed to retrieve books'}), 500
        
        @self.app.route('/api/books/<int:book_id>', methods=['GET'])
        def get_book_details(book_id):
            """Get detailed information about a specific book"""
            try:
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                
                # Get book details
                book = conn.execute('''
                SELECT book_id, isbn, title, author, publisher, publication_year, 
                       genre, pages, description, total_copies, available_copies, 
                       location, dewey_decimal, created_at
                FROM Library_Books WHERE book_id = ?
                ''', (book_id,)).fetchone()
                
                if not book:
                    conn.close()
                    return jsonify({'error': 'Book not found'}), 404
                
                # Get reviews for this book
                reviews = conn.execute('''
                SELECT r.rating, r.review_text, r.review_date, 
                       m.first_name || ' ' || m.last_name as reviewer_name
                FROM Book_Reviews r
                JOIN Member m ON r.member_id = m.member_id
                WHERE r.book_id = ? AND r.is_approved = 1
                ORDER BY r.review_date DESC
                ''', (book_id,)).fetchall()
                
                # Get current loans
                active_loans = conn.execute('''
                SELECT COUNT(*) FROM Library_Loans 
                WHERE book_id = ? AND status = 'active'
                ''', (book_id,)).fetchone()[0]
                
                conn.close()
                
                book_data = {
                    'book_id': book[0],
                    'isbn': book[1],
                    'title': book[2],
                    'author': book[3],
                    'publisher': book[4],
                    'publication_year': book[5],
                    'genre': book[6],
                    'pages': book[7],
                    'description': book[8],
                    'total_copies': book[9],
                    'available_copies': book[10],
                    'location': book[11],
                    'dewey_decimal': book[12],
                    'created_at': book[13],
                    'active_loans': active_loans,
                    'is_available': book[10] > 0,
                    'reviews': [
                        {
                            'rating': review[0],
                            'review_text': review[1],
                            'review_date': review[2],
                            'reviewer_name': review[3]
                        } for review in reviews
                    ],
                    'average_rating': sum(r[0] for r in reviews) / len(reviews) if reviews else 0
                }
                
                return jsonify(book_data)
                
            except Exception as e:
                logging.error(f"Error getting book details: {e}")
                return jsonify({'error': 'Failed to retrieve book details'}), 500
        
        @self.app.route('/api/loans', methods=['POST'])
        @self.token_required
        def create_loan(current_user):
            """Create a new book loan"""
            try:
                data = request.get_json()
                book_id = data.get('book_id')
                member_id = data.get('member_id')
                
                if not book_id or not member_id:
                    return jsonify({'error': 'Book ID and Member ID required'}), 400
                
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                
                # Check if book is available
                book = conn.execute('''
                SELECT available_copies, title FROM Library_Books WHERE book_id = ?
                ''', (book_id,)).fetchone()
                
                if not book:
                    conn.close()
                    return jsonify({'error': 'Book not found'}), 404
                
                if book[0] <= 0:
                    conn.close()
                    return jsonify({'error': 'Book not available'}), 400
                
                # Check if member already has this book
                existing_loan = conn.execute('''
                SELECT loan_id FROM Library_Loans 
                WHERE book_id = ? AND member_id = ? AND status = 'active'
                ''', (book_id, member_id)).fetchone()
                
                if existing_loan:
                    conn.close()
                    return jsonify({'error': 'Member already has this book on loan'}), 400
                
                # Create loan
                loan_date = datetime.now().date()
                due_date = loan_date + timedelta(days=21)  # 3 week loan period
                
                loan_id = conn.execute('''
                INSERT INTO Library_Loans 
                (book_id, member_id, librarian_id, loan_date, due_date, status)
                VALUES (?, ?, ?, ?, ?, 'active')
                ''', (book_id, member_id, current_user['user_id'], loan_date, due_date)).lastrowid
                
                # Update available copies
                conn.execute('''
                UPDATE Library_Books 
                SET available_copies = available_copies - 1 
                WHERE book_id = ?
                ''', (book_id,))
                
                conn.commit()
                conn.close()
                
                return jsonify({
                    'message': 'Loan created successfully',
                    'loan_id': loan_id,
                    'book_title': book[1],
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
                
                # Create fine record if applicable
                if fine_amount > 0:
                    conn.execute('''
                    INSERT INTO Library_Fines 
                    (loan_id, member_id, fine_type, amount, issue_date, status)
                    VALUES (?, ?, 'overdue', ?, ?, 'unpaid')
                    ''', (loan_id, loan[1], fine_amount, return_date))
                
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
        
        @self.app.route('/api/members/<int:member_id>/loans', methods=['GET'])
        @self.token_required
        def get_member_loans(current_user, member_id):
            """Get loan history for a member"""
            try:
                status = request.args.get('status', 'all')  # active, returned, all
                
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                
                query = '''
                SELECT l.loan_id, l.book_id, b.title, b.author, l.loan_date, 
                       l.due_date, l.return_date, l.status, l.fine_amount,
                       l.renewal_count
                FROM Library_Loans l
                JOIN Library_Books b ON l.book_id = b.book_id
                WHERE l.member_id = ?
                '''
                params = [member_id]
                
                if status != 'all':
                    query += ' AND l.status = ?'
                    params.append(status)
                
                query += ' ORDER BY l.loan_date DESC'
                
                loans = conn.execute(query, params).fetchall()
                conn.close()
                
                loans_list = []
                for loan in loans:
                    loan_data = {
                        'loan_id': loan[0],
                        'book_id': loan[1],
                        'book_title': loan[2],
                        'author': loan[3],
                        'loan_date': loan[4],
                        'due_date': loan[5],
                        'return_date': loan[6],
                        'status': loan[7],
                        'fine_amount': loan[8],
                        'renewal_count': loan[9],
                        'days_remaining': None,
                        'is_overdue': False
                    }
                    
                    if loan[7] == 'active' and loan[5]:
                        due_date = datetime.strptime(loan[5], '%Y-%m-%d').date()
                        today = datetime.now().date()
                        days_remaining = (due_date - today).days
                        loan_data['days_remaining'] = days_remaining
                        loan_data['is_overdue'] = days_remaining < 0
                    
                    loans_list.append(loan_data)
                
                return jsonify({'loans': loans_list})
                
            except Exception as e:
                logging.error(f"Error getting member loans: {e}")
                return jsonify({'error': 'Failed to retrieve loans'}), 500
        
        @self.app.route('/api/search', methods=['GET'])
        def search_catalog():
            """Advanced catalog search"""
            try:
                query = request.args.get('q', '')
                search_type = request.args.get('type', 'all')  # title, author, isbn, all
                
                if not query:
                    return jsonify({'error': 'Search query required'}), 400
                
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                
                if search_type == 'title':
                    where_clause = 'title LIKE ?'
                elif search_type == 'author':
                    where_clause = 'author LIKE ?'
                elif search_type == 'isbn':
                    where_clause = 'isbn LIKE ?'
                else:  # all
                    where_clause = '(title LIKE ? OR author LIKE ? OR isbn LIKE ?)'
                
                search_term = f'%{query}%'
                params = [search_term] if search_type != 'all' else [search_term] * 3
                
                books = conn.execute(f'''
                SELECT book_id, title, author, isbn, genre, available_copies, total_copies
                FROM Library_Books 
                WHERE {where_clause}
                ORDER BY title
                LIMIT 50
                ''', params).fetchall()
                
                conn.close()
                
                results = []
                for book in books:
                    results.append({
                        'book_id': book[0],
                        'title': book[1],
                        'author': book[2],
                        'isbn': book[3],
                        'genre': book[4],
                        'available_copies': book[5],
                        'total_copies': book[6],
                        'is_available': book[5] > 0
                    })
                
                return jsonify({
                    'query': query,
                    'search_type': search_type,
                    'results': results,
                    'total_results': len(results)
                })
                
            except Exception as e:
                logging.error(f"Error searching catalog: {e}")
                return jsonify({'error': 'Search failed'}), 500

        @self.app.route('/api/dashboard/library-stats', methods=['GET'])
        @self.token_required
        def get_library_statistics(current_user):
            """Get comprehensive library statistics"""
            try:
                conn = self.get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                
                # Basic stats
                total_books = conn.execute('SELECT COUNT(*) FROM Library_Books').fetchone()[0]
                total_copies = conn.execute('SELECT SUM(total_copies) FROM Library_Books').fetchone()[0]
                available_copies = conn.execute('SELECT SUM(available_copies) FROM Library_Books').fetchone()[0]
                active_loans = conn.execute('SELECT COUNT(*) FROM Library_Loans WHERE status = "active"').fetchone()[0]
                
                # Overdue loans
                today = datetime.now().date()
                overdue_loans = conn.execute('''
                SELECT COUNT(*) FROM Library_Loans 
                WHERE status = 'active' AND due_date < ?
                ''', (today,)).fetchone()[0]
                
                # Popular books (most loaned)
                popular_books = conn.execute('''
                SELECT b.title, b.author, COUNT(l.loan_id) as loan_count
                FROM Library_Books b
                LEFT JOIN Library_Loans l ON b.book_id = l.book_id
                GROUP BY b.book_id
                ORDER BY loan_count DESC
                LIMIT 5
                ''').fetchall()
                
                # Recent activity
                recent_loans = conn.execute('''
                SELECT b.title, m.first_name || ' ' || m.last_name as member_name, 
                       l.loan_date, l.status
                FROM Library_Loans l
                JOIN Library_Books b ON l.book_id = b.book_id
                JOIN Member m ON l.member_id = m.member_id
                ORDER BY l.loan_date DESC
                LIMIT 10
                ''').fetchall()
                
                # Genre distribution
                genre_stats = conn.execute('''
                SELECT genre, COUNT(*) as count
                FROM Library_Books
                GROUP BY genre
                ORDER BY count DESC
                ''').fetchall()
                
                conn.close()
                
                return jsonify({
                    'basic_stats': {
                        'total_books': total_books,
                        'total_copies': total_copies,
                        'available_copies': available_copies,
                        'loaned_copies': total_copies - available_copies,
                        'active_loans': active_loans,
                        'overdue_loans': overdue_loans,
                        'utilization_rate': round((total_copies - available_copies) / total_copies * 100, 1) if total_copies > 0 else 0
                    },
                    'popular_books': [
                        {
                            'title': book[0],
                            'author': book[1],
                            'loan_count': book[2]
                        } for book in popular_books
                    ],
                    'recent_activity': [
                        {
                            'book_title': activity[0],
                            'member_name': activity[1],
                            'loan_date': activity[2],
                            'status': activity[3]
                        } for activity in recent_loans
                    ],
                    'genre_distribution': [
                        {
                            'genre': genre[0],
                            'count': genre[1]
                        } for genre in genre_stats
                    ]
                })
                
            except Exception as e:
                logging.error(f"Error getting library statistics: {e}")
                return jsonify({'error': 'Failed to retrieve statistics'}), 500

def main():
    """Main function to run the library management API"""
    api = LibraryManagementAPI()
    
    print("🚀 Starting Phase 5: Library Management API")
    print("=" * 60)
    print("📚 Enhanced Features:")
    print("  ✅ Complete book catalog management")
    print("  ✅ Loan processing (checkout/return)")
    print("  ✅ Advanced search capabilities")
    print("  ✅ Member loan history")
    print("  ✅ Library statistics dashboard")
    print("  ✅ Overdue tracking and fines")
    print("\n🔗 API running on: http://localhost:5003")
    print("🎯 Ready for Phase 5 dashboard integration!")
    print("=" * 60)
    
    api.app.run(host='0.0.0.0', port=5003, debug=True)

if __name__ == "__main__":
    main()
