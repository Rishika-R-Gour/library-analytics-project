#!/usr/bin/env python3
"""
Minimal Fast Dashboard - No Dependencies on External APIs
Loads instantly, no waiting times
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime, timedelta
from scipy import stats

# Streamlit configuration for fastest loading
st.set_page_config(
    page_title="Fast Library Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"  # Faster loading
)

# Minimal CSS for speed
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
    .success-animation {
        animation: pulse 0.5s ease-in-out;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
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
    .book-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .action-button {
        background: linear-gradient(45deg, #00b894, #00cec9);
        border: none;
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,184,148,0.4);
    }
    .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Simple authentication (no API calls)
def simple_auth():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.markdown('<h1 class="main-header">⚡ Fast Library Dashboard</h1>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("💡 **Instant Access** - No API dependencies, loads in < 2 seconds!")
            
            with st.form("quick_login"):
                st.markdown("### Quick Login")
                role = st.selectbox("Select Role", ["Admin", "Librarian", "Member"])
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.form_submit_button("🚀 Login", type="primary"):
                        st.session_state.logged_in = True
                        st.session_state.user_role = role
                        st.success(f"✅ Logged in as {role}")
                        st.rerun()
                        
                with col_b:
                    if st.form_submit_button("👥 Demo Mode"):
                        st.session_state.logged_in = True
                        st.session_state.user_role = "Demo"
                        st.success("✅ Demo mode activated")
                        st.rerun()
        return False
    return True

def generate_sample_data():
    """Generate rich, realistic sample data"""
    np.random.seed(42)
    
    # Rich book catalog with real-looking data
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
        "Dr. Kevin Miller", "Amanda White", "Dr. Daniel Taylor",
        "Jessica Moore", "Dr. Ryan Clark", "Nicole Adams",
        "Dr. Brian Lewis", "Samantha Cooper"
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
    
    # Rich loan data
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
        'Due_Date': pd.date_range('2024-01-15', periods=50, freq='D'),
        'Rating_Given': np.random.choice([None, 4, 5, 3, 4, 5], 50, p=[0.3, 0.2, 0.3, 0.1, 0.05, 0.05])
    })
    
    return books, loans

def show_dashboard():
    """Enhanced dashboard with modern UI and advanced features"""
    user_role = st.session_state.get('user_role', 'Demo')
    
    # Enhanced Header with role badge
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.markdown(f'<h1 class="main-header">⚡ Smart Library System</h1>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="role-badge">🎭 {user_role} Portal</div>', unsafe_allow_html=True)
    with col3:
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.rerun()
    
    # Get enhanced data
    books_df, loans_df = generate_sample_data()
    
    # Enhanced metrics with modern styling
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📚 Total Books", len(books_df), delta="+12 this month")
    with col2:
        active_loans = len(loans_df[loans_df['Status'] == 'Active'])
        st.metric("📖 Active Loans", active_loans, delta=f"+{np.random.randint(5,15)} today")
    with col3:
        available = len(books_df[books_df['Available']])
        st.metric("✅ Available", available, delta=f"+{np.random.randint(2,8)} returned")
    with col4:
        overdue = len(loans_df[loans_df['Status'] == 'Overdue'])
        st.metric("⚠️ Overdue", overdue, delta=f"-{np.random.randint(1,5)} resolved")
    with col5:
        avg_rating = books_df['Rating'].mean()
        st.metric("⭐ Avg Rating", f"{avg_rating:.1f}/5.0", delta="+0.2 this month")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add real-time updates simulation
    current_time = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"🕒 **Live Dashboard** - Last updated: {current_time}")
    
    # Enhanced role-based navigation with icons and descriptions
    if user_role == "Admin":
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 Executive Dashboard", 
            "📚 Book Management", 
            "👥 User Administration", 
            "� Advanced Analytics",
            "⚙️ System Settings"
        ])
    elif user_role == "Librarian":
        tab1, tab2, tab3, tab4 = st.tabs([
            "� Today's Operations", 
            "📚 Collection Management", 
            "� Loan Processing",
            "📈 Performance Metrics"
        ])
    elif user_role == "Member":
        tab1, tab2, tab3 = st.tabs([
            "🏠 My Library Home", 
            "🔍 Discover Books", 
            "� My Account"
        ])
    else:  # Demo
        tab1, tab2, tab3, tab4 = st.tabs([
            "🌟 Feature Showcase", 
            "📚 Smart Catalog", 
            "� Live Analytics",
            "🚀 AI Features"
        ])
    
    # Enhanced Tab Content
    with tab1:
        if user_role == "Member":
            # Member Dashboard - Personalized Experience
            st.markdown("### 🏠 Welcome to Your Personal Library!")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("#### 📚 Recommended for You")
                recommended_books = books_df.nlargest(5, 'Rating')
                
                for _, book in recommended_books.iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div class="book-card">
                            <h4>📖 {book['Title']}</h4>
                            <p><strong>Author:</strong> {book['Author']} | <strong>Genre:</strong> {book['Genre']}</p>
                            <p>⭐ {book['Rating']}/5.0 | 📄 {book['Pages']} pages | 📅 {book['Year']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_a, col_b, col_c = st.columns([1, 1, 2])
                        with col_a:
                            if book['Available']:
                                if st.button(f"📖 Borrow", key=f"borrow_{book['ID']}"):
                                    st.success(f"✅ Reserved: {book['Title']}")
                                    st.balloons()
                        with col_b:
                            if st.button(f"💖 Wishlist", key=f"wish_{book['ID']}"):
                                st.info(f"💖 Added to wishlist!")
                        with col_c:
                            st.write(f"📊 Popularity: {book['Popularity']}/100")
            
            with col2:
                st.markdown("#### 📊 Your Reading Stats")
                st.markdown("""
                <div class="feature-card">
                    <h4>📈 This Month</h4>
                    <p>📚 Books Read: <strong>3</strong></p>
                    <p>⏱️ Reading Time: <strong>24 hours</strong></p>
                    <p>🎯 Goal Progress: <strong>75%</strong></p>
                    <p>🏆 Streak: <strong>12 days</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Quick actions
                st.markdown("#### ⚡ Quick Actions")
                if st.button("🔍 Advanced Search", key="adv_search"):
                    st.info("🔍 Advanced search filters activated!")
                if st.button("📱 Mobile App", key="mobile"):
                    st.info("� Download our mobile app!")
                if st.button("🤝 Book Club", key="club"):
                    st.info("🤝 Join our reading community!")
        
        elif user_role == "Admin":
            # Admin Executive Dashboard
            st.markdown("### 🎯 Executive Overview")
            
            # Key Performance Indicators
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="feature-card">
                    <h4>📊 System Health</h4>
                    <p>🟢 All systems operational</p>
                    <p>⚡ Response time: 0.2s</p>
                    <p>📈 Uptime: 99.9%</p>
                    <p>👥 Active users: 1,247</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="feature-card">
                    <h4>💰 Financial Metrics</h4>
                    <p>💵 Monthly Revenue: $12,450</p>
                    <p>📈 Growth: +15% vs last month</p>
                    <p>💳 Outstanding Fees: $2,340</p>
                    <p>🎯 Collection Rate: 94%</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="feature-card">
                    <h4>🚀 Innovation Metrics</h4>
                    <p>🤖 AI Recommendations: 89% accuracy</p>
                    <p>📱 Mobile Usage: 67%</p>
                    <p>⭐ User Satisfaction: 4.8/5</p>
                    <p>🔄 Feature Adoption: 78%</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Advanced visualizations
            col1, col2 = st.columns(2)
            with col1:
                # Enhanced genre analysis
                genre_data = books_df.groupby('Genre').agg({
                    'Rating': 'mean',
                    'Popularity': 'mean'
                }).reset_index()
                
                fig = px.scatter(genre_data, x='Rating', y='Popularity', 
                               size='Popularity', color='Genre',
                               title="📊 Genre Performance Matrix",
                               hover_data=['Genre'])
                fig.update_layout(showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Loan trends with forecasting
                daily_loans = loans_df.groupby('Date').size().reset_index(name='Loans')
                fig = px.line(daily_loans, x='Date', y='Loans',
                            title="📈 Daily Loan Trends with Forecast")
                
                # Add trend line
                from scipy import stats
                x_numeric = range(len(daily_loans))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, daily_loans['Loans'])
                daily_loans['Trend'] = [slope * x + intercept for x in x_numeric]
                fig.add_scatter(x=daily_loans['Date'], y=daily_loans['Trend'], 
                              mode='lines', name='Trend', line=dict(dash='dash'))
                
                st.plotly_chart(fig, use_container_width=True)
        
        else:  # Librarian, Demo, etc.
            # Enhanced overview for other roles
            col1, col2 = st.columns(2)
            
            with col1:
                # Interactive genre distribution
                genre_counts = books_df['Genre'].value_counts()
                fig = px.pie(values=genre_counts.values, names=genre_counts.index, 
                           title="📚 Collection Distribution",
                           hole=0.4,
                           color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Enhanced loan status with drill-down
                status_counts = loans_df['Status'].value_counts()
                colors = {'Active': '#74b9ff', 'Returned': '#00b894', 'Overdue': '#fd79a8'}
                fig = px.bar(x=status_counts.index, y=status_counts.values,
                           title="📊 Current Loan Status",
                           color=status_counts.index,
                           color_discrete_map=colors)
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            # Real-time activity feed
            st.markdown("### 📡 Live Activity Feed")
            activities = [
                "📚 'Python Crash Course' returned by Alice Johnson - 2 min ago",
                "📖 'Machine Learning Mastery' borrowed by Bob Smith - 5 min ago", 
                "⭐ 'Clean Code' rated 5 stars by Carol Davis - 8 min ago",
                "🔄 'Design Patterns' renewed by David Wilson - 12 min ago",
                "📱 Emma Brown joined the mobile app - 15 min ago"
            ]
            
            for activity in activities:
                st.markdown(f"• {activity}")
    # Enhanced Tab Content continues with tab2, tab3, etc.
    with tab2:
        if user_role == "Admin":
            st.markdown("### 📚 Advanced Book Management")
            
            # Admin book management with advanced features
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("➕ Add New Book", key="add_book"):
                    st.success("✅ New book form opened")
                    st.balloons()
            with col2:
                if st.button("📊 Bulk Operations", key="bulk_ops"):
                    st.info("📊 Bulk management tools activated")
            with col3:
                if st.button("🔍 Advanced Analytics", key="book_analytics"):
                    st.info("🔍 Deep book insights loading...")
            with col4:
                if st.button("📱 QR Code Generator", key="qr_gen"):
                    st.success("📱 QR codes generated for new books")
            
            # Enhanced search with filters
            col1, col2, col3 = st.columns(3)
            with col1:
                search = st.text_input("🔍 Search books...", placeholder="Title, author, or ISBN")
            with col2:
                genre_filter = st.selectbox("📚 Filter by Genre", ["All"] + books_df['Genre'].unique().tolist())
            with col3:
                year_filter = st.slider("📅 Publication Year", 2018, 2024, (2018, 2024))
            
            # Apply filters
            filtered_books = books_df.copy()
            if search:
                filtered_books = filtered_books[
                    filtered_books['Title'].str.contains(search, case=False) |
                    filtered_books['Author'].str.contains(search, case=False)
                ]
            if genre_filter != "All":
                filtered_books = filtered_books[filtered_books['Genre'] == genre_filter]
            
            filtered_books = filtered_books[
                (filtered_books['Year'] >= year_filter[0]) & 
                (filtered_books['Year'] <= year_filter[1])
            ]
            
            # Enhanced book display
            st.markdown(f"📊 **Showing {len(filtered_books)} of {len(books_df)} books**")
            
            for _, book in filtered_books.iterrows():
                with st.expander(f"📖 {book['Title']} - {book['Author']}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Genre:** {book['Genre']}")
                        st.write(f"**Year:** {book['Year']}")
                        st.write(f"**Pages:** {book['Pages']}")
                    with col2:
                        st.write(f"⭐ **Rating:** {book['Rating']}/5.0")
                        st.write(f"📊 **Popularity:** {book['Popularity']}/100")
                        status = "🟢 Available" if book['Available'] else "🔴 Checked Out"
                        st.write(f"**Status:** {status}")
                    with col3:
                        if st.button(f"✏️ Edit", key=f"edit_{book['ID']}"):
                            st.info(f"Editing {book['Title']}")
                        if st.button(f"📊 Analytics", key=f"analytics_{book['ID']}"):
                            st.success(f"Analytics for {book['Title']} loaded")
        
        elif user_role == "Member":
            st.markdown("### 🔍 Smart Book Discovery")
            
            # AI-powered recommendations
            st.markdown("#### 🤖 AI Recommendations Based on Your Reading History")
            
            # Simulated recommendation engine
            top_books = books_df.nlargest(8, 'Rating')
            
            col1, col2 = st.columns(2)
            for i, (_, book) in enumerate(top_books.iterrows()):
                with col1 if i % 2 == 0 else col2:
                    with st.container():
                        st.markdown(f"""
                        <div class="book-card">
                            <h4>📚 {book['Title']}</h4>
                            <p><strong>By:</strong> {book['Author']}</p>
                            <p><strong>Genre:</strong> {book['Genre']} | <strong>Year:</strong> {book['Year']}</p>
                            <p>⭐ {book['Rating']}/5.0 | 📄 {book['Pages']} pages</p>
                            <p>🔥 Popularity: {book['Popularity']}/100</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        btn_col1, btn_col2, btn_col3 = st.columns(3)
                        with btn_col1:
                            if book['Available']:
                                if st.button("📖 Borrow", key=f"borrow_disc_{book['ID']}"):
                                    st.success(f"✅ {book['Title']} reserved!")
                                    st.balloons()
                        with btn_col2:
                            if st.button("💖 Wishlist", key=f"wish_disc_{book['ID']}"):
                                st.info("💖 Added to wishlist!")
                        with btn_col3:
                            if st.button("👀 Preview", key=f"preview_{book['ID']}"):
                                st.info("👀 Opening book preview...")
    
    # Add more enhanced tabs based on user role
    if len([tab for tab in ['tab3', 'tab4', 'tab5'] if user_role == "Admin"]) > 0:
        with tab3:
            if user_role == "Admin":
                st.markdown("### 👥 Advanced User Management")
                
                # User statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("👥 Total Users", "1,247", delta="+23 this week")
                with col2:
                    st.metric("🆕 New Members", "45", delta="+12% vs last month")
                with col3:
                    st.metric("🏆 VIP Members", "89", delta="+5 upgraded")
                with col4:
                    st.metric("⚠️ Suspended", "3", delta="-2 resolved")
                
                # User management actions
                st.markdown("#### 🛠️ Administrative Actions")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("➕ Register New User", key="new_user"):
                        st.success("✅ User registration portal opened")
                with col2:
                    if st.button("📧 Send Bulk Notifications", key="bulk_notify"):
                        st.info("📧 Notification system activated")
                with col3:
                    if st.button("📊 Generate User Reports", key="user_reports"):
                        st.success("📊 Comprehensive user report generated")
                
                # Member type distribution
                member_types = ['Students', 'Faculty', 'Community', 'Staff', 'Senior Citizens']
                member_counts = [523, 234, 367, 123, 89]
                
                fig = go.Figure(data=[
                    go.Bar(x=member_types, y=member_counts, 
                          marker_color=['#74b9ff', '#00b894', '#fd79a8', '#fdcb6e', '#a29bfe'])
                ])
                fig.update_layout(
                    title="👥 Member Distribution by Type",
                    xaxis_title="Member Type",
                    yaxis_title="Number of Members"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Continue with remaining tabs...
    if user_role == "Admin":
        with tab4:
            st.markdown("### 📊 Advanced Analytics & Insights")
            
            # Performance dashboard
            col1, col2 = st.columns(2)
            
            with col1:
                # Book performance correlation
                fig = px.scatter(books_df, x='Rating', y='Popularity', 
                               size='Pages', color='Genre',
                               title="📈 Book Performance Analysis",
                               hover_data=['Title', 'Author'])
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Loan patterns
                loan_by_status = loans_df['Status'].value_counts()
                fig = px.pie(values=loan_by_status.values, names=loan_by_status.index,
                           title="📊 Loan Distribution",
                           hole=0.4,
                           color_discrete_sequence=['#74b9ff', '#00b894', '#fd79a8'])
                st.plotly_chart(fig, use_container_width=True)
            
            # Advanced metrics
            st.markdown("#### 🎯 Key Performance Indicators")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                avg_rating = books_df['Rating'].mean()
                st.metric("⭐ Avg Book Rating", f"{avg_rating:.2f}/5.0", delta="+0.15")
            with col2:
                popular_books = len(books_df[books_df['Popularity'] > 70])
                st.metric("🔥 Popular Books", popular_books, delta="+3")
            with col3:
                utilization = (len(books_df) - len(books_df[books_df['Available']])) / len(books_df) * 100
                st.metric("📊 Collection Utilization", f"{utilization:.1f}%", delta="+5.2%")
            with col4:
                member_satisfaction = 4.7
                st.metric("😊 Member Satisfaction", f"{member_satisfaction}/5.0", delta="+0.3")
        
        with tab5:
            st.markdown("### ⚙️ System Configuration & Settings")
            
            # System settings
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🔧 Library Configuration")
                loan_period = st.slider("📅 Default Loan Period (days)", 7, 30, 14)
                max_renewals = st.slider("🔄 Maximum Renewals", 1, 5, 2)
                late_fee = st.number_input("💰 Late Fee per Day ($)", 0.25, 5.0, 1.0, 0.25)
                
                if st.button("💾 Save Settings", key="save_settings"):
                    st.success("✅ Settings saved successfully!")
            
            with col2:
                st.markdown("#### 📊 System Status")
                st.markdown("""
                <div class="feature-card">
                    <h4>🖥️ System Health</h4>
                    <p>🟢 Database: Online</p>
                    <p>🟢 API Services: Operational</p>
                    <p>🟢 Backup: Current</p>
                    <p>🟡 Maintenance: Scheduled for Sunday</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🔄 System Backup", key="backup"):
                    st.success("🔄 Backup initiated successfully!")
                if st.button("📊 Generate System Report", key="sys_report"):
                    st.info("📊 System report being generated...")
    
    # Enhanced footer with role-specific information and real-time stats
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if user_role == "Admin":
            st.markdown("👑 **Administrator Portal** - Complete system oversight")
        elif user_role == "Librarian":
            st.markdown("📚 **Librarian Workspace** - Efficient operations management")
        elif user_role == "Member":
            st.markdown("📖 **Member Experience** - Personalized library journey")
        else:
            st.markdown("⚡ **Demo Experience** - Explore all features")
    
    with col2:
        st.markdown(f"🔄 **Auto-refresh** - Updates every 30 seconds")
    
    with col3:
        st.markdown(f"📊 **Performance** - Loading time < 2 seconds")
    
    with tab2:
        if user_role == "Admin":
            st.markdown("### 📚 Complete Book Catalog (Admin View)")
            
            # Admin controls
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("➕ Add New Book"):
                    st.success("✅ Book addition form would open here")
            with col2:
                if st.button("📝 Edit Selected"):
                    st.info("📝 Bulk edit mode activated")
            with col3:
                if st.button("🗑️ Remove Books"):
                    st.warning("⚠️ Deletion mode activated")
            
            # Search functionality
            search = st.text_input("🔍 Search books...")
            if search:
                filtered_books = books_df[books_df['Title'].str.contains(search, case=False) |
                                        books_df['Author'].str.contains(search, case=False)]
            else:
                filtered_books = books_df
            
            st.dataframe(filtered_books, use_container_width=True)
            
        elif user_role == "Librarian":
            st.markdown("### 📚 Book Management (Librarian View)")
            
            # Librarian controls
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Check In Books"):
                    st.success("✅ Check-in mode activated")
            with col2:
                if st.button("📤 Check Out Books"):
                    st.info("📤 Check-out mode activated")
            
            # Books needing attention
            st.markdown("#### 📋 Books Needing Attention")
            overdue_books = books_df[~books_df['Available']].head(5)
            st.dataframe(overdue_books, use_container_width=True)
            
        elif user_role == "Member":
            st.markdown("### 📖 My Loan History")
            
            # Member's loans (simulated)
            member_loans = loans_df.merge(books_df, left_on='Book_ID', right_on='ID', suffixes=('', '_book'))
            member_loans = member_loans[['Title', 'Status', 'Date']].head(8)
            
            for _, loan in member_loans.iterrows():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"📖 **{loan['Title']}**")
                with col2:
                    status_icon = "✅" if loan['Status'] == "Returned" else "📚" if loan['Status'] == "Active" else "⚠️"
                    st.write(f"{status_icon} {loan['Status']}")
                with col3:
                    if loan['Status'] == "Active":
                        if st.button("🔄 Renew", key=f"renew_{loan['Title']}"):
                            st.success("✅ Renewed successfully!")
        else:  # Demo
            st.markdown("### � Book Catalog")
            
            # Search functionality
            search = st.text_input("🔍 Search books...")
            if search:
                filtered_books = books_df[books_df['Title'].str.contains(search, case=False) |
                                        books_df['Author'].str.contains(search, case=False)]
            else:
                filtered_books = books_df
            
            st.dataframe(filtered_books, use_container_width=True)
    
    if user_role in ["Admin", "Librarian", "Demo"] and len(st.session_state.get('tabs', [])) > 2:
        with tab3:
            if user_role == "Admin":
                st.markdown("### 👥 Member Management (Admin Only)")
                
                # Member stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("👥 Total Members", "1,247")
                with col2:
                    st.metric("🆕 New This Month", "23")
                with col3:
                    st.metric("⚠️ Overdue Members", "8")
                
                # Member actions
                st.markdown("#### Admin Actions")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("➕ Add Member"):
                        st.success("✅ Member registration form opened")
                with col2:
                    if st.button("📧 Send Notifications"):
                        st.info("📧 Bulk notification system activated")
                with col3:
                    if st.button("📊 Generate Reports"):
                        st.success("📊 Report generation started")
                        
            elif user_role == "Librarian":
                st.markdown("### 📋 Daily Operations")
                
                # Today's tasks
                st.markdown("#### Today's Tasks")
                tasks = [
                    "📚 Process 15 returned books",
                    "📞 Call 3 members with overdue books", 
                    "📦 Receive new book shipment",
                    "🧹 Shelf organization - Fiction section"
                ]
                
                for i, task in enumerate(tasks):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(task)
                    with col2:
                        if st.button("✅ Done", key=f"task_{i}"):
                            st.success("Task completed!")
            else:  # Demo
                st.markdown("### �📈 Quick Analytics")
                
                # Loan trends
                loans_by_date = loans_df.groupby('Date').size().reset_index(name='Count')
                fig = px.line(loans_by_date, x='Date', y='Count', title="Daily Loans")
                st.plotly_chart(fig, use_container_width=True)
                
                # Recent activity
                st.markdown("#### Recent Loans")
                recent_loans = loans_df.merge(books_df, left_on='Book_ID', right_on='ID', suffixes=('', '_book'))
                recent_loans = recent_loans[['Title', 'Member', 'Status', 'Date']].sort_values('Date', ascending=False)
                st.dataframe(recent_loans.head(10), use_container_width=True)
    
    if user_role == "Admin" and len(st.session_state.get('tabs', [])) > 3:
        with tab4:
            st.markdown("### 📈 Advanced Admin Analytics")
            
            # Advanced metrics for admin
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 System Performance")
                performance_data = {
                    'Metric': ['Daily Logins', 'Books Circulated', 'Member Satisfaction', 'System Uptime'],
                    'Current': ['1,234', '456', '4.2/5', '99.8%'],
                    'Target': ['1,000', '400', '4.0/5', '99.0%'],
                    'Status': ['✅ Above', '✅ Above', '✅ Above', '✅ Above']
                }
                st.dataframe(pd.DataFrame(performance_data), use_container_width=True)
            
            with col2:
                st.markdown("#### 🔍 Member Analytics")
                member_types = ['Students', 'Faculty', 'Community', 'Staff']
                member_counts = [523, 234, 367, 123]
                fig = px.bar(x=member_types, y=member_counts, title="Members by Type")
                st.plotly_chart(fig, use_container_width=True)
    
    # Role-specific footer
    st.markdown("---")
    if user_role == "Admin":
        st.info("👑 **Admin Access** - Full system control • User management • Advanced analytics")
    elif user_role == "Librarian":
        st.info("📚 **Librarian Tools** - Book management • Loan operations • Daily tasks")
    elif user_role == "Member":
        st.info("📖 **Member Portal** - Browse books • Manage loans • Personal library")
    else:
        st.info("⚡ **Demo Mode** - Explore all features • No authentication required")

def main():
    if simple_auth():
        show_dashboard()

if __name__ == "__main__":
    main()
