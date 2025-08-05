# 📚 Library Analytics Project

A comprehensive library management and analytics system with role-based dashboards, data visualizations, and cloud deployment.

## 🌐 **Live Demo**
🔗 **[Library Analytics Dashboard](https://a4sbmlac2wrrnjlahpyaqv.streamlit.app/)** - Role-based dashboards with interactive analytics

🤖 **[ML Prediction Hub](https://mlpredictionapppy-97ovakrjjxaenevmrrjp89.streamlit.app/)** - Advanced machine learning predictions & analytics

> **🎯 Complete System**: Features role-based dashboards (Admin, Librarian, Member) with interactive analytics, book management, real-time visualizations, and AI-powered predictions.

## ✨ **Key Features**

### 🎭 **Role-Based Access**
- **👑 Admin Portal**: Executive dashboard, user management, business intelligence
- **📚 Librarian Workspace**: Daily operations, collection management, performance metrics
- **📖 Member Experience**: Personal library, book discovery, reading analytics
- **🌟 Demo Mode**: Full system exploration with sample data

### 📊 **Advanced Analytics**
- Interactive charts with Plotly
- Real-time performance metrics
- Predictive analytics and insights
- Custom visualizations for each role

### 🚀 **Cloud-Ready**
- Optimized for Streamlit Cloud deployment
- Lightweight dependencies (13 packages)
- Fast loading times (< 2 seconds)
- Mobile-responsive design

## 🚀 Quick Start

## 🎯 **Development & Testing**

### 📋 **Default Test Accounts (Local Development)**
| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Librarian | librarian | lib123 |
| Member | member | member123 |

### 🛠️ **Local Development Commands**
```bash
# Quick start with scripts
./scripts/START_NOW.sh           # Ultra-fast local startup
./scripts/status.sh              # Check service status

# Manual startup
source env/bin/activate
streamlit run app.py             # Main dashboard
streamlit run ml_prediction_hub.py --server.port 8502  # ML hub
```

## 📁 **Organized Project Structure**

```
library_analytics_project/
├── 📱 CORE APPLICATIONS
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
│   ├── PORTFOLIO_TEMPLATES.md   # � Portfolio & resume templates
│   ├── ML_HUB_DEPLOYMENT.md     # 🚀 ML deployment guide
│   └── docs/                    # 📚 Additional documentation
│
├── � DEVELOPMENT (Optional)
│   ├── app/advanced_api.py       # 🌐 Advanced API (local dev)
│   ├── models/                  # 🤖 ML models & training
│   ├── scripts/                 # ⚡ Quick start scripts
│   ├── sql/                     # 🗄️ Database scripts
│   └── tests/                   # 🧪 Test files
│
└── 🗃️ ARCHIVE
    ├── old_dashboards/          # 📊 Previous dashboard versions
    ├── old_apis/               # 🌐 Previous API versions
    ├── old_requirements/       # 📦 Previous dependency files
    └── etl_system/             # 🔄 ETL infrastructure (archived)
```

## 🚀 **Quick Start Options**

### ⚡ **Instant Access (Recommended)**
Use the live deployed applications:
- **📊 Dashboard**: https://a4sbmlac2wrrnjlahpyaqv.streamlit.app/
- **🤖 ML Hub**: https://mlpredictionapppy-97ovakrjjxaenevmrrjp89.streamlit.app/

### 🔧 **Local Development**
```bash
# Clone and setup
git clone https://github.com/Rishika-R-Gour/library-analytics-project.git
cd library-analytics-project
source env/bin/activate

# Run main dashboard
streamlit run app.py

# Run ML prediction hub (separate terminal)
streamlit run ml_prediction_hub.py --server.port 8502
```

## 👥 Default Test Accounts

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Librarian | librarian | lib123 |
| Member | member | member123 |

## ✨ **Core Features**

### 🎨 **Modern Professional UI**
- **Role-based interfaces** (Admin/Librarian/Member) with distinct features
- **Modern design** with gradients, animations, and responsive layouts
- **Interactive visualizations** with advanced analytics and insights
- **Real-time updates** and live activity monitoring

### 🤖 **AI-Powered Machine Learning**
- **Member Churn Prediction**: Identify at-risk members (85%+ accuracy)
- **Overdue Risk Analysis**: Predict loan defaults and late returns
- **Book Popularity Forecasting**: Demand prediction for inventory management
- **Model Performance Monitoring**: Real-time ML model tracking
- **Batch Processing Engine**: Bulk predictions and analysis

### 📚 **Comprehensive Library Management**
- **Professional book catalog** with ratings, popularity, and metadata
- **Advanced search and filtering** with multiple criteria
- **Smart loan management** with automated workflows
- **Real-time availability tracking** and inventory management

### 📊 **Advanced Analytics & Insights**
- **Executive dashboards** with KPIs and performance metrics
- **Interactive data visualizations** with drill-down capabilities
- **Member behavior analytics** and usage patterns
- **Correlation analysis** and trend forecasting

## �️ **Technical Stack**

- **Frontend**: Streamlit with custom CSS and responsive design
- **Machine Learning**: Scikit-learn with Random Forest and Gradient Boosting
- **Visualization**: Plotly for interactive charts and analytics
- **Database**: SQLite with comprehensive schema
- **Deployment**: Streamlit Cloud with optimized dependencies
- **Environment**: Python 3.11 with virtual environment

## � **Usage Guide**

### 🌐 **Accessing the Applications**
1. **🔗 Online**: Visit the live deployed applications (recommended)
   - **Dashboard**: https://a4sbmlac2wrrnjlahpyaqv.streamlit.app/
   - **ML Hub**: https://mlpredictionapppy-97ovakrjjxaenevmrrjp89.streamlit.app/

2. **💻 Local**: Run locally for development
   - Clone repository and follow Quick Start instructions above

### 🎯 **Navigation & Features**
- **📚 Library Management**: Book catalog, search, loans
- **📊 Analytics**: Real-time dashboards and visualizations  
- **🤖 ML Predictions**: AI-powered insights and forecasting
- **👥 Role-based Views**: Different features for each user type (Admin/Librarian/Member)

### 🔐 **Authentication**
- **Online Apps**: Select role (Admin/Librarian/Member) or Demo Mode
- **Local Development**: Use test accounts listed above if running with APIs

## 🎯 **Project Status**

- ✅ **Core Applications**: Both apps deployed and fully functional
- ✅ **ML Integration**: 3 trained models with high accuracy  
- ✅ **Documentation**: Comprehensive guides and portfolio templates
- ✅ **Cloud Deployment**: Optimized for production use
- ✅ **Professional Organization**: Clean structure ready for portfolio showcase

## � **Documentation Files**

- `README.md`: Main project documentation (this file)
- `PORTFOLIO_TEMPLATES.md`: Resume, LinkedIn, and portfolio templates  
- `ML_HUB_DEPLOYMENT.md`: ML prediction hub deployment guide
- `PROJECT_CLEANUP.md`: Organization and cleanup documentation

---

