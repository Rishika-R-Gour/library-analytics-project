#!/usr/bin/env python3
"""
Phase 3: Advanced User Management Database Setup
Creates tables for multi-role user system and advanced features
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime
import os

def hash_password(password):
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}:{pwd_hash.hex()}"

def setup_advanced_user_tables():
    """Create advanced user management tables"""
    
    # Connect to database
    db_path = os.path.join(os.path.dirname(__file__), 'notebooks', 'library.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create Roles table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS User_Roles (
        role_id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_name VARCHAR(50) UNIQUE NOT NULL,
        description TEXT,
        permissions TEXT, -- JSON string of permissions
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create Advanced Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Advanced_Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        role_id INTEGER,
        is_active BOOLEAN DEFAULT 1,
        last_login TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (role_id) REFERENCES User_Roles (role_id)
    )
    ''')
    
    # Create User Sessions table for session management
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS User_Sessions (
        session_id VARCHAR(255) PRIMARY KEY,
        user_id INTEGER,
        token_hash TEXT,
        expires_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES Advanced_Users (user_id)
    )
    ''')
    
    # Create User Activity Log
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS User_Activity_Log (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action VARCHAR(100),
        resource VARCHAR(100),
        details TEXT,
        ip_address VARCHAR(45),
        user_agent TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Advanced_Users (user_id)
    )
    ''')
    
    # Create Analytics Events table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Analytics_Events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type VARCHAR(100),
        event_name VARCHAR(100),
        user_id INTEGER,
        data TEXT, -- JSON string
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Advanced_Users (user_id)
    )
    ''')
    
    # Insert default roles
    roles_data = [
        ('admin', 'System Administrator', '["all"]'),
        ('librarian', 'Library Staff', '["read_all", "manage_books", "manage_loans", "view_reports"]'),
        ('member', 'Library Member', '["read_own", "borrow_books", "view_recommendations"]')
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO User_Roles (role_name, description, permissions)
    VALUES (?, ?, ?)
    ''', roles_data)
    
    # Create default admin user
    admin_password = hash_password('admin123')
    cursor.execute('''
    INSERT OR IGNORE INTO Advanced_Users 
    (username, email, password_hash, first_name, last_name, role_id)
    VALUES (?, ?, ?, ?, ?, 
        (SELECT role_id FROM User_Roles WHERE role_name = 'admin'))
    ''', ('admin', 'admin@library.com', admin_password, 'System', 'Administrator'))
    
    # Create demo librarian
    librarian_password = hash_password('librarian123')
    cursor.execute('''
    INSERT OR IGNORE INTO Advanced_Users 
    (username, email, password_hash, first_name, last_name, role_id)
    VALUES (?, ?, ?, ?, ?, 
        (SELECT role_id FROM User_Roles WHERE role_name = 'librarian'))
    ''', ('librarian', 'librarian@library.com', librarian_password, 'Jane', 'Smith'))
    
    # Create demo member
    member_password = hash_password('member123')
    cursor.execute('''
    INSERT OR IGNORE INTO Advanced_Users 
    (username, email, password_hash, first_name, last_name, role_id)
    VALUES (?, ?, ?, ?, ?, 
        (SELECT role_id FROM User_Roles WHERE role_name = 'member'))
    ''', ('member', 'member@library.com', member_password, 'John', 'Doe'))
    
    conn.commit()
    conn.close()
    
    print("✅ Advanced user management tables created successfully!")
    print("👥 Default users created:")
    print("   🔐 Admin: admin / admin123")
    print("   📚 Librarian: librarian / librarian123") 
    print("   👤 Member: member / member123")

if __name__ == "__main__":
    setup_advanced_user_tables()
