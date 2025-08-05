#!/bin/bash

echo "🚀 GitHub Setup Helper for Rishika's Library Analytics Project"
echo "============================================================="
echo ""

# Check if we're in the right directory
if [[ ! -f "README.md" || ! -d "app" || ! -d "dashboard" ]]; then
    echo "❌ Error: Please run this from the library_analytics_project directory"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo ""

# Check git status
if git status &>/dev/null; then
    echo "✅ Git repository initialized"
    
    # Check if remote exists
    if git remote get-url origin &>/dev/null; then
        echo "✅ Remote origin set: $(git remote get-url origin)"
    else
        echo "🔗 Setting up remote..."
        git remote add origin https://github.com/Rishika-R-Gour/library-analytics-project.git
        echo "✅ Remote added: $(git remote get-url origin)"
    fi
    
    # Check if there are commits
    if git log --oneline -1 &>/dev/null; then
        echo "✅ Commits ready: $(git log --oneline -1)"
    else
        echo "📝 Creating initial commit..."
        git add .
        git commit -m "🚀 Initial commit: Library Analytics Project

✨ Features:
- Professional ML-powered library management system
- Role-based authentication (Admin/Librarian/Member)
- Real-time predictive analytics and recommendations
- Modern UI with glass-morphism effects
- Enterprise-grade ETL infrastructure
- Ultra-fast dashboard (<2s load time)

🛠️ Tech Stack:
- Backend: Flask APIs with JWT authentication
- Frontend: Streamlit dashboards with custom CSS
- ML: XGBoost models for predictions
- Database: SQLite with optimized schema

🎯 Ready for: Portfolio, interviews, production deployment"
        echo "✅ Initial commit created"
    fi
    
    echo ""
    echo "🎯 NEXT STEPS:"
    echo "1. Go to: https://github.com/Rishika-R-Gour"
    echo "2. Click 'New repository'"
    echo "3. Name: library-analytics-project"
    echo "4. Make it PUBLIC"
    echo "5. DON'T check any initialization boxes"
    echo "6. Click 'Create repository'"
    echo "7. Then run: git push -u origin main"
    echo ""
    echo "🔗 Your repository URL will be:"
    echo "   https://github.com/Rishika-R-Gour/library-analytics-project"
    echo ""
    echo "✨ Ready to push!"
    
else
    echo "❌ Git not initialized. Run: git init"
fi
