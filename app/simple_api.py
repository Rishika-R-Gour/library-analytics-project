#!/usr/bin/env python3
"""
Simple Flask API for Library Analytics
Minimal working example to test localhost serving
"""

from flask import Flask, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Library Analytics API is running!',
        'timestamp': datetime.now().isoformat(),
        'status': 'healthy'
    })

@app.route('/health')
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
            'total_loans': count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/stats')
def stats():
    try:
        conn = sqlite3.connect('notebooks/library.db')
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute("SELECT COUNT(*) FROM Loan")
        total_loans = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT member_id) FROM Loan")
        unique_members = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT item_id) FROM Loan")
        unique_items = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Member")
        total_members = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total_loans': total_loans,
            'unique_members': unique_members,
            'unique_items': unique_items,
            'total_members': total_members,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Simple Library Analytics API...")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📊 Database: notebooks/library.db")
    print("✨ Endpoints available:")
    print("   GET /         - Welcome message")
    print("   GET /health   - Health check with DB connection")
    print("   GET /stats    - Basic statistics")
    print("-" * 50)
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        use_reloader=False
    )
