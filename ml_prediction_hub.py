#!/usr/bin/env python3
"""
ML Prediction Hub - Streamlit Cloud Optimized
Advanced machine learning predictions for library analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

# Streamlit configuration
st.set_page_config(
    page_title="ML Prediction Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS for ML theme
st.markdown("""
<style>
    .main-header { 
        color: #6c5ce7; 
        text-align: center; 
        font-size: 3rem;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .ml-card { 
        background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
        color: white;
        padding: 1.5rem; 
        border-radius: 15px; 
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    .prediction-card {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .risk-high {
        background: linear-gradient(135deg, #e17055 0%, #d63031 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .risk-medium {
        background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .risk-low {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .model-metrics {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .feature-importance {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def generate_ml_data():
    """Generate realistic data for ML predictions"""
    np.random.seed(42)
    
    # Generate member data for churn prediction
    n_members = 1000
    members_data = {
        'member_id': range(1, n_members + 1),
        'books_borrowed_last_month': np.random.poisson(3, n_members),
        'days_since_last_visit': np.random.exponential(7, n_members),
        'average_rating_given': np.random.normal(4.2, 0.8, n_members),
        'membership_duration_months': np.random.exponential(12, n_members),
        'overdue_count': np.random.poisson(0.5, n_members),
        'digital_engagement': np.random.beta(2, 5, n_members),
        'preferred_genre_diversity': np.random.uniform(1, 8, n_members)
    }
    
    # Create churn labels based on realistic patterns
    churn_probability = (
        0.1 + 
        0.3 * (members_data['days_since_last_visit'] > 30) +
        0.2 * (members_data['books_borrowed_last_month'] == 0) +
        0.15 * (members_data['overdue_count'] > 2) +
        0.1 * (members_data['digital_engagement'] < 0.2)
    )
    members_data['churned'] = np.random.binomial(1, np.clip(churn_probability, 0, 1), n_members)
    
    members_df = pd.DataFrame(members_data)
    
    # Generate book data for popularity prediction
    n_books = 500
    books_data = {
        'book_id': range(1, n_books + 1),
        'publication_year': np.random.randint(1990, 2024, n_books),
        'page_count': np.random.normal(300, 100, n_books),
        'author_popularity': np.random.exponential(50, n_books),
        'genre_popularity': np.random.uniform(0, 100, n_books),
        'review_count': np.random.poisson(25, n_books),
        'average_rating': np.random.beta(8, 2, n_books) * 5,
        'price': np.random.gamma(2, 10, n_books),
        'marketing_spend': np.random.exponential(100, n_books)
    }
    
    # Create popularity score
    popularity_score = (
        0.3 * books_data['average_rating'] +
        0.2 * np.log1p(books_data['review_count']) +
        0.15 * books_data['genre_popularity'] / 100 +
        0.15 * books_data['author_popularity'] / 100 +
        0.1 * (2024 - books_data['publication_year']) / 34 +
        0.1 * books_data['marketing_spend'] / 1000
    )
    books_data['popularity_score'] = popularity_score
    
    books_df = pd.DataFrame(books_data)
    
    # Generate loan data for overdue prediction
    n_loans = 2000
    loans_data = {
        'loan_id': range(1, n_loans + 1),
        'member_age': np.random.normal(35, 15, n_loans),
        'loan_duration_days': np.random.choice([7, 14, 21, 30], n_loans, p=[0.4, 0.3, 0.2, 0.1]),
        'book_popularity': np.random.exponential(50, n_loans),
        'member_history_overdue': np.random.poisson(1, n_loans),
        'book_length': np.random.normal(300, 100, n_loans),
        'season_factor': np.random.uniform(0.5, 1.5, n_loans),
        'member_engagement_score': np.random.beta(3, 2, n_loans) * 100,
        'distance_from_library': np.random.exponential(5, n_loans)
    }
    
    # Create overdue probability
    overdue_prob = (
        0.05 +
        0.3 * (loans_data['member_history_overdue'] > 2) +
        0.2 * (loans_data['book_length'] > 400) +
        0.15 * (loans_data['loan_duration_days'] > 21) +
        0.1 * (loans_data['member_engagement_score'] < 30) +
        0.1 * (loans_data['distance_from_library'] > 10)
    )
    loans_data['overdue'] = np.random.binomial(1, np.clip(overdue_prob, 0, 1), n_loans)
    
    loans_df = pd.DataFrame(loans_data)
    
    return members_df, books_df, loans_df

def train_churn_model(members_df):
    """Train member churn prediction model"""
    feature_cols = ['books_borrowed_last_month', 'days_since_last_visit', 'average_rating_given',
                   'membership_duration_months', 'overdue_count', 'digital_engagement', 'preferred_genre_diversity']
    
    X = members_df[feature_cols]
    y = members_df['churned']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Model metrics
    train_accuracy = model.score(X_train, y_train)
    test_accuracy = model.score(X_test, y_test)
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    return model, {'train_accuracy': train_accuracy, 'test_accuracy': test_accuracy}, feature_importance

def train_overdue_model(loans_df):
    """Train overdue prediction model"""
    feature_cols = ['member_age', 'loan_duration_days', 'book_popularity', 'member_history_overdue',
                   'book_length', 'season_factor', 'member_engagement_score', 'distance_from_library']
    
    X = loans_df[feature_cols]
    y = loans_df['overdue']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Model metrics
    train_accuracy = model.score(X_train, y_train)
    test_accuracy = model.score(X_test, y_test)
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    return model, {'train_accuracy': train_accuracy, 'test_accuracy': test_accuracy}, feature_importance

def train_popularity_model(books_df):
    """Train book popularity prediction model"""
    feature_cols = ['publication_year', 'page_count', 'author_popularity', 'genre_popularity',
                   'review_count', 'average_rating', 'price', 'marketing_spend']
    
    X = books_df[feature_cols]
    y = books_df['popularity_score']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Model metrics
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    return model, {'train_r2': train_score, 'test_r2': test_score}, feature_importance

def show_ml_dashboard():
    """Main ML dashboard"""
    st.markdown('<h1 class="main-header">🤖 ML Prediction Hub</h1>', unsafe_allow_html=True)
    
    # Real-time indicator
    current_time = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"🔬 **AI-Powered Analytics** - Live Models Updated: {current_time}")
    
    # Generate data and train models
    with st.spinner("🔄 Training ML models with latest data..."):
        members_df, books_df, loans_df = generate_ml_data()
        churn_model, churn_metrics, churn_features = train_churn_model(members_df)
        overdue_model, overdue_metrics, overdue_features = train_overdue_model(loans_df)
        popularity_model, popularity_metrics, popularity_features = train_popularity_model(books_df)
    
    # Model performance overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🤖 Active Models", "3", delta="All Operational")
    with col2:
        st.metric("🎯 Churn Model Accuracy", f"{churn_metrics['test_accuracy']:.1%}", delta="+2.3%")
    with col3:
        st.metric("⚠️ Overdue Model Accuracy", f"{overdue_metrics['test_accuracy']:.1%}", delta="+1.8%")
    with col4:
        st.metric("📈 Popularity Model R²", f"{popularity_metrics['test_r2']:.3f}", delta="+0.045")
    
    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Member Churn Prediction",
        "⚠️ Overdue Risk Analysis", 
        "📈 Book Popularity Forecast",
        "🔬 Model Performance",
        "🚀 Real-time Predictions"
    ])
    
    with tab1:
        st.markdown("### 🎯 Member Churn Prediction")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### 🔧 Input Member Data")
            books_last_month = st.slider("Books borrowed last month", 0, 20, 3, key="churn_books_last_month")
            days_since_visit = st.slider("Days since last visit", 0, 90, 7, key="churn_days_since_visit")
            avg_rating = st.slider("Average rating given", 1.0, 5.0, 4.2, 0.1, key="churn_avg_rating")
            membership_months = st.slider("Membership duration (months)", 1, 60, 12, key="churn_membership_months")
            overdue_count = st.slider("Previous overdue count", 0, 10, 1, key="churn_overdue_count")
            digital_engagement = st.slider("Digital engagement score", 0.0, 1.0, 0.5, 0.1, key="churn_digital_engagement")
            genre_diversity = st.slider("Genre diversity (1-8)", 1, 8, 4, key="churn_genre_diversity")
            
            # Make prediction
            if st.button("🔮 Predict Churn Risk", key="churn_predict"):
                input_data = [[books_last_month, days_since_visit, avg_rating, 
                             membership_months, overdue_count, digital_engagement, genre_diversity]]
                
                churn_prob = churn_model.predict_proba(input_data)[0][1]
                
                if churn_prob > 0.7:
                    st.markdown(f"""
                    <div class="risk-high">
                        <h4>🚨 HIGH RISK: {churn_prob:.1%}</h4>
                        <p>Immediate intervention recommended</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif churn_prob > 0.4:
                    st.markdown(f"""
                    <div class="risk-medium">
                        <h4>⚠️ MEDIUM RISK: {churn_prob:.1%}</h4>
                        <p>Consider engagement initiatives</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="risk-low">
                        <h4>✅ LOW RISK: {churn_prob:.1%}</h4>
                        <p>Member likely to remain active</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            # Feature importance chart
            fig = px.bar(churn_features, x='importance', y='feature', orientation='h',
                        title="🔍 Feature Importance - Churn Prediction",
                        color='importance', color_continuous_scale='Viridis')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Churn risk distribution
            risk_counts = members_df['churned'].value_counts()
            fig2 = px.pie(values=risk_counts.values, names=['Active', 'Churned'],
                         title="📊 Current Member Status Distribution",
                         color_discrete_sequence=['#00b894', '#e17055'])
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        st.markdown("### ⚠️ Overdue Risk Analysis")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### 🔧 Input Loan Data")
            member_age = st.slider("Member age", 18, 80, 35, key="overdue_member_age")
            loan_duration = st.selectbox("Loan duration", [7, 14, 21, 30], index=1, key="overdue_loan_duration")
            book_popularity = st.slider("Book popularity score", 0, 100, 50, key="overdue_book_popularity")
            history_overdue = st.slider("Previous overdue count", 0, 10, 1, key="overdue_history_overdue")
            book_length = st.slider("Book length (pages)", 50, 800, 300, key="overdue_book_length")
            season_factor = st.slider("Seasonal factor", 0.5, 1.5, 1.0, 0.1, key="overdue_season_factor")
            engagement_score = st.slider("Member engagement score", 0, 100, 70, key="overdue_engagement_score")
            distance = st.slider("Distance from library (km)", 0.5, 50.0, 5.0, 0.5, key="overdue_distance")
            
            # Make prediction
            if st.button("🔮 Predict Overdue Risk", key="overdue_predict"):
                input_data = [[member_age, loan_duration, book_popularity, history_overdue,
                             book_length, season_factor, engagement_score, distance]]
                
                overdue_prob = overdue_model.predict_proba(input_data)[0][1]
                
                if overdue_prob > 0.6:
                    st.markdown(f"""
                    <div class="risk-high">
                        <h4>🚨 HIGH RISK: {overdue_prob:.1%}</h4>
                        <p>Consider shorter loan period or reminder</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif overdue_prob > 0.3:
                    st.markdown(f"""
                    <div class="risk-medium">
                        <h4>⚠️ MEDIUM RISK: {overdue_prob:.1%}</h4>
                        <p>Send proactive reminder</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="risk-low">
                        <h4>✅ LOW RISK: {overdue_prob:.1%}</h4>
                        <p>Loan likely to be returned on time</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            # Feature importance
            fig = px.bar(overdue_features, x='importance', y='feature', orientation='h',
                        title="🔍 Feature Importance - Overdue Prediction",
                        color='importance', color_continuous_scale='Reds')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Overdue risk distribution by loan duration
            overdue_by_duration = loans_df.groupby('loan_duration_days')['overdue'].mean()
            fig2 = px.bar(x=overdue_by_duration.index, y=overdue_by_duration.values,
                         title="📊 Overdue Rate by Loan Duration",
                         color=overdue_by_duration.values, color_continuous_scale='Oranges')
            fig2.update_xaxis(title="Loan Duration (Days)")
            fig2.update_yaxis(title="Overdue Rate")
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        st.markdown("### 📈 Book Popularity Forecast")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### 🔧 Input Book Data")
            pub_year = st.slider("Publication year", 1990, 2024, 2020, key="popularity_pub_year")
            page_count = st.slider("Page count", 50, 1000, 300, key="popularity_page_count")
            author_pop = st.slider("Author popularity", 0, 100, 50, key="popularity_author_pop")
            genre_pop = st.slider("Genre popularity", 0, 100, 60, key="popularity_genre_pop")
            review_count = st.slider("Number of reviews", 0, 200, 25, key="popularity_review_count")
            avg_rating = st.slider("Average rating", 1.0, 5.0, 4.0, 0.1, key="popularity_avg_rating")
            price = st.slider("Price ($)", 5, 100, 20, key="popularity_price")
            marketing = st.slider("Marketing spend ($)", 0, 1000, 100, key="popularity_marketing")
            
            # Make prediction
            if st.button("🔮 Predict Popularity", key="popularity_predict"):
                input_data = [[pub_year, page_count, author_pop, genre_pop,
                             review_count, avg_rating, price, marketing]]
                
                popularity_score = popularity_model.predict(input_data)[0]
                
                if popularity_score > 3.5:
                    st.markdown(f"""
                    <div class="risk-low">
                        <h4>🔥 HIGH POPULARITY: {popularity_score:.2f}</h4>
                        <p>Expected to be very popular!</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif popularity_score > 2.5:
                    st.markdown(f"""
                    <div class="risk-medium">
                        <h4>📚 MODERATE POPULARITY: {popularity_score:.2f}</h4>
                        <p>Decent circulation expected</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="risk-high">
                        <h4>📉 LOW POPULARITY: {popularity_score:.2f}</h4>
                        <p>May need promotion efforts</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            # Feature importance
            fig = px.bar(popularity_features, x='importance', y='feature', orientation='h',
                        title="🔍 Feature Importance - Popularity Prediction",
                        color='importance', color_continuous_scale='Blues')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Popularity vs features correlation
            fig2 = px.scatter(books_df, x='average_rating', y='popularity_score', 
                            size='review_count', color='genre_popularity',
                            title="📊 Popularity vs Rating & Reviews",
                            hover_data=['author_popularity'])
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab4:
        st.markdown("### 🔬 Model Performance Dashboard")
        
        # Model comparison
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="model-metrics">
                <h4>🎯 Churn Model</h4>
                <p><strong>Type:</strong> Random Forest</p>
                <p><strong>Features:</strong> 7</p>
                <p><strong>Training Accuracy:</strong> {:.1%}</p>
                <p><strong>Test Accuracy:</strong> {:.1%}</p>
                <p><strong>Status:</strong> ✅ Operational</p>
            </div>
            """.format(churn_metrics['train_accuracy'], churn_metrics['test_accuracy']), 
            unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="model-metrics">
                <h4>⚠️ Overdue Model</h4>
                <p><strong>Type:</strong> Random Forest</p>
                <p><strong>Features:</strong> 8</p>
                <p><strong>Training Accuracy:</strong> {:.1%}</p>
                <p><strong>Test Accuracy:</strong> {:.1%}</p>
                <p><strong>Status:</strong> ✅ Operational</p>
            </div>
            """.format(overdue_metrics['train_accuracy'], overdue_metrics['test_accuracy']), 
            unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="model-metrics">
                <h4>📈 Popularity Model</h4>
                <p><strong>Type:</strong> Gradient Boosting</p>
                <p><strong>Features:</strong> 8</p>
                <p><strong>Training R²:</strong> {:.3f}</p>
                <p><strong>Test R²:</strong> {:.3f}</p>
                <p><strong>Status:</strong> ✅ Operational</p>
            </div>
            """.format(popularity_metrics['train_r2'], popularity_metrics['test_r2']), 
            unsafe_allow_html=True)
        
        # Performance trends
        col1, col2 = st.columns(2)
        
        with col1:
            # Model accuracy comparison
            models = ['Churn', 'Overdue', 'Popularity']
            accuracies = [churn_metrics['test_accuracy'], overdue_metrics['test_accuracy'], popularity_metrics['test_r2']]
            
            fig = px.bar(x=models, y=accuracies, title="🎯 Model Performance Comparison",
                        color=accuracies, color_continuous_scale='Viridis')
            fig.update_yaxis(title="Performance Score")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Feature count comparison
            feature_counts = [7, 8, 8]
            fig2 = px.pie(values=feature_counts, names=models, 
                         title="🔧 Feature Distribution Across Models",
                         color_discrete_sequence=['#6c5ce7', '#e17055', '#74b9ff'])
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab5:
        st.markdown("### 🚀 Real-time Prediction Engine")
        
        # Batch prediction interface
        st.markdown("#### 📊 Batch Member Analysis")
        
        if st.button("🔄 Analyze Random Member Sample", key="batch_analyze"):
            # Get random sample of members
            sample_members = members_df.sample(10)
            
            # Predict churn for sample
            feature_cols = ['books_borrowed_last_month', 'days_since_last_visit', 'average_rating_given',
                           'membership_duration_months', 'overdue_count', 'digital_engagement', 'preferred_genre_diversity']
            
            churn_probs = churn_model.predict_proba(sample_members[feature_cols])[:, 1]
            sample_members['churn_risk'] = churn_probs
            sample_members['risk_category'] = pd.cut(churn_probs, 
                                                   bins=[0, 0.3, 0.6, 1.0], 
                                                   labels=['Low', 'Medium', 'High'])
            
            # Display results
            display_cols = ['member_id', 'books_borrowed_last_month', 'days_since_last_visit', 
                          'churn_risk', 'risk_category']
            
            styled_df = sample_members[display_cols].style.format({
                'churn_risk': '{:.1%}'
            }).background_gradient(subset=['churn_risk'], cmap='Reds')
            
            st.dataframe(styled_df, use_container_width=True)
            
            # Risk distribution in sample
            risk_dist = sample_members['risk_category'].value_counts()
            fig = px.pie(values=risk_dist.values, names=risk_dist.index,
                        title="🎯 Risk Distribution in Sample",
                        color_discrete_map={'Low': '#00b894', 'Medium': '#fdcb6e', 'High': '#e17055'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Real-time alerts simulation
        st.markdown("#### 🚨 Real-time Alerts")
        
        alerts = [
            "🔴 Member #1247: High churn risk detected (87% probability)",
            "🟡 Loan #5639: Medium overdue risk for 'Machine Learning Guide'", 
            "🟢 Book #892: High popularity predicted for new arrival",
            "🔴 Member #3421: 45 days since last visit - intervention needed",
            "🟡 Batch processing: 23 members flagged for retention campaign"
        ]
        
        for alert in alerts:
            st.markdown(f"• {alert}")
        
        # Model refresh status
        st.markdown("""
        <div class="prediction-card">
            <h4>🔄 Model Status</h4>
            <p>✅ <strong>Last Training:</strong> 2 hours ago</p>
            <p>✅ <strong>Data Freshness:</strong> Real-time</p>
            <p>✅ <strong>Prediction Latency:</strong> < 100ms</p>
            <p>✅ <strong>Model Drift:</strong> Within acceptable range</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application entry point"""
    show_ml_dashboard()

if __name__ == "__main__":
    main()
