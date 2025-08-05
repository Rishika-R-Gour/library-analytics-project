# 🚀 Library Analytics Production Application

## Overview
This is the production-ready Flask API and Streamlit dashboard for the Library Analytics System. The application provides REST API endpoints for ML model predictions and an interactive dashboard for data visualization.

## 🏗️ Architecture

```
Production Application
├── app/                     # Flask API Backend
│   ├── api.py              # Main Flask application
│   ├── api_client.py       # API testing client
│   └── __init__.py         # Package initialization
├── dashboard/              # Streamlit Frontend
│   └── library_dashboard.py # Interactive dashboard
├── models/                 # ML Models & Management
│   ├── production/         # Production models
│   └── model_manager.py    # Model lifecycle management
└── scripts/               # Startup scripts
    ├── start_api.sh       # Start Flask API
    └── start_dashboard.sh # Start Streamlit dashboard
```

## 🔧 Components

### 1. **Flask API Backend** (`app/api.py`)
- **Authentication**: JWT-based authentication system
- **Rate Limiting**: Built-in rate limiting for API endpoints
- **CORS Support**: Cross-origin resource sharing enabled
- **ML Predictions**: Real-time model inference endpoints
- **Data API**: Database query endpoints with pagination

#### **API Endpoints:**
- `POST /api/auth/login` - User authentication
- `GET /api/health` - Health check
- `GET /api/dashboard/stats` - Dashboard statistics
- `POST /api/predictions/overdue` - Overdue prediction
- `POST /api/predictions/churn` - Churn prediction
- `GET /api/recommendations/{member_id}` - Book recommendations
- `GET /api/members` - Members list with pagination
- `GET /api/models/status` - ML models status

### 2. **Streamlit Dashboard** (`dashboard/library_dashboard.py`)
- **Interactive UI**: Modern web interface with authentication
- **Real-time API Integration**: Live data from Flask backend
- **ML Predictions**: Interactive model prediction interface
- **Data Visualization**: Charts and metrics powered by Plotly
- **Responsive Design**: Mobile-friendly layout

### 3. **Authentication System**
- **Demo Credentials**: Username: `admin`, Password: `admin123`
- **JWT Tokens**: Secure token-based authentication
- **Session Management**: Automatic token refresh and logout
- **Rate Limiting**: Protection against abuse

## 🚀 Quick Start

### **Option 1: Using Startup Scripts**

1. **Start the API Server:**
   ```bash
   ./start_api.sh
   ```
   This will start the Flask API on `http://localhost:5000`

2. **Start the Dashboard:**
   ```bash
   ./start_dashboard.sh
   ```
   This will start the Streamlit dashboard on `http://localhost:8501`

### **Option 2: Manual Setup**

1. **Install Dependencies:**
   ```bash
   pip install flask flask-cors flask-limiter pyjwt requests streamlit
   ```

2. **Start Flask API:**
   ```bash
   cd app
   python api.py
   ```

3. **Start Streamlit Dashboard:**
   ```bash
   cd dashboard
   streamlit run library_dashboard.py
   ```

## 🔐 Authentication

### **Login Credentials**
- **Username**: `admin`
- **Password**: `admin123`

### **API Usage**
1. Get authentication token:
   ```bash
   curl -X POST http://localhost:5000/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"admin123"}'
   ```

2. Use token in subsequent requests:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:5000/api/dashboard/stats
   ```

## 📊 Dashboard Features

### **Main Dashboard**
- **Key Metrics**: Members, loans, overdue statistics
- **Real-time Updates**: Live data from the API
- **Interactive Charts**: Plotly-powered visualizations

### **ML Predictions**
- **Overdue Risk**: Predict which loans are likely to be overdue
- **Member Churn**: Identify members at risk of leaving
- **Book Recommendations**: Personalized book suggestions

### **System Monitoring**
- **Model Status**: Check ML model health and performance
- **API Health**: Monitor backend connectivity
- **Database Stats**: View data freshness and counts

## 🤖 API Testing

Use the included API client for testing:

```python
from app.api_client import LibraryAPIClient

# Initialize client
client = LibraryAPIClient()

# Login
client.login("admin", "admin123")

# Get stats
stats = client.get_dashboard_stats()
print(f"Total members: {stats['total_members']}")

# Make predictions
predictions = client.predict_overdue([
    {'loan_id': 1, 'member_type': 'Student', 'days_borrowed': 15}
])
```

Or run the demo:
```bash
cd app
python api_client.py
```

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based auth
- **Rate Limiting**: API endpoint protection
- **CORS Configuration**: Controlled cross-origin access
- **Input Validation**: Request data validation
- **Error Handling**: Secure error responses

## 📈 Performance

- **Rate Limits**: 200 requests/day, 50 requests/hour per IP
- **Response Time**: <200ms for most endpoints
- **Caching**: Streamlit data caching for performance
- **Database**: SQLite with optimized queries

## 🔄 API Response Format

All API responses follow this format:
```json
{
  "status": "success",
  "data": { ... },
  "timestamp": "2025-08-04T13:00:00Z"
}
```

Error responses:
```json
{
  "error": "Error message",
  "timestamp": "2025-08-04T13:00:00Z"
}
```

## 🐛 Troubleshooting

### **API Connection Issues**
- Ensure Flask API is running on port 5000
- Check firewall settings
- Verify virtual environment activation

### **Authentication Problems**
- Use correct credentials: admin/admin123
- Check token expiration (24-hour default)
- Clear browser cache if needed

### **Dashboard Not Loading**
- Confirm Streamlit is running on port 8501
- Check API connectivity from dashboard
- Verify database file exists in notebooks/

## 🔧 Configuration

### **Environment Variables**
- `SECRET_KEY`: Flask secret key (auto-generated if not set)
- `JWT_SECRET_KEY`: JWT signing key (auto-generated if not set)
- `FLASK_DEBUG`: Enable debug mode (default: False)

### **Database Path**
The API expects the SQLite database at:
`../notebooks/library.db`

Modify the `DATABASE_PATH` in `api.py` if your database is elsewhere.

## 📦 Dependencies

**Core:**
- Flask 2.3.3 - Web framework
- Streamlit - Dashboard framework
- SQLite3 - Database
- Pandas/NumPy - Data processing
- Plotly - Visualizations

**Security:**
- PyJWT - JWT tokens
- Flask-CORS - Cross-origin support
- Flask-Limiter - Rate limiting

**Production:**
- Gunicorn - WSGI server
- Requests - HTTP client

## 🚀 Production Deployment

For production deployment:

1. **Use Gunicorn:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app.api:create_app()
   ```

2. **Set Environment Variables:**
   ```bash
   export SECRET_KEY="your-secret-key"
   export JWT_SECRET_KEY="your-jwt-key"
   export FLASK_DEBUG=false
   ```

3. **Use HTTPS** and proper SSL certificates
4. **Configure Database** connection pooling
5. **Set up Monitoring** and logging
6. **Use Redis** for rate limiting in production

---

## 🎯 Next Steps

- **Docker Containerization**: Package the application
- **Cloud Deployment**: Deploy to AWS/GCP/Azure
- **Database Migration**: Move to PostgreSQL
- **Advanced Monitoring**: Add Prometheus/Grafana
- **CI/CD Pipeline**: Automated testing and deployment

---

*Built with ❤️ for advanced library analytics*
