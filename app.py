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
        "Alex Brown", "Dr. Christopher Davis", "Rachel Green",
        "Dr. Michael Smith", "Prof. Lisa Wang", "Dr. John Anderson",
        "Maria Rodriguez", "David Brown", "Dr. Emily Chen",
        "Prof. Sarah Davis", "Dr. Mark Wilson"
    ]
    
    genres = ['Technology', 'Business', 'Science', 'Psychology', 'History', 'Management']
    
    books = pd.DataFrame({
        'ID': range(1, 21),
        'Title': book_titles,
        'Author': authors,
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
    
    # Tab content with role-based differentiation
    with tab1:
        if user_role == "Admin":
            st.markdown("### 🎯 Executive Dashboard - Administrative Overview")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div class="feature-card">
                    <h4>📊 System Performance</h4>
                    <p>🟢 All systems operational</p>
                    <p>⚡ Response time: 0.2s</p>
                    <p>📈 Uptime: 99.9%</p>
                    <p>👥 Active users: 1,247</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="feature-card">
                    <h4>💰 Financial Overview</h4>
                    <p>💵 Monthly Revenue: $12,450</p>
                    <p>📈 Growth: +15%</p>
                    <p>💳 Outstanding: $2,340</p>
                    <p>🎯 Collection Rate: 94%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="feature-card">
                    <h4>🚀 Innovation Metrics</h4>
                    <p>🤖 AI Accuracy: 89%</p>
                    <p>📱 Mobile Usage: 67%</p>
                    <p>⭐ Satisfaction: 4.8/5</p>
                    <p>🔄 Adoption: 78%</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Admin-specific charts
            col1, col2 = st.columns(2)
            with col1:
                # User growth chart
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
                users = [1200, 1180, 1350, 1400, 1380, 1247]
                fig = px.line(x=months, y=users, title="👥 User Growth Trend", markers=True)
                fig.update_traces(line_color='#74b9ff')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Revenue chart
                revenue = [11500, 10800, 12200, 13100, 12800, 12450]
                fig = px.bar(x=months, y=revenue, title="💰 Monthly Revenue", color=revenue)
                st.plotly_chart(fig, use_container_width=True)
        
        elif user_role == "Librarian":
            st.markdown("### 📋 Today's Operations - Librarian Dashboard")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 📋 Today's Tasks")
                tasks = [
                    "📚 Process 12 new book arrivals",
                    "🔄 Handle 8 book returns", 
                    "📞 Follow up on 3 overdue items",
                    "📋 Inventory check: Science section",
                    "👥 Assist 15+ member queries"
                ]
                for task in tasks:
                    st.markdown(f"• {task}")
            
            with col2:
                st.markdown("#### ⚠️ Priority Items")
                st.error("🚨 3 books overdue by 2+ weeks")
                st.warning("⚠️ 5 popular books need restocking")
                st.info("📘 New arrivals need cataloging")
                st.success("✅ Monthly report ready for review")
            
            # Librarian workload chart
            work_types = ['Book Processing', 'Member Assistance', 'Maintenance', 'Admin Tasks']
            hours = [4, 3, 2, 1]
            fig = px.pie(values=hours, names=work_types, title="⏰ Daily Time Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        elif user_role == "Member":
            st.markdown("### 🏠 Welcome to Your Personal Library!")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("#### 📚 Recommended for You")
                recommended = books_df.nlargest(3, 'Rating')
                for _, book in recommended.iterrows():
                    with st.container():
                        col_a, col_b, col_c = st.columns([2, 1, 1])
                        with col_a:
                            st.markdown(f"**{book['Title']}**")
                            st.markdown(f"by {book['Author']}")
                        with col_b:
                            st.markdown(f"⭐ {book['Rating']}")
                        with col_c:
                            if st.button("📖 Borrow", key=f"borrow_{book['ID']}"):
                                st.success("Added to your wishlist!")
            
            with col2:
                st.markdown("#### 📊 Your Reading Stats")
                st.markdown("""
                <div class="feature-card">
                    <h4>📈 This Month</h4>
                    <p>📚 Books Read: <strong>3</strong></p>
                    <p>⏱️ Reading Time: <strong>24h</strong></p>
                    <p>🎯 Goal Progress: <strong>75%</strong></p>
                    <p>🏆 Reading Streak: <strong>12 days</strong></p>
                </div>
                """, unsafe_allow_html=True)
        
        else:  # Demo User, Guest
            st.markdown("### 🌟 Library Overview - Demo Mode")
            
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
            
            # Demo features
            st.markdown("### 🎯 Available Features")
            feature_cols = st.columns(4)
            with feature_cols[0]:
                st.info("� **Admin**: Full system control")
            with feature_cols[1]:
                st.info("📚 **Librarian**: Daily operations")
            with feature_cols[2]:
                st.info("📖 **Member**: Personal library")
            with feature_cols[3]:
                st.info("🌟 **Demo**: Explore features")
    
    with tab2:
        if user_role == "Admin":
            st.markdown("### 📚 Advanced Book Management - Admin Controls")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("➕ Add New Book", key="admin_add"):
                    st.success("✅ New book form opened")
            with col2:
                if st.button("📊 Bulk Operations", key="admin_bulk"):
                    st.info("📋 Bulk operations panel ready")
            with col3:
                if st.button("🔍 Advanced Search", key="admin_search"):
                    st.info("🔍 Advanced search enabled")
            with col4:
                if st.button("📱 Generate QR Codes", key="admin_qr"):
                    st.success("📱 QR codes generated")
            
            # Admin book table with all data
            st.markdown("#### 📋 Complete Book Database")
            st.dataframe(books_df, use_container_width=True)
            
            # Admin analytics
            col1, col2 = st.columns(2)
            with col1:
                avg_pages = books_df['Pages'].mean()
                st.metric("📄 Average Pages", f"{avg_pages:.0f}", delta="+12 vs last month")
            with col2:
                popular_genre = books_df['Genre'].mode()[0]
                st.metric("🔥 Most Popular Genre", popular_genre, delta="Technology leading")
        
        elif user_role == "Librarian":
            st.markdown("### 📚 Collection Management - Librarian Tools")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📋 Check In Books", key="lib_checkin"):
                    st.success("📋 Check-in mode activated")
            with col2:
                if st.button("📤 Check Out Books", key="lib_checkout"):
                    st.success("📤 Check-out mode activated")
            with col3:
                if st.button("🔍 Find Book", key="lib_find"):
                    st.info("🔍 Book search opened")
            
            # Books needing attention
            st.markdown("#### 📋 Books Requiring Attention")
            attention_books = books_df[~books_df['Available']].head(5)
            for _, book in attention_books.iterrows():
                col_a, col_b, col_c = st.columns([2, 1, 1])
                with col_a:
                    st.markdown(f"📖 **{book['Title']}** by {book['Author']}")
                with col_b:
                    st.markdown(f"📚 {book['Genre']}")
                with col_c:
                    if st.button("🔄 Follow Up", key=f"followup_{book['ID']}"):
                        st.success("📞 Follow-up scheduled")
        
        elif user_role == "Member":
            st.markdown("### 🔍 Discover Amazing Books")
            
            # Search and filter
            col1, col2 = st.columns([2, 1])
            with col1:
                search_term = st.text_input("🔍 Search books...", placeholder="Title, author, or genre")
            with col2:
                genre_filter = st.selectbox("📚 Filter by genre", ["All"] + list(books_df['Genre'].unique()))
            
            # Filter books
            filtered_books = books_df.copy()
            if search_term:
                filtered_books = filtered_books[
                    filtered_books['Title'].str.contains(search_term, case=False) |
                    filtered_books['Author'].str.contains(search_term, case=False)
                ]
            if genre_filter != "All":
                filtered_books = filtered_books[filtered_books['Genre'] == genre_filter]
            
            # Display filtered books
            st.markdown(f"📊 Found {len(filtered_books)} books")
            for _, book in filtered_books.head(8).iterrows():
                with st.container():
                    col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])
                    with col_a:
                        st.markdown(f"**{book['Title']}** by {book['Author']}")
                    with col_b:
                        st.markdown(f"⭐ {book['Rating']}")
                    with col_c:
                        st.markdown(f"📚 {book['Genre']}")
                    with col_d:
                        if book['Available']:
                            if st.button("� Borrow", key=f"borrow_tab2_{book['ID']}"):
                                st.success("📚 Added to cart!")
                        else:
                            st.markdown("❌ Unavailable")
        
        else:  # Demo User, Guest
            st.markdown("### 📚 Explore Our Collection")
            
            # Search functionality for demo
            search = st.text_input("🔍 Search books...", placeholder="Try searching for 'Python' or 'Data'")
            
            if search:
                filtered_books = books_df[
                    books_df['Title'].str.contains(search, case=False) |
                    books_df['Author'].str.contains(search, case=False)
                ]
                st.markdown(f"� Found {len(filtered_books)} matches")
            else:
                filtered_books = books_df.head(10)
                st.markdown("📊 Showing top 10 books")
            
            # Display books in card format
            for i in range(0, len(filtered_books), 2):
                col1, col2 = st.columns(2)
                for j, col in enumerate([col1, col2]):
                    if i + j < len(filtered_books):
                        book = filtered_books.iloc[i + j]
                        with col:
                            st.markdown(f"""
                            <div class="book-card">
                                <h4>📖 {book['Title']}</h4>
                                <p><strong>Author:</strong> {book['Author']}</p>
                                <p><strong>Genre:</strong> {book['Genre']} | <strong>Rating:</strong> ⭐ {book['Rating']}</p>
                                <p><strong>Pages:</strong> {book['Pages']} | <strong>Year:</strong> {book['Year']}</p>
                            </div>
                            """, unsafe_allow_html=True)
    
    with tab3:
        if user_role == "Admin":
            st.markdown("### 👥 User Administration - Advanced Management")
            
            # User statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("👥 Total Members", "1,247", delta="+23 this week")
            with col2:
                st.metric("📚 Active Borrowers", "892", delta="+15 today")
            with col3:
                st.metric("⭐ Premium Members", "156", delta="+8 this month")
            with col4:
                st.metric("🚨 Suspended", "3", delta="-2 resolved")
            
            # Admin actions
            st.markdown("#### 🛠️ Administrative Actions")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("👤 Add New Member", key="admin_add_member"):
                    st.success("👤 New member registration form opened")
            with col2:
                if st.button("� Send Notifications", key="admin_notify"):
                    st.info("📧 Notification system activated")
            with col3:
                if st.button("�📊 Generate Report", key="admin_report"):
                    st.success("📊 Comprehensive report generated")
            
            # Member analytics
            member_types = ['Students', 'Faculty', 'Community', 'Staff', 'Seniors']
            member_counts = [523, 234, 367, 123, 89]
            fig = px.bar(x=member_types, y=member_counts, 
                        title="👥 Member Distribution by Type",
                        color=member_counts,
                        color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
        
        elif user_role == "Librarian":
            st.markdown("### 📈 Performance Metrics - Daily & Weekly Stats")
            
            # Daily metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📚 Books Processed Today", "28", delta="+5 vs yesterday")
            with col2:
                st.metric("👥 Members Helped", "47", delta="+12 vs yesterday")
            with col3:
                st.metric("⭐ Average Service Rating", "4.8", delta="+0.2")
            
            # Weekly performance chart
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            checkouts = [23, 34, 28, 31, 29, 15, 8]
            returns = [18, 25, 31, 27, 33, 12, 6]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Checkouts', x=days, y=checkouts, marker_color='#74b9ff'))
            fig.add_trace(go.Bar(name='Returns', x=days, y=returns, marker_color='#00b894'))
            fig.update_layout(title='📊 Weekly Activity Overview', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance goals
            st.markdown("#### 🎯 Performance Goals")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Daily Targets:**")
                st.progress(0.85, text="Books Processed: 85% (28/33)")
                st.progress(0.94, text="Member Assistance: 94% (47/50)")
                st.progress(0.76, text="Inventory Updates: 76% (38/50)")
            with col2:
                st.markdown("**Weekly Goals:**")
                st.success("✅ Customer Satisfaction > 4.5")
                st.success("✅ Response Time < 5 minutes")
                st.warning("⚠️ Overdue Follow-ups: 3 pending")
        
        elif user_role == "Member":
            st.markdown("### 📊 My Reading Statistics & Achievements")
            
            # Personal stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📚 Books This Year", "27", delta="+3 this month")
            with col2:
                st.metric("⏱️ Reading Hours", "156", delta="+12 this week")
            with col3:
                st.metric("🏆 Reading Streak", "18 days", delta="+1 day")
            
            # Reading progress
            st.markdown("#### 📈 Reading Progress")
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            books_read = [3, 5, 4, 6, 5, 4]
            fig = px.line(x=months, y=books_read, title="📚 Books Read This Year", 
                         markers=True, line_shape='spline')
            fig.update_traces(line_color='#00b894', marker_color='#74b9ff')
            st.plotly_chart(fig, use_container_width=True)
            
            # Achievements
            st.markdown("#### 🏆 Your Achievements")
            achievements = [
                "🥉 Bronze Reader - Read 10+ books",
                "📚 Genre Explorer - Read 5+ different genres", 
                "⭐ Quality Reader - Average rating given: 4.6",
                "🔥 Consistent Reader - 18-day reading streak"
            ]
            for achievement in achievements:
                st.success(achievement)
            
            # Reading goals
            st.markdown("#### 🎯 2024 Reading Goals")
            st.progress(0.68, text="Annual Goal: 68% (27/40 books)")
            st.progress(0.52, text="Genre Challenge: 52% (13/25 genres)")
            st.progress(0.75, text="Review Goal: 75% (18/24 reviews)")
        
        else:  # Demo User, Guest
            st.markdown("### 📊 Library Analytics Dashboard")
            
            col1, col2 = st.columns(2)
            with col1:
                # Book ratings distribution
                fig = px.histogram(books_df, x='Rating', nbins=10,
                                 title="📊 Book Rating Distribution",
                                 color_discrete_sequence=['#74b9ff'])
                fig.update_layout(xaxis_title="Rating", yaxis_title="Number of Books")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Books by publication year
                year_counts = books_df['Year'].value_counts().sort_index()
                fig = px.bar(x=year_counts.index, y=year_counts.values,
                           title="📈 Books by Publication Year",
                           color=year_counts.values,
                           color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
            
            # Top performers
            st.markdown("### 🏆 Top Performing Books")
            top_books = books_df.nlargest(5, 'Rating')[['Title', 'Author', 'Rating', 'Genre', 'Year']]
            
            for i, (_, book) in enumerate(top_books.iterrows(), 1):
                col_a, col_b, col_c = st.columns([1, 3, 1])
                with col_a:
                    if i == 1:
                        st.markdown("🥇")
                    elif i == 2:
                        st.markdown("🥈")
                    elif i == 3:
                        st.markdown("🥉")
                    else:
                        st.markdown(f"#{i}")
                with col_b:
                    st.markdown(f"**{book['Title']}** by {book['Author']}")
                with col_c:
                    st.markdown(f"⭐ {book['Rating']}")
    
    # Add fourth tab for Admin users
    if user_role == "Admin":
        with tab4:
            st.markdown("### 📊 Advanced Analytics & Business Intelligence")
            
            # Advanced metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                collection_value = books_df['Pages'].sum() * 0.15  # Estimate value
                st.metric("💰 Collection Value", f"${collection_value:,.0f}", delta="+$2,340")
            with col2:
                utilization = ((len(books_df) - len(books_df[books_df['Available']])) / len(books_df)) * 100
                st.metric("📊 Utilization Rate", f"{utilization:.1f}%", delta="+5.2%")
            with col3:
                popular_books = len(books_df[books_df['Popularity'] > 70])
                st.metric("🔥 Popular Titles", popular_books, delta="+3")
            with col4:
                member_satisfaction = 4.7
                st.metric("😊 Satisfaction Score", f"{member_satisfaction}/5.0", delta="+0.3")
            
            # Advanced visualizations
            col1, col2 = st.columns(2)
            with col1:
                # Book performance correlation
                fig = px.scatter(books_df, x='Rating', y='Popularity', 
                               size='Pages', color='Genre',
                               title="📈 Book Performance Analysis",
                               hover_data=['Title', 'Author'])
                fig.update_layout(showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Predictive analytics
                future_months = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                current_loans = [15, 18, 22, 19, 24, 16]
                predicted_loans = [26, 28, 30, 25, 32, 20]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], 
                                       y=current_loans, mode='lines+markers', 
                                       name='Historical', line=dict(color='#74b9ff')))
                fig.add_trace(go.Scatter(x=future_months, y=predicted_loans, 
                                       mode='lines+markers', name='Predicted', 
                                       line=dict(color='#fd79a8', dash='dash')))
                fig.update_layout(title='🔮 Loan Volume Prediction')
                st.plotly_chart(fig, use_container_width=True)
            
            # System insights
            st.markdown("#### 🧠 AI-Powered Insights")
            insights = [
                "📈 **Growth Opportunity**: Technology books show 23% higher engagement",
                "🎯 **Recommendation**: Increase Science fiction collection by 15%",
                "⚠️ **Alert**: History section underutilized - consider promotion campaign",
                "🔥 **Trend**: Mobile app usage increased 45% this quarter"
            ]
            for insight in insights:
                st.info(insight)
    
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
