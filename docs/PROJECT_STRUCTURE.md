# Library Analytics Project - File Organization

## 📁 Project Structure

```
library_analytics_project/
├── 📋 README.md                     # Main project documentation
├── 📋 PROJECT_STRUCTURE.md          # This file - project organization
├── 📦 requirements.txt              # Python dependencies
├── 🗄️ library.db                   # Main SQLite database
├── 🚀 quick_start.sh                # Smart startup script (recommended)
├── 📊 status.sh                     # Quick status checker
├── 🔧 start.sh                      # Interactive menu (legacy)
│
├── 📱 app/                          # Backend APIs
│   ├── advanced_api.py              # Multi-role authentication API
│   ├── simple_library_api.py        # Library management API
│   └── simple_api.py                # Basic API
│
├── 📊 dashboard/                    # Frontend Streamlit apps
│   ├── advanced_dashboard.py        # Enhanced dashboard with role-based features
│   └── library_dashboard.py         # Original ML predictions dashboard
│
├── 🗃️ data/                        # Data storage
│   ├── raw/                        # Raw data files
│   ├── processed/                  # Processed data
│   └── staging/                    # Staging area for ETL
│
├── 📚 docs/                        # Documentation
│   ├── COMPLETION_STATUS.md         # Project completion status
│   ├── NOTEBOOK_STATUS.md           # Notebook documentation
│   ├── PHASE4_COMPLETION_SUMMARY.md # Phase 4 summary
│   └── SYSTEM_WORKING.md            # System status documentation
│
├── 🤖 models/                      # ML models and training
│   └── (ML model files)
│
├── 📓 notebooks/                   # Jupyter notebooks
│   ├── 01_data_modeling.ipynb      # Data modeling notebook
│   ├── library.db                  # Notebook database
│   └── test.db                     # Test database
│
├── ⚙️ scripts/                     # Startup and utility scripts
│   ├── fast_start.sh               # Quick startup (recommended)
│   ├── start_phase4.sh             # Full ETL startup
│   ├── start_phase5.sh             # Phase 5 startup
│   ├── start_project.sh            # Basic project startup
│   └── check_status.py             # System status checker
│
├── 🔧 setup/                       # Setup and initialization scripts
│   ├── setup_phase3_db.py          # Phase 3 database setup
│   ├── setup_phase4_etl.py         # ETL infrastructure setup
│   ├── setup_phase4_etl_demo.py    # ETL demo setup
│   └── setup_phase5_database.py    # Phase 5 database setup
│
├── 🧪 tests/                       # Test files and HTML test pages
│   ├── api_test.html               # API testing page
│   ├── complex_api_test.html       # Complex API tests
│   ├── phase3_test.html            # Phase 3 tests
│   ├── test_db_connection.py       # Database connection test
│   └── test_system.py              # System integration test
│
├── 🗄️ sql/                        # SQL scripts and queries
│   └── (SQL files)
│
├── 📈 monitoring/                  # ETL monitoring and metrics
│   └── (monitoring files)
│
├── 🔄 pipelines/                   # ETL pipeline definitions
│   └── (pipeline files)
│
├── ⏰ schedulers/                  # Task scheduling
│   └── (scheduler files)
│
├── ⚙️ config/                      # Configuration files
│   └── (config files)
│
├── 📝 logs/                        # Application logs
│   └── (log files)
│
└── 🐍 env/                         # Python virtual environment
    └── (virtual environment files)
```

## 🚀 Quick Start Commands

### Smartest Startup (Recommended)
```bash
./quick_start.sh
```

### Quick Status Check
```bash
./status.sh
```

### Advanced Options
```bash
./scripts/fast_start.sh      # Fast startup
./scripts/start_phase4.sh    # Full ETL system
./scripts/start_phase5.sh    # Phase 5 library management
```

## 🔗 Service URLs

- **📊 Enhanced Dashboard**: http://localhost:8501
- **🤖 ML Predictions**: http://localhost:8503
- **🔧 Advanced API**: http://localhost:5002
- **📚 Library API**: http://localhost:5003

## 👥 Default Accounts

- **Admin**: admin / admin123
- **Librarian**: librarian / lib123
- **Member**: member / member123

## 📋 Key Features

- ✅ Multi-role Authentication
- ✅ Library Management System
- ✅ ML Predictions (4 types)
- ✅ ETL Infrastructure
- ✅ Data Quality Monitoring
- ✅ Real-time Dashboards

## 🔧 Management

- **Quick Status**: `./status.sh`
- **Smart Start**: `./quick_start.sh`  
- **Detailed Status**: `python scripts/check_status.py`
- **Stop All**: `pkill -f "streamlit|advanced_api"`
- **View Logs**: Check `logs/` directory
