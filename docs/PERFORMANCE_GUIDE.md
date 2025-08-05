# 🚨 Performance Troubleshooting Guide

## Common Causes of Slow Loading:

### 1. **Port Conflicts** 🔴
**Problem**: Other applications using ports 5002, 5003, 8501, 8503
**Solution**:
```bash
# Check what's using the ports
lsof -i :5002,:5003,:8501,:8503

# Kill processes if needed
pkill -f "streamlit"
pkill -f "python.*api"
```

### 2. **API Timeout Issues** ⏰
**Problem**: Dashboard waiting for APIs that aren't responding
**Solution**: Use the ultra-fast dashboard (no API dependencies)
```bash
./scripts/ultra_fast_start.sh
```

### 3. **Resource Conflicts** 💾
**Problem**: Multiple instances running simultaneously
**Solution**:
```bash
# Clean slate restart
pkill -f "streamlit|python.*api"
sleep 3
./scripts/ultra_fast_start.sh
```

### 4. **Virtual Environment Issues** 🐍
**Problem**: Python environment not properly activated
**Solution**:
```bash
cd /Users/rishikagour/library_analytics_project
source env/bin/activate
python --version  # Should show Python from env/bin/
```

## 🚀 **INSTANT SOLUTIONS**:

### **Option 1: Ultra Fast Dashboard (Recommended)**
```bash
./scripts/ultra_fast_start.sh
```
- ⚡ Loads in < 2 seconds
- 🚫 No API dependencies
- ✅ All core features

### **Option 2: Diagnostic + Auto-Fix**
```bash
python scripts/diagnose_and_fix.py
```
- 🔍 Identifies issues automatically
- 🔧 Creates optimized startup script
- 📋 Provides specific recommendations

### **Option 3: Manual Clean Start**
```bash
# Kill everything
pkill -f "streamlit|python.*api"

# Wait
sleep 5

# Start just the dashboard
cd /Users/rishikagour/library_analytics_project
source env/bin/activate
streamlit run dashboard/ultra_fast_dashboard.py --server.port 8501
```

## 🎯 **Performance Tips**:

1. **Use the ultra-fast dashboard** for instant access
2. **Close other browsers/applications** to free up resources  
3. **Restart your computer** if issues persist
4. **Check Activity Monitor** for runaway processes
5. **Use Chrome in incognito mode** for testing

## 📊 **Expected Loading Times**:
- **Ultra Fast Dashboard**: < 2 seconds
- **Regular Dashboard (with APIs)**: 5-10 seconds
- **Full System**: 10-15 seconds

If any option takes longer than these times, there's likely a system issue that needs addressing.
