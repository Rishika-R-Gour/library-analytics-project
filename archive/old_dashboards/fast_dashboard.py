#!/usr/bin/env python3
"""
Optimized Advanced Library Analytics Dashboard - No API Dependencies
Fast, offline authentication with instant login
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sqlite3
import hashlib

# Dashboard Configuration
st.set_page_config(
    page_title="Advanced Library Analytics",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Offline user database (no API needed)
USERS_DB = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "first_name": "Admin",
        "last_name": "User",
        "permissions": ["all"]
    },
    "librarian": {
        "password": "lib123", 
        "role": "librarian",
        "first_name": "Library",
        "last_name": "Staff",
        "permissions": ["library_management", "reports"]
    },
    "member": {
        "password": "member123",
        "role": "member", 
        "first_name": "Library",
        "last_name": "Member",
        "permissions": ["basic_access"]
    }
}

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .role-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    .admin-badge { background-color: #dc3545; color: white; }
    .librarian-badge { background-color: #28a745; color: white; }
    .member-badge { background-color: #007bff; color: white; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        margin: 0.5rem;
    }
    .success-login {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def authenticate():
    """Fast offline authentication - no API calls"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown('<h1 class="main-header">🚀 Library Analytics System</h1>', unsafe_allow_html=True)
        
        # Quick login tabs
        tab1, tab2, tab3 = st.tabs(["👤 Admin Login", "📚 Librarian Login", "👥 Member Login"])
        
        with tab1:
            st.markdown("### Admin Access")
            with st.form("admin_login"):
                username = st.text_input("Username", value="admin", key="admin_user")
                password = st.text_input("Password", type="password", value="admin123", key="admin_pass")
                if st.form_submit_button("🚀 Login as Admin", type="primary"):
                    fast_login(username, password)
        
        with tab2:
            st.markdown("### Librarian Access") 
            with st.form("librarian_login"):
                username = st.text_input("Username", value="librarian", key="lib_user")
                password = st.text_input("Password", type="password", value="lib123", key="lib_pass")
                if st.form_submit_button("📚 Login as Librarian", type="primary"):
                    fast_login(username, password)
        
        with tab3:
            st.markdown("### Member Access")
            with st.form("member_login"):
                username = st.text_input("Username", value="member", key="mem_user") 
                password = st.text_input("Password", type="password", value="member123", key="mem_pass")
                if st.form_submit_button("👥 Login as Member", type="primary"):
                    fast_login(username, password)
        
        # Quick access info
        st.info("💡 **Quick Access**: Use the pre-filled credentials or try admin/admin123, librarian/lib123, or member/member123")
        return False
    
    return True

def fast_login(username, password):
    """Instant offline login - no waiting!"""
    if username in USERS_DB and USERS_DB[username]["password"] == password:
        user = USERS_DB[username]
        st.session_state.authenticated = True
        st.session_state.user_info = {
            "username": username,
            "role": user["role"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "permissions": user["permissions"]
        }
        st.success(f"✅ Welcome {user['first_name']} {user['last_name']}! Logged in as {user['role'].title()}")
        st.rerun()
    else:
        st.error("❌ Invalid credentials")

def get_sample_data():
    """Generate sample library data"""
    np.random.seed(42)
    
    # Sample books data
    books_data = {
        'Book_ID': range(1, 101),
        'Title': [f'Book Title {i}' for i in range(1, 101)],
        'Author': [f'Author {np.random.randint(1, 20)}' for _ in range(100)],
        'Genre': np.random.choice(['Fiction', 'Non-Fiction', 'Science', 'History', 'Biography'], 100),
        'Publication_Year': np.random.randint(1990, 2024, 100),
        'Copies_Available': np.random.randint(1, 10, 100)
    }
    
    # Sample members data
    members_data = {
        'Member_ID': range(1, 51),
        'Name': [f'Member {i}' for i in range(1, 51)],
        'Email': [f'member{i}@library.com' for i in range(1, 51)],
        'Join_Date': pd.date_range('2020-01-01', periods=50, freq='W'),
        'Status': np.random.choice(['Active', 'Inactive'], 50, p=[0.8, 0.2])
    }
    
    # Sample loans data
    loans_data = {
        'Loan_ID': range(1, 201),
        'Member_ID': np.random.randint(1, 51, 200),
        'Book_ID': np.random.randint(1, 101, 200),
        'Loan_Date': pd.date_range('2024-01-01', periods=200, freq='D'),
        'Due_Date': pd.date_range('2024-01-15', periods=200, freq='D'),
        'Status': np.random.choice(['Active', 'Returned', 'Overdue'], 200, p=[0.3, 0.6, 0.1])
    }
    
    return pd.DataFrame(books_data), pd.DataFrame(members_data), pd.DataFrame(loans_data)

def show_main_dashboard():
    """Main dashboard with role-based content"""
    user = st.session_state.user_info
    
    # Header with user info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f'<h1 class="main-header">📚 Library Analytics Dashboard</h1>', unsafe_allow_html=True)
    with col2:
        role_class = f"{user['role']}-badge"
        st.markdown(f'<span class="role-badge {role_class}">{user["role"].title()}</span>', unsafe_allow_html=True)
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown(f"Welcome back, **{user['first_name']} {user['last_name']}**!")
    
    # Get sample data
    books_df, members_df, loans_df = get_sample_data()
    
    # Role-based tabs
    if user['role'] == 'admin':
        tabs = st.tabs(["📊 Overview", "👥 User Management", "📚 Library Stats", "🤖 Churn Prediction", "⚙️ System"])
    elif user['role'] == 'librarian':
        tabs = st.tabs(["📊 Overview", "📚 Library Management", "📈 Reports", "🤖 Churn Prediction"])
    else:  # member
        tabs = st.tabs(["📊 My Dashboard", "🔍 Search Books", "📖 My Loans"])
    
    # Overview tab (all roles)
    with tabs[0]:
        show_overview_stats(books_df, members_df, loans_df, user['role'])
    
    # Role-specific tabs
    if user['role'] == 'admin':
        with tabs[1]:
            show_user_management()
        with tabs[2]:
            show_library_stats(books_df, members_df, loans_df)
        with tabs[3]:
            show_churn_prediction()
        with tabs[4]:
            show_system_management()
            
    elif user['role'] == 'librarian':
        with tabs[1]:
            show_library_management(books_df, loans_df)
        with tabs[2]:
            show_reports(books_df, members_df, loans_df)
        with tabs[3]:
            show_churn_prediction()
            
    else:  # member
        with tabs[1]:
            show_book_search(books_df)
        with tabs[2]:
            show_member_loans(loans_df, books_df)

def show_overview_stats(books_df, members_df, loans_df, role):
    """Show overview statistics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total Books", len(books_df))
    with col2:
        st.metric("👥 Total Members", len(members_df))
    with col3:
        active_loans = len(loans_df[loans_df['Status'] == 'Active'])
        st.metric("📖 Active Loans", active_loans)
    with col4:
        overdue_loans = len(loans_df[loans_df['Status'] == 'Overdue'])
        st.metric("⚠️ Overdue", overdue_loans)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Genre distribution
        genre_counts = books_df['Genre'].value_counts()
        fig = px.pie(values=genre_counts.values, names=genre_counts.index, 
                    title="📚 Books by Genre")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Loan status
        status_counts = loans_df['Status'].value_counts()
        fig = px.bar(x=status_counts.index, y=status_counts.values,
                    title="📊 Loan Status Distribution")
        st.plotly_chart(fig, use_container_width=True)

def show_churn_prediction():
    """Show churn prediction analysis"""
    st.markdown("### 🤖 Member Churn Prediction")
    
    # Sample churn data
    np.random.seed(42)
    churn_data = {
        'Member_ID': range(1, 51),
        'Risk_Score': np.random.uniform(0, 1, 50),
        'Last_Activity': pd.date_range('2024-01-01', periods=50, freq='D'),
        'Books_Borrowed': np.random.randint(0, 20, 50)
    }
    df = pd.DataFrame(churn_data)
    df['Risk_Level'] = pd.cut(df['Risk_Score'], bins=[0, 0.3, 0.7, 1.0], 
                             labels=['Low', 'Medium', 'High'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        high_risk = len(df[df['Risk_Level'] == 'High'])
        st.metric("🔴 High Risk Members", high_risk)
    with col2:
        medium_risk = len(df[df['Risk_Level'] == 'Medium'])
        st.metric("🟡 Medium Risk Members", medium_risk)
    with col3:
        low_risk = len(df[df['Risk_Level'] == 'Low'])
        st.metric("🟢 Low Risk Members", low_risk)
    
    # Risk distribution chart
    risk_counts = df['Risk_Level'].value_counts()
    fig = px.bar(x=risk_counts.index, y=risk_counts.values,
                title="Member Churn Risk Distribution",
                color=risk_counts.index,
                color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed risk table
    st.markdown("#### Member Risk Details")
    st.dataframe(df.sort_values('Risk_Score', ascending=False))

def show_user_management():
    """Admin-only user management"""
    st.markdown("### 👥 User Management")
    
    # User stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Users", len(USERS_DB))
    with col2:
        st.metric("Active Sessions", 1)
    with col3:
        st.metric("Admin Users", 1)
    
    # User list
    st.markdown("#### Current Users")
    user_data = []
    for username, data in USERS_DB.items():
        user_data.append({
            'Username': username,
            'Role': data['role'].title(),
            'Name': f"{data['first_name']} {data['last_name']}"
        })
    
    st.dataframe(pd.DataFrame(user_data))

def show_library_stats(books_df, members_df, loans_df):
    """Detailed library statistics"""
    st.markdown("### 📚 Library Statistics")
    
    # Advanced metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Books by publication year
        year_counts = books_df['Publication_Year'].value_counts().sort_index()
        fig = px.line(x=year_counts.index, y=year_counts.values,
                     title="Books by Publication Year")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Member join trends
        members_df['Join_Month'] = members_df['Join_Date'].dt.to_period('M')
        month_counts = members_df['Join_Month'].value_counts().sort_index()
        fig = px.bar(x=[str(x) for x in month_counts.index], y=month_counts.values,
                    title="Member Registrations by Month")
        st.plotly_chart(fig, use_container_width=True)

def show_library_management(books_df, loans_df):
    """Library management for librarians"""
    st.markdown("### 📚 Library Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📖 Book Inventory")
        st.dataframe(books_df.head(10))
    
    with col2:
        st.markdown("#### 📋 Recent Loans")
        recent_loans = loans_df.sort_values('Loan_Date', ascending=False).head(10)
        st.dataframe(recent_loans)

def show_reports(books_df, members_df, loans_df):
    """Reports for librarians"""
    st.markdown("### 📈 Library Reports")
    
    # Popular books
    loan_counts = loans_df['Book_ID'].value_counts().head(10)
    popular_books = books_df[books_df['Book_ID'].isin(loan_counts.index)]
    
    st.markdown("#### 🏆 Most Popular Books")
    st.dataframe(popular_books[['Title', 'Author', 'Genre']])
    
    # Member activity
    member_activity = loans_df['Member_ID'].value_counts().head(10)
    st.markdown("#### 👑 Most Active Members")
    fig = px.bar(x=member_activity.index, y=member_activity.values,
                title="Loans by Member")
    st.plotly_chart(fig, use_container_width=True)

def show_book_search(books_df):
    """Book search for members"""
    st.markdown("### 🔍 Search Books")
    
    search_term = st.text_input("Search by title, author, or genre:")
    
    if search_term:
        mask = (books_df['Title'].str.contains(search_term, case=False) |
                books_df['Author'].str.contains(search_term, case=False) |
                books_df['Genre'].str.contains(search_term, case=False))
        results = books_df[mask]
        st.dataframe(results)
    else:
        st.dataframe(books_df.head(20))

def show_member_loans(loans_df, books_df):
    """Member loan history"""
    st.markdown("### 📖 My Loans")
    
    # Simulate current user's loans
    user_loans = loans_df.head(10)
    loan_details = user_loans.merge(books_df, on='Book_ID')
    
    st.dataframe(loan_details[['Title', 'Author', 'Loan_Date', 'Due_Date', 'Status']])

def show_system_management():
    """System management for admins"""
    st.markdown("### ⚙️ System Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🖥️ System Status")
        st.success("✅ Dashboard: Online")
        st.success("✅ Database: Connected")
        st.info("ℹ️ API Services: Offline (Not Required)")
    
    with col2:
        st.markdown("#### 📊 Performance")
        st.metric("Response Time", "< 1s")
        st.metric("Active Users", "1")
        st.metric("System Load", "Low")

# Main execution
def main():
    if authenticate():
        show_main_dashboard()

if __name__ == "__main__":
    main()
