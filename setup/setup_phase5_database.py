#!/usr/bin/env python3
"""
Phase 5: Real Library Features Database Setup
Creates comprehensive library management schema with real functionality
"""

import sqlite3
import os
import sys
from datetime import datetime, timedelta
import random
import json

def create_enhanced_library_schema():
    """Create comprehensive library management tables"""
    
    db_path = os.path.join('notebooks', 'library.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🗄️ Creating Enhanced Library Schema...")
    
    # Enhanced Books Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Library_Books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        isbn VARCHAR(13) UNIQUE,
        title VARCHAR(255) NOT NULL,
        author VARCHAR(255) NOT NULL,
        publisher VARCHAR(255),
        publication_year INTEGER,
        genre VARCHAR(100),
        language VARCHAR(50) DEFAULT 'English',
        pages INTEGER,
        description TEXT,
        cover_image_url VARCHAR(500),
        total_copies INTEGER DEFAULT 1,
        available_copies INTEGER DEFAULT 1,
        location VARCHAR(100),
        dewey_decimal VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Enhanced Loans Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Library_Loans (
        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        member_id INTEGER NOT NULL,
        librarian_id INTEGER,
        loan_date DATE NOT NULL,
        due_date DATE NOT NULL,
        return_date DATE,
        renewal_count INTEGER DEFAULT 0,
        max_renewals INTEGER DEFAULT 2,
        status VARCHAR(20) DEFAULT 'active',
        fine_amount DECIMAL(10,2) DEFAULT 0.00,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (book_id) REFERENCES Library_Books(book_id),
        FOREIGN KEY (member_id) REFERENCES Member(member_id)
    )
    ''')
    
    # Book Reviews Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Book_Reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        member_id INTEGER NOT NULL,
        rating INTEGER CHECK (rating >= 1 AND rating <= 5),
        review_text TEXT,
        review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_approved BOOLEAN DEFAULT 1,
        helpful_votes INTEGER DEFAULT 0,
        FOREIGN KEY (book_id) REFERENCES Library_Books(book_id),
        FOREIGN KEY (member_id) REFERENCES Member(member_id)
    )
    ''')
    
    # Book Reservations Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Book_Reservations (
        reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        member_id INTEGER NOT NULL,
        reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expiry_date TIMESTAMP,
        status VARCHAR(20) DEFAULT 'active',
        notification_sent BOOLEAN DEFAULT 0,
        FOREIGN KEY (book_id) REFERENCES Library_Books(book_id),
        FOREIGN KEY (member_id) REFERENCES Member(member_id)
    )
    ''')
    
    # Member Reading History
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reading_History (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        read_date DATE,
        completion_status VARCHAR(20) DEFAULT 'completed',
        reading_duration_days INTEGER,
        personal_rating INTEGER CHECK (personal_rating >= 1 AND personal_rating <= 5),
        notes TEXT,
        FOREIGN KEY (member_id) REFERENCES Member(member_id),
        FOREIGN KEY (book_id) REFERENCES Library_Books(book_id)
    )
    ''')
    
    # Fine Management Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Library_Fines (
        fine_id INTEGER PRIMARY KEY AUTOINCREMENT,
        loan_id INTEGER NOT NULL,
        member_id INTEGER NOT NULL,
        fine_type VARCHAR(50) NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        due_date DATE,
        paid_date TIMESTAMP,
        payment_method VARCHAR(50),
        status VARCHAR(20) DEFAULT 'unpaid',
        waived BOOLEAN DEFAULT 0,
        waived_by INTEGER,
        notes TEXT,
        FOREIGN KEY (loan_id) REFERENCES Library_Loans(loan_id),
        FOREIGN KEY (member_id) REFERENCES Member(member_id)
    )
    ''')
    
    # Library Events Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Library_Events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        event_date DATE NOT NULL,
        start_time TIME,
        end_time TIME,
        location VARCHAR(255),
        max_attendees INTEGER,
        current_attendees INTEGER DEFAULT 0,
        event_type VARCHAR(100),
        age_group VARCHAR(50),
        registration_required BOOLEAN DEFAULT 0,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(20) DEFAULT 'active'
    )
    ''')
    
    # Event Registrations Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Event_Registrations (
        registration_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        member_id INTEGER NOT NULL,
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        attended BOOLEAN DEFAULT 0,
        feedback TEXT,
        rating INTEGER CHECK (rating >= 1 AND rating <= 5),
        FOREIGN KEY (event_id) REFERENCES Library_Events(event_id),
        FOREIGN KEY (member_id) REFERENCES Member(member_id)
    )
    ''')
    
    # Book Categories/Tags Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Book_Categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name VARCHAR(100) UNIQUE NOT NULL,
        description TEXT,
        parent_category_id INTEGER,
        display_order INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_category_id) REFERENCES Book_Categories(category_id)
    )
    ''')
    
    # Book-Category Mapping Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Book_Category_Mapping (
        mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        FOREIGN KEY (book_id) REFERENCES Library_Books(book_id),
        FOREIGN KEY (category_id) REFERENCES Book_Categories(category_id),
        UNIQUE(book_id, category_id)
    )
    ''')
    
    # Member Preferences Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Member_Reading_Preferences (
        preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER NOT NULL,
        preferred_genres TEXT,
        favorite_authors TEXT,
        reading_goals_per_month INTEGER DEFAULT 2,
        notification_preferences TEXT,
        privacy_settings TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (member_id) REFERENCES Member(member_id)
    )
    ''')
    
    conn.commit()
    print("✅ Enhanced library schema created successfully!")
    return conn

def populate_sample_books(conn):
    """Populate the database with realistic sample books"""
    
    print("📚 Adding sample books...")
    
    sample_books = [
        {
            'isbn': '9780134092669',
            'title': 'The Pragmatic Programmer: Your Journey to Mastery',
            'author': 'David Thomas, Andrew Hunt',
            'publisher': 'Addison-Wesley Professional',
            'publication_year': 2019,
            'genre': 'Technology',
            'pages': 352,
            'description': 'A guide to software craftsmanship and programming best practices.',
            'total_copies': 3,
            'available_copies': 2,
            'location': 'Computer Science - Shelf A1',
            'dewey_decimal': '004.6'
        },
        {
            'isbn': '9781492040347',
            'title': 'Designing Data-Intensive Applications',
            'author': 'Martin Kleppmann',
            'publisher': "O'Reilly Media",
            'publication_year': 2017,
            'genre': 'Technology',
            'pages': 616,
            'description': 'The big ideas behind reliable, scalable, and maintainable systems.',
            'total_copies': 2,
            'available_copies': 1,
            'location': 'Computer Science - Shelf A2',
            'dewey_decimal': '004.6'
        },
        {
            'isbn': '9780385537859',
            'title': 'The Martian',
            'author': 'Andy Weir',
            'publisher': 'Crown Publishers',
            'publication_year': 2014,
            'genre': 'Science Fiction',
            'pages': 369,
            'description': 'A stranded astronaut must survive on Mars using science and ingenuity.',
            'total_copies': 4,
            'available_copies': 3,
            'location': 'Fiction - Shelf F5',
            'dewey_decimal': '813.6'
        },
        {
            'isbn': '9780062315007',
            'title': 'The Alchemist',
            'author': 'Paulo Coelho',
            'publisher': 'HarperOne',
            'publication_year': 2014,
            'genre': 'Philosophy',
            'pages': 208,
            'description': 'A mystical story about following your dreams.',
            'total_copies': 5,
            'available_copies': 4,
            'location': 'Philosophy - Shelf P1',
            'dewey_decimal': '869.3'
        },
        {
            'isbn': '9780143127550',
            'title': 'Atomic Habits',
            'author': 'James Clear',
            'publisher': 'Avery',
            'publication_year': 2018,
            'genre': 'Self-Help',
            'pages': 320,
            'description': 'An easy and proven way to build good habits and break bad ones.',
            'total_copies': 3,
            'available_copies': 2,
            'location': 'Self-Help - Shelf S2',
            'dewey_decimal': '158.1'
        },
        {
            'isbn': '9780596009205',
            'title': 'Head First Design Patterns',
            'author': 'Eric Freeman, Elisabeth Robson',
            'publisher': "O'Reilly Media",
            'publication_year': 2004,
            'genre': 'Technology',
            'pages': 694,
            'description': 'A brain-friendly guide to software design patterns.',
            'total_copies': 2,
            'available_copies': 2,
            'location': 'Computer Science - Shelf A3',
            'dewey_decimal': '005.1'
        },
        {
            'isbn': '9780451524935',
            'title': '1984',
            'author': 'George Orwell',
            'publisher': 'Signet Classics',
            'publication_year': 1983,
            'genre': 'Dystopian Fiction',
            'pages': 328,
            'description': 'A dystopian social science fiction novel about totalitarianism.',
            'total_copies': 6,
            'available_copies': 5,
            'location': 'Classic Fiction - Shelf C1',
            'dewey_decimal': '823.912'
        },
        {
            'isbn': '9780525559474',
            'title': 'Becoming',
            'author': 'Michelle Obama',
            'publisher': 'Crown Publishing',
            'publication_year': 2018,
            'genre': 'Biography',
            'pages': 448,
            'description': 'A memoir by former First Lady Michelle Obama.',
            'total_copies': 4,
            'available_copies': 3,
            'location': 'Biography - Shelf B1',
            'dewey_decimal': '973.932'
        },
        {
            'isbn': '9780735219090',
            'title': 'Digital Minimalism',
            'author': 'Cal Newport',
            'publisher': 'Portfolio',
            'publication_year': 2019,
            'genre': 'Technology',
            'pages': 304,
            'description': 'Choosing a focused life in a noisy world.',
            'total_copies': 2,
            'available_copies': 1,
            'location': 'Self-Help - Shelf S1',
            'dewey_decimal': '302.23'
        },
        {
            'isbn': '9780593230572',
            'title': 'The Thursday Murder Club',
            'author': 'Richard Osman',
            'publisher': 'Pamela Dorman Books',
            'publication_year': 2020,
            'genre': 'Mystery',
            'pages': 384,
            'description': 'Four unlikely friends meet weekly to investigate cold cases.',
            'total_copies': 3,
            'available_copies': 2,
            'location': 'Mystery - Shelf M1',
            'dewey_decimal': '823.92'
        }
    ]
    
    cursor = conn.cursor()
    
    for book in sample_books:
        cursor.execute('''
        INSERT OR REPLACE INTO Library_Books 
        (isbn, title, author, publisher, publication_year, genre, pages, description, 
         total_copies, available_copies, location, dewey_decimal)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            book['isbn'], book['title'], book['author'], book['publisher'],
            book['publication_year'], book['genre'], book['pages'], book['description'],
            book['total_copies'], book['available_copies'], book['location'], book['dewey_decimal']
        ))
    
    conn.commit()
    print(f"✅ Added {len(sample_books)} sample books!")

def populate_sample_categories(conn):
    """Create book categories"""
    
    print("🏷️ Creating book categories...")
    
    categories = [
        ('Technology', 'Computer Science, Programming, and Technology books'),
        ('Fiction', 'Novels and fictional stories'),
        ('Science Fiction', 'Science fiction and fantasy novels'),
        ('Mystery', 'Mystery, thriller, and detective stories'),
        ('Biography', 'Biographies and autobiographies'),
        ('Self-Help', 'Personal development and self-improvement'),
        ('Philosophy', 'Philosophy and spiritual books'),
        ('Classic Fiction', 'Classic literature and timeless stories'),
        ('History', 'Historical books and events'),
        ('Science', 'Scientific texts and research')
    ]
    
    cursor = conn.cursor()
    
    for name, description in categories:
        cursor.execute('''
        INSERT OR REPLACE INTO Book_Categories (category_name, description)
        VALUES (?, ?)
        ''', (name, description))
    
    conn.commit()
    print(f"✅ Created {len(categories)} book categories!")

def create_sample_loans(conn):
    """Create some sample loan records"""
    
    print("📋 Creating sample loan records...")
    
    cursor = conn.cursor()
    
    # Get some book and member IDs
    books = cursor.execute('SELECT book_id FROM Library_Books LIMIT 5').fetchall()
    members = cursor.execute('SELECT member_id FROM Member LIMIT 3').fetchall()
    
    if not books or not members:
        print("⚠️ No books or members found, skipping loan creation")
        return
    
    # Create some active loans
    for i, (book_id,) in enumerate(books[:3]):
        member_id = members[i % len(members)][0]
        loan_date = datetime.now() - timedelta(days=random.randint(1, 14))
        due_date = loan_date + timedelta(days=21)  # 3 week loan period
        
        cursor.execute('''
        INSERT INTO Library_Loans 
        (book_id, member_id, loan_date, due_date, status)
        VALUES (?, ?, ?, ?, 'active')
        ''', (book_id, member_id, loan_date.date(), due_date.date()))
    
    # Create some completed loans
    for i, (book_id,) in enumerate(books[3:]):
        member_id = members[i % len(members)][0]
        loan_date = datetime.now() - timedelta(days=random.randint(30, 60))
        due_date = loan_date + timedelta(days=21)
        return_date = due_date - timedelta(days=random.randint(1, 5))
        
        cursor.execute('''
        INSERT INTO Library_Loans 
        (book_id, member_id, loan_date, due_date, return_date, status)
        VALUES (?, ?, ?, ?, ?, 'returned')
        ''', (book_id, member_id, loan_date.date(), due_date.date(), return_date.date()))
    
    conn.commit()
    print("✅ Created sample loan records!")

def main():
    """Main setup function"""
    print("🚀 Phase 5: Setting up Real Library Features Database")
    print("=" * 60)
    
    try:
        # Create enhanced schema
        conn = create_enhanced_library_schema()
        
        # Populate with sample data
        populate_sample_books(conn)
        populate_sample_categories(conn)
        create_sample_loans(conn)
        
        # Update available copies based on active loans
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE Library_Books 
        SET available_copies = total_copies - (
            SELECT COUNT(*) FROM Library_Loans 
            WHERE Library_Loans.book_id = Library_Books.book_id 
            AND status = 'active'
        )
        ''')
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 Phase 5 Database Setup Complete!")
        print("=" * 60)
        print("\n📊 What's New:")
        print("  ✅ Enhanced book catalog with real data")
        print("  ✅ Complete loan management system")
        print("  ✅ Book reviews and ratings")
        print("  ✅ Reservation system")
        print("  ✅ Fine management")
        print("  ✅ Library events system")
        print("  ✅ Member reading preferences")
        print("  ✅ Reading history tracking")
        print("\n🎯 Ready for Phase 5 API development!")
        
    except Exception as e:
        print(f"❌ Error setting up Phase 5 database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
