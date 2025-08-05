#!/usr/bin/env python3
import sqlite3
import sys
import os

# Test database connection from app directory
os.chdir('/Users/rishikagour/library_analytics_project/app')

print("Testing database connections...")

# Try different paths
db_paths = ['../notebooks/library.db', 'library.db', 'notebooks/library.db']

for db_path in db_paths:
    try:
        print(f"Trying: {db_path}")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # Test query
        books = conn.execute('SELECT COUNT(*) FROM Library_Books').fetchone()
        print(f"✅ Success! Found {books[0]} books in {db_path}")
        
        # Test actual query
        books = conn.execute('''
        SELECT book_id, title, author, available_copies 
        FROM Library_Books 
        LIMIT 3
        ''').fetchall()
        
        for book in books:
            print(f"  📚 {book[1]} by {book[2]} ({book[3]} available)")
        
        conn.close()
        print(f"Database path that works: {db_path}")
        break
        
    except Exception as e:
        print(f"❌ Failed with {db_path}: {e}")
        continue
else:
    print("❌ No database connection worked")
