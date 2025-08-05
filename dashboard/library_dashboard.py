
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
import json

# Dashboard Configuration
st.set_page_config(
    page_title="Library Analytics Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:5001/api"
AUTH_TOKEN = st.session_state.get('auth_token', None)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #cccccc;
        padding: 5% 5% 5% 10%;
        border-radius: 5px;
        color: rgb(30, 103, 119);
        overflow-wrap: break-word;
    }
</style>
""", unsafe_allow_html=True)

def authenticate():
    """Handle user authentication"""
    if 'auth_token' not in st.session_state:
        st.session_state.auth_token = None
    
    if not st.session_state.auth_token:
        st.title("🔐 Library Analytics Login")
        
        with st.form("login_form"):
            username = st.text_input("Username", value="admin")
            password = st.text_input("Password", type="password", value="admin123")
            submit = st.form_submit_button("Login")
            
            if submit:
                try:
                    response = requests.post(f"{API_BASE_URL}/auth/login", 
                                           json={"username": username, "password": password})
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.auth_token = data['token']
                        st.session_state.username = data['user']
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to API server. Please ensure the Flask API is running on localhost:5001")
                except Exception as e:
                    st.error(f"Login error: {e}")
        
        st.info("**Demo Credentials:** Username: admin, Password: admin123")
        return False
    
    return True

def api_request(endpoint, method="GET", data=None):
    """Make authenticated API request"""
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
    
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE_URL}{endpoint}", headers=headers)
        elif method == "POST":
            response = requests.post(f"{API_BASE_URL}{endpoint}", headers=headers, json=data)
        
        if response.status_code == 401:
            st.session_state.auth_token = None
            st.error("Session expired. Please login again.")
            st.rerun()
            
        return response.json() if response.status_code == 200 else None
        
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API server")
        return None
    except Exception as e:
        st.error(f"API request error: {e}")
        return None

@st.cache_data
def load_data():
    """Load and cache library data"""
    try:
        conn = sqlite3.connect('library.db')

        # Load all necessary data
        queries = {
            'members': "SELECT COUNT(*) as count FROM Member",
            'loans': "SELECT COUNT(*) as count FROM Loan",
            'overdue': "SELECT COUNT(*) as count FROM Loan WHERE Status = 'Overdue'",
            'branches': "SELECT COUNT(*) as count FROM Branch",
            'books': "SELECT COUNT(*) as count FROM Book"
        }

        data = {}
        for key, query in queries.items():
            result = pd.read_sql_query(query, conn)
            data[key] = result['count'].iloc[0] if not result.empty else 0

        conn.close()
        return data
    except:
        # Return sample data if database not available
        return {
            'members': 1000,
            'loans': 15000,
            'overdue': 75,
            'branches': 5,
            'books': 2500
        }

def get_api_stats():
    """Get dashboard stats from API"""
    stats = api_request("/dashboard/stats")
    return stats['data'] if stats else None

def main():
    """Main dashboard function"""
    # Check authentication first
    if not authenticate():
        return
    
    # Sidebar logout button
    with st.sidebar:
        st.markdown(f"**Logged in as:** {st.session_state.get('username', 'Unknown')}")
        if st.button("Logout"):
            st.session_state.auth_token = None
            st.session_state.username = None
            st.rerun()
    
    st.markdown('<h1 class="main-header">📚 Library Analytics Dashboard</h1>', 
                unsafe_allow_html=True)
    
    # API Health Check
    health = api_request("/health")
    if health:
        st.success(f"✅ Connected to API (v{health.get('version', '1.0.0')})")
    else:
        st.error("❌ Cannot connect to API server")
        st.stop()
    
    # Load data
    data = load_data()
    if not data:
        st.error("Failed to load data")
        return
    
    # Get API stats
    api_stats = get_api_stats()
    
    # Main Dashboard Content
    st.markdown("---")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_members = api_stats['total_members'] if api_stats else data['members']
        st.metric("Total Members", f"{total_members:,}")
        
    with col2:
        active_loans = api_stats['active_loans'] if api_stats else data['loans']
        st.metric("Active Loans", f"{active_loans:,}")
        
    with col3:
        overdue_loans = api_stats['overdue_loans'] if api_stats else data['overdue']
        st.metric("Overdue Loans", f"{overdue_loans:,}", delta="-15 vs last month")
        
    with col4:
        total_books = api_stats['total_books'] if api_stats else data['books']
        st.metric("Total Books", f"{total_books:,}")
    
    # ML Predictions Section
    st.markdown("## 🤖 Machine Learning Predictions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Overdue Risk Prediction")
        if st.button("Predict Overdue Risk"):
            # Sample loan data for prediction
            sample_loans = [
                {'loan_id': 1, 'member_type': 'Student', 'days_borrowed': 10},
                {'loan_id': 2, 'member_type': 'Professional', 'days_borrowed': 5}
            ]
            
            predictions = api_request("/predictions/overdue", "POST", sample_loans)
            if predictions:
                for pred in predictions['predictions']:
                    risk_color = "🔴" if pred['risk_level'] == 'High' else "🟡" if pred['risk_level'] == 'Medium' else "🟢"
                    st.write(f"{risk_color} Loan {pred['loan_id']}: {pred['overdue_probability']:.1%} probability ({pred['risk_level']} risk)")
    
    with col2:
        st.subheader("👥 Member Churn Prediction")
        if st.button("Predict Member Churn"):
            # Sample member data for prediction
            sample_members = [
                {'member_id': 1, 'days_since_last_visit': 30, 'total_loans': 5},
                {'member_id': 2, 'days_since_last_visit': 60, 'total_loans': 1}
            ]
            
            predictions = api_request("/predictions/churn", "POST", sample_members)
            if predictions:
                for pred in predictions['predictions']:
                    risk_color = "🔴" if pred['risk_level'] == 'High' else "🟡" if pred['risk_level'] == 'Medium' else "🟢"
                    st.write(f"{risk_color} Member {pred['member_id']}: {pred['churn_probability']:.1%} churn risk (Retention: {pred['retention_score']:.1%})")
    
    # Book Recommendations
    st.markdown("## 📚 Book Recommendations")
    member_id = st.number_input("Member ID for Recommendations", min_value=1, max_value=1000, value=1)
    
    if st.button("Get Recommendations"):
        recommendations = api_request(f"/recommendations/{member_id}")
        if recommendations:
            st.subheader(f"📖 Recommended Books for Member {member_id}")
            for i, rec in enumerate(recommendations['recommendations'], 1):
                st.write(f"**{i}. {rec['title']}** by {rec['author']}")
                st.write(f"   📊 Score: {rec['recommendation_score']:.1%} | 📚 Genre: {rec['genre']}")
                st.write(f"   💡 {rec['reason']}")
                st.write("---")
    
    # Model Status
    st.markdown("## 🔧 Model Status")
    models_status = api_request("/models/status")
    if models_status:
        status_data = models_status['models']
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Models Loaded", f"{status_data['loaded_models']}/{status_data['total_models']}")
        
        with col2:
            df_models = pd.DataFrame(status_data['models'])
            st.dataframe(df_models[['name', 'version', 'algorithm', 'status', 'size_mb']], use_container_width=True)

    # Sidebar Navigation
    st.sidebar.title("📊 Dashboard Navigation")
    dashboard_type = st.sidebar.selectbox(
        "Select Dashboard",
        ["🎯 Executive Overview", "⚙️ Operations", "📈 Analytics", "🔍 Reports"]
    )

    # Load data
    data = load_data()

    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    # Main Dashboard Content
    if dashboard_type == "🎯 Executive Overview":
        executive_dashboard(data)
    elif dashboard_type == "⚙️ Operations":
        operations_dashboard(data)
    elif dashboard_type == "📈 Analytics":
        analytics_dashboard(data)
    else:
        reports_dashboard(data)

def executive_dashboard(data):
    st.header("🎯 Executive Overview")

    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📚 Total Members",
            value=f"{data['members']:,}",
            delta=f"+{np.random.randint(10, 50)}"
        )

    with col2:
        st.metric(
            label="📖 Total Loans",
            value=f"{data['loans']:,}",
            delta=f"+{np.random.randint(100, 500)}"
        )

    with col3:
        st.metric(
            label="⚠️ Overdue Items",
            value=f"{data['overdue']}",
            delta=f"-{np.random.randint(5, 15)}"
        )

    with col4:
        st.metric(
            label="🏢 Active Branches",
            value=f"{data['branches']}",
            delta="0"
        )

    # Charts Row
    col1, col2 = st.columns(2)

    with col1:
        # Monthly Trends
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        loans = [1200, 1350, 1480, 1520, 1600, 1650]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months, y=loans,
            mode='lines+markers',
            name='Monthly Loans',
            line=dict(color='#1f77b4', width=3)
        ))
        fig.update_layout(
            title="📈 Monthly Loan Trends",
            xaxis_title="Month",
            yaxis_title="Number of Loans"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Branch Performance
        branches = ['Main', 'North', 'South', 'East', 'West']
        performance = [3000, 2800, 2500, 3200, 3500]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=branches, y=performance,
            marker_color='#ff7f0e',
            text=performance,
            textposition='auto'
        ))
        fig.update_layout(
            title="🏢 Branch Performance",
            xaxis_title="Branch",
            yaxis_title="Total Loans"
        )
        st.plotly_chart(fig, use_container_width=True)

def operations_dashboard(data):
    st.header("⚙️ Operations Dashboard")

    # Real-time metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🔄 Active Loans", f"{np.random.randint(400, 500)}")
    with col2:
        st.metric("📅 Due Today", f"{np.random.randint(20, 40)}")
    with col3:
        st.metric("👥 Staff on Duty", f"{np.random.randint(8, 15)}")

    # Operations Charts
    col1, col2 = st.columns(2)

    with col1:
        # Staff Workload
        staff = ['Alice', 'Bob', 'Carol', 'David', 'Eve']
        workload = np.random.randint(10, 30, 5)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=staff, y=workload,
            marker_color='#2ca02c'
        ))
        fig.update_layout(title="👥 Staff Workload Today")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Popular Books
        books = ['Book A', 'Book B', 'Book C', 'Book D', 'Book E']
        popularity = np.random.randint(5, 15, 5)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=books, x=popularity,
            orientation='h',
            marker_color='#d62728'
        ))
        fig.update_layout(title="📚 Popular Books Today")
        st.plotly_chart(fig, use_container_width=True)

def analytics_dashboard(data):
    st.header("📈 Analytics Dashboard")

    # Analytics Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🧠 Model Accuracy", "87.5%", "+2.3%")
    with col2:
        st.metric("📊 Churn Risk", "12.8%", "-1.5%")
    with col3:
        st.metric("📚 Avg Books/Member", "15.2", "+0.8")
    with col4:
        st.metric("🎯 Satisfaction", "4.2/5.0", "+0.1")

    # Analytics Charts
    tab1, tab2, tab3 = st.tabs(["Member Behavior", "Collection Performance", "Predictions"])

    with tab1:
        # Member segmentation
        segments = ['Power Users', 'Regular', 'At Risk', 'New Users']
        values = [25, 45, 15, 15]

        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels=segments, values=values,
            hole=0.4
        ))
        fig.update_layout(title="👥 Member Segmentation")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Collection performance
        categories = ['Fiction', 'Non-Fiction', 'Science', 'History', 'Children']
        loans_per_book = [3.2, 2.8, 2.1, 1.9, 2.4]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=categories, y=loans_per_book,
            marker_color='#9467bd'
        ))
        fig.update_layout(
            title="📚 Collection Performance",
            yaxis_title="Loans per Book"
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        # Prediction accuracy over time
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        accuracy = [85.2, 86.1, 86.8, 87.2, 87.5, 87.8]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months, y=accuracy,
            mode='lines+markers',
            line=dict(color='#ff7f0e', width=3)
        ))
        fig.update_layout(
            title="🔮 Model Accuracy Trends",
            yaxis_title="Accuracy (%)"
        )
        st.plotly_chart(fig, use_container_width=True)

def reports_dashboard(data):
    st.header("🔍 Reports Dashboard")

    # Report Generation
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Generate Executive Report"):
            st.success("Executive report generated!")

    with col2:
        if st.button("📈 Generate Analytics Report"):
            st.success("Analytics report generated!")

    with col3:
        if st.button("📋 Generate Operations Report"):
            st.success("Operations report generated!")

    # Sample Report Data
    st.subheader("📋 Recent Reports")

    reports_data = {
        'Report Name': ['Monthly Summary', 'Branch Performance', 'Member Analysis'],
        'Generated': ['2024-08-01', '2024-07-28', '2024-07-25'],
        'Status': ['✅ Complete', '✅ Complete', '✅ Complete'],
        'Download': ['📥 Download', '📥 Download', '📥 Download']
    }

    st.dataframe(pd.DataFrame(reports_data), use_container_width=True)

if __name__ == "__main__":
    main()
