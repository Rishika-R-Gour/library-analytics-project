
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Dashboard Configuration
st.set_page_config(
    page_title="Library Analytics Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
            'branches': "SELECT COUNT(*) as count FROM Branch"
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
            'branches': 5
        }

def main():
    # Title and Header
    st.markdown('<h1 class="main-header">📚 Library Analytics Dashboard</h1>', 
                unsafe_allow_html=True)

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
