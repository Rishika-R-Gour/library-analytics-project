#!/usr/bin/env python3
"""
Streamlit Cloud Optimized Dashboard - Lightweight & Fast
Optimized for cloud deployment with minimal dependencies
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Streamlit configuration for fastest loading
st.set_page_config(
    page_title="Library Analytics Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS for professional look
st.markdown("""
<style>
    .main-header { 
        color: #1f77b4; 
        text-align: center; 
        font-size: 3rem;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem; 
        border-radius: 15px; 
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    .role-badge {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: bold;
        display: inline-block;
        margin: 1rem 0;
    }
    .feature-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .stats-container {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
    }
    .book-card {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #74b9ff;
        transition: transform 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

def simple_auth():
    """Simplified authentication for cloud deployment"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.markdown('<h1 class="main-header">📚 Library Analytics Dashboard</h1>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("🚀 **Cloud-Optimized Demo** - Instant loading, no API dependencies!")
            
            with st.form("quick_login"):
                st.markdown("### Select Your Role")
                role = st.selectbox("Choose Access Level", ["Demo User", "Librarian", "Admin", "Member"])
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.form_submit_button("🚀 Enter Dashboard", use_container_width=True):
                        st.session_state.logged_in = True
                        st.session_state.user_role = role
                        st.success(f"✅ Logged in as {role}")
                        st.rerun()
                        
                with col_b:
                    if st.form_submit_button("📖 Guest Access", use_container_width=True):
                        st.session_state.logged_in = True
                        st.session_state.user_role = "Guest"
                        st.success("✅ Guest access granted")
                        st.rerun()
        return False
    return True

def generate_sample_data():
    """Generate rich, realistic sample data optimized for cloud"""
    np.random.seed(42)
    
    # Rich book catalog
    book_titles = [
        "The Data Science Handbook", "Machine Learning Mastery", "Python Crash Course",
        "Clean Code", "Design Patterns", "The Pragmatic Programmer",
        "Algorithms Unleashed", "Database Systems", "Web Development Guide",
        "Artificial Intelligence", "Cloud Computing", "Cybersecurity Essentials",
        "Digital Marketing", "Project Management", "Leadership Principles",
        "Financial Analysis", "Business Strategy", "Innovation Theory",
        "Psychology Today", "History of Technology"
    ]
    
    authors = [
        "Dr. Sarah Johnson", "Prof. Michael Chen", "Dr. Emily Rodriguez",
        "James Wilson", "Dr. Lisa Park", "Robert Thompson",
        "Dr. Maria Garcia", "David Kim", "Dr. Jennifer Lee",
        "Alex Brown", "Dr. Christopher Davis", "Rachel Green"
    ]
    
    genres = ['Technology', 'Business', 'Science', 'Psychology', 'History', 'Management']
    
    books = pd.DataFrame({
        'ID': range(1, 21),
        'Title': book_titles,
        'Author': authors[:20],
        'Genre': np.random.choice(genres, 20),
        'Rating': np.round(np.random.uniform(3.5, 5.0, 20), 1),
        'Pages': np.random.randint(200, 800, 20),
        'Year': np.random.randint(2018, 2024, 20),
        'Available': np.random.choice([True, False], 20, p=[0.7, 0.3]),
        'Popularity': np.random.randint(1, 100, 20)
    })
    
    # Loan data
    member_names = [
        "Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Emma Brown",
        "Frank Miller", "Grace Lee", "Henry Taylor", "Ivy Chen", "Jack Rodriguez"
    ]
    
    loans = pd.DataFrame({
        'ID': range(1, 51),
        'Book_ID': np.random.randint(1, 21, 50),
        'Member': np.random.choice(member_names, 50),
        'Status': np.random.choice(['Active', 'Returned', 'Overdue'], 50, p=[0.3, 0.6, 0.1]),
        'Date': pd.date_range('2024-01-01', periods=50, freq='D'),
        'Due_Date': pd.date_range('2024-01-15', periods=50, freq='D')
    })
    
    return books, loans

def show_dashboard():
    """Cloud-optimized dashboard with enhanced features"""
    user_role = st.session_state.get('user_role', 'Demo User')
    
    # Header with role badge
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.markdown(f'<h1 class="main-header">📚 Smart Library System</h1>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="role-badge">🎭 {user_role} Portal</div>', unsafe_allow_html=True)
    with col3:
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.rerun()
    
    # Get data
    books_df, loans_df = generate_sample_data()
    
    # Key metrics
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📚 Total Books", len(books_df), delta="+12")
    with col2:
        active_loans = len(loans_df[loans_df['Status'] == 'Active'])
        st.metric("📖 Active Loans", active_loans, delta=f"+{np.random.randint(5,15)}")
    with col3:
        available = len(books_df[books_df['Available']])
        st.metric("✅ Available", available, delta=f"+{np.random.randint(2,8)}")
    with col4:
        overdue = len(loans_df[loans_df['Status'] == 'Overdue'])
        st.metric("⚠️ Overdue", overdue, delta=f"-{np.random.randint(1,5)}")
    with col5:
        avg_rating = books_df['Rating'].mean()
        st.metric("⭐ Avg Rating", f"{avg_rating:.1f}/5.0", delta="+0.2")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Real-time indicator
    current_time = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"🕒 **Live Dashboard** - Updated: {current_time} | 🌐 **Streamlit Cloud Deployment**")
    
    # Enhanced tabs based on role
    if user_role == "Admin":
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Executive Dashboard", 
            "📚 Book Management", 
            "👥 User Administration", 
            "📊 Advanced Analytics"
        ])
    elif user_role == "Librarian":
        tab1, tab2, tab3 = st.tabs([
            "📋 Daily Operations", 
            "📚 Collection Management", 
            "📈 Performance Metrics"
        ])
    elif user_role == "Member":
        tab1, tab2, tab3 = st.tabs([
            "🏠 My Library", 
            "🔍 Discover Books", 
            "📊 My Stats"
        ])
    else:  # Demo User, Guest
        tab1, tab2, tab3 = st.tabs([
            "🌟 Overview", 
            "📚 Book Catalog", 
            "📊 Analytics"
        ])
    
    # Tab content
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Genre distribution
            genre_counts = books_df['Genre'].value_counts()
            fig = px.pie(values=genre_counts.values, names=genre_counts.index, 
                       title="📚 Collection by Genre",
                       hole=0.4,
                       color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Loan status
            status_counts = loans_df['Status'].value_counts()
            colors = {'Active': '#74b9ff', 'Returned': '#00b894', 'Overdue': '#fd79a8'}
            fig = px.bar(x=status_counts.index, y=status_counts.values,
                       title="📊 Loan Status Distribution",
                       color=status_counts.index,
                       color_discrete_map=colors)
            st.plotly_chart(fig, use_container_width=True)
        
        # Activity feed
        st.markdown("### 📡 Recent Activity")
        activities = [
            "📚 'Python Crash Course' returned by Alice Johnson",
            "📖 'Machine Learning Mastery' borrowed by Bob Smith", 
            "⭐ 'Clean Code' rated 5 stars by Carol Davis",
            "🔄 'Design Patterns' renewed by David Wilson"
        ]
        
        for activity in activities:
            st.markdown(f"• {activity}")
    
    with tab2:
        st.markdown("### 📚 Book Catalog")
        
        # Search functionality
        col1, col2 = st.columns([2, 1])
        with col1:
            search = st.text_input("🔍 Search books...", placeholder="Title or author")
        with col2:
            genre_filter = st.selectbox("📚 Filter by Genre", ["All"] + list(books_df['Genre'].unique()))
        
        # Apply filters
        filtered_books = books_df.copy()
        if search:
            filtered_books = filtered_books[
                filtered_books['Title'].str.contains(search, case=False) |
                filtered_books['Author'].str.contains(search, case=False)
            ]
        if genre_filter != "All":
            filtered_books = filtered_books[filtered_books['Genre'] == genre_filter]
        
        st.markdown(f"📊 **Showing {len(filtered_books)} of {len(books_df)} books**")
        
        # Display books
        for _, book in filtered_books.head(10).iterrows():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                st.markdown(f"**{book['Title']}**")
                st.markdown(f"by {book['Author']}")
            with col2:
                st.markdown(f"📚 {book['Genre']}")
                st.markdown(f"📅 {book['Year']}")
            with col3:
                st.markdown(f"⭐ {book['Rating']}")
                st.markdown(f"📄 {book['Pages']} pages")
            with col4:
                if book['Available']:
                    st.success("✅ Available")
                else:
                    st.error("❌ On Loan")
    
    with tab3:
        st.markdown("### 📊 Analytics Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Rating distribution
            fig = px.histogram(books_df, x='Rating', nbins=10,
                             title="📊 Book Rating Distribution",
                             color_discrete_sequence=['#74b9ff'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Books by year
            year_counts = books_df['Year'].value_counts().sort_index()
            fig = px.line(x=year_counts.index, y=year_counts.values,
                        title="📈 Books Published by Year",
                        markers=True)
            fig.update_traces(line_color='#00b894')
            st.plotly_chart(fig, use_container_width=True)
        
        # Top performers
        st.markdown("### 🏆 Top Performing Books")
        top_books = books_df.nlargest(5, 'Rating')[['Title', 'Author', 'Rating', 'Genre']]
        st.dataframe(top_books, use_container_width=True)
    
    # Enhanced footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"🎭 **{user_role}** - Role-based access")
    with col2:
        st.markdown("🌐 **Streamlit Cloud** - Optimized deployment")
    with col3:
        st.markdown("⚡ **Performance** - < 2 second load time")

def main():
    """Main application entry point"""
    if simple_auth():
        show_dashboard()

if __name__ == "__main__":
    main()
