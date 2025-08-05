# 📚 Library Analytics Project - Clean Architecture

A professional library management ecosystem with role-based dashboards, interactive analytics, and AI-powered predictions.

## 🌐 **Live Demo**
🔗 **[Library Analytics Dashboard](https://a4sbmlac2wrrnjlahpyaqv.streamlit.app/)** - Role-based dashboards with interactive analytics

🤖 **[ML Prediction Hub](https://mlpredictionapppy-97ovakrjjxaenevmrrjp89.streamlit.app/)** - Advanced machine learning predictions & analytics

> **🎯 Complete System**: Features role-based dashboards (Admin, Librarian, Member) with interactive analytics, book management, real-time visualizations, and AI-powered predictions.

## 📁 **Clean Project Structure**

```
library_analytics_project/
├── 📱 DEPLOYED APPLICATIONS
│   ├── app.py                    # 🎯 Main Dashboard (deployed)
│   ├── ml_prediction_hub.py      # 🤖 ML Prediction System (deployed)
│   ├── requirements.txt          # 📦 Main dependencies
│   └── requirements_ml_hub.txt   # 🔬 ML-specific dependencies
│
├── 📚 DATA & CONFIGURATION
│   ├── data/                     # 🗃️ Data storage & databases
│   ├── notebooks/               # 📓 Analysis & ML notebooks
│   ├── .streamlit/              # ⚙️ Streamlit configuration
│   └── env/                     # 🐍 Python virtual environment
│
├── 📖 DOCUMENTATION
│   ├── README.md                # 📋 Main project documentation
│   ├── PORTFOLIO_TEMPLATES.md   # 💼 Portfolio & resume templates
│   ├── ML_HUB_DEPLOYMENT.md     # 🚀 ML deployment guide
│   ├── DEPLOYMENT_GUIDE.md      # 📡 General deployment guide
│   └── docs/                    # 📚 Additional documentation
│
├── 🔧 DEVELOPMENT (Optional)
│   ├── app/advanced_api.py       # 🌐 Advanced API (local dev)
│   ├── models/                  # 🤖 ML models & training
│   ├── scripts/                 # ⚡ Quick start scripts
│   ├── sql/                     # 🗄️ Database scripts
│   ├── tests/                   # 🧪 Test files
│   └── setup/                   # 🔧 Setup utilities
│
└── 🗃️ ARCHIVE
    ├── old_dashboards/          # 📊 Previous dashboard versions
    ├── old_apis/               # 🌐 Previous API versions
    ├── old_requirements/       # 📦 Previous dependency files
    └── etl_system/             # 🔄 ETL infrastructure (archived)
```

## ✨ **Key Features**

### 🎭 **Role-Based Dashboard System**
- **👑 Admin Portal**: Executive insights, user management, business intelligence
- **📚 Librarian Tools**: Daily operations, collection management, performance tracking
- **📖 Member Experience**: Personal library, book discovery, reading analytics
- **🌟 Demo Mode**: Full system exploration with sample data

### 🤖 **AI-Powered ML Prediction Hub**
- **🎯 Member Churn Prediction**: Identify at-risk members (85%+ accuracy)
- **⚠️ Overdue Risk Analysis**: Predict loan defaults and late returns
- **📈 Book Popularity Forecasting**: Demand prediction for inventory management
- **📊 Model Performance Monitoring**: Real-time model tracking and metrics
- **🔧 Batch Processing Engine**: Bulk predictions and analysis

### 📊 **Advanced Analytics**
- Interactive charts with Plotly
- Real-time performance metrics
- Predictive analytics and insights
- Custom visualizations for each role

### 🚀 **Cloud-Ready Deployment**
- Optimized for Streamlit Cloud
- Lightweight dependencies
- Fast loading times (< 2 seconds)
- Mobile-responsive design

## 🚀 **Quick Start**

### ⚡ **Instant Access (Recommended)**
Use the live deployed applications:
- **Dashboard**: https://a4sbmlac2wrrnjlahpyaqv.streamlit.app/
- **ML Hub**: https://mlpredictionapppy-97ovakrjjxaenevmrrjp89.streamlit.app/

### 🔧 **Local Development**
```bash
# 1. Clone repository
git clone https://github.com/Rishika-R-Gour/library-analytics-project.git
cd library-analytics-project

# 2. Set up environment
source env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run main dashboard
streamlit run app.py

# 5. Run ML prediction hub
streamlit run ml_prediction_hub.py --server.port 8502
```

### 🎯 **Quick Scripts**
```bash
./scripts/START_NOW.sh        # Ultra-fast local startup
./scripts/status.sh           # Check service status
```

## 🛠️ **Technical Stack**

- **Frontend**: Streamlit with custom CSS and responsive design
- **Backend**: Flask APIs (optional for local development)
- **Database**: SQLite with comprehensive schema
- **ML**: Scikit-learn with Random Forest and Gradient Boosting
- **Visualization**: Plotly for interactive charts
- **Deployment**: Streamlit Cloud with optimized dependencies
- **Environment**: Python 3.11 with virtual environment

## 📊 **Applications Overview**

### 🎯 **Main Dashboard (app.py)**
Professional library management system with:
- Role-based authentication and interfaces
- Real-time analytics and visualizations
- Book catalog and loan management
- Member analytics and insights
- Mobile-responsive design

### 🤖 **ML Prediction Hub (ml_prediction_hub.py)**
Advanced AI prediction system with:
- 3 trained machine learning models
- Interactive prediction interfaces
- Model performance monitoring
- Batch processing capabilities
- Feature importance analysis

## 📖 **Usage Guide**

### 🔐 **Authentication Options**
- **Quick Access**: Select role (Admin/Librarian/Member) or Demo Mode
- **Local API**: Use test accounts (admin/admin123, librarian/lib123, member/member123)

### 🎯 **Navigation**
1. **Library Management**: Book catalog, search, loans
2. **Analytics**: Dashboards, reports, visualizations
3. **ML Predictions**: AI-powered insights and forecasting
4. **User Management**: Role-based access and permissions

## 🎯 **Development Status**

- ✅ **Core Applications**: Both apps deployed and fully functional
- ✅ **Documentation**: Comprehensive guides and templates
- ✅ **ML Integration**: 3 trained models with high accuracy
- ✅ **Cloud Deployment**: Optimized for production use
- ✅ **Portfolio Ready**: Professional presentation materials

## 📝 **Documentation**

- `README.md`: Main project documentation (this file)
- `PORTFOLIO_TEMPLATES.md`: Resume, LinkedIn, and portfolio templates
- `ML_HUB_DEPLOYMENT.md`: ML prediction hub deployment guide
- `DEPLOYMENT_GUIDE.md`: General deployment instructions
- `PROJECT_CLEANUP.md`: Organization and cleanup documentation

## 🔧 **Project Organization**

This project has been professionally organized with:
- **Clean separation** of deployed vs development code
- **Archived legacy files** to maintain history without clutter
- **Simplified structure** for easy navigation and maintenance
- **Professional documentation** ready for portfolio use

## 🎯 **For Developers**

### 📋 **Essential Files Only**
Focus on these key files for understanding the project:
- `app.py` - Main application
- `ml_prediction_hub.py` - ML system
- `requirements.txt` & `requirements_ml_hub.txt` - Dependencies
- This README for overview

### 🗃️ **Archived Components**
Complex ETL infrastructure, multiple API versions, and old dashboard iterations have been archived but preserved for reference.

---

**🌟 Ready for professional showcase, portfolio inclusion, and continued development!**
