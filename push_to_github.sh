#!/bin/bash

echo "🚀 Pushing Library Analytics Project to GitHub"
echo "=============================================="

# Navigate to project directory
cd /Users/rishikagour/library_analytics_project

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
fi

# Add all files
echo "📁 Adding all files..."
git add -A

# Create commit if needed
if ! git log --oneline -1 &>/dev/null; then
    echo "📝 Creating initial commit..."
    git commit -m "🚀 Library Analytics Project - Complete Implementation

✨ Enterprise-grade library management system with:
- ML predictions (overdue risk, churn analysis, recommendations)  
- Role-based authentication (Admin/Librarian/Member)
- Modern Streamlit dashboards with professional UI
- Flask APIs with JWT authentication
- Real-time analytics and visualizations

🛠️ Tech Stack: Flask, Streamlit, ML models, SQLite, JWT auth
🎯 Portfolio-ready full-stack project"
fi

# Set up remote if not exists
if ! git remote get-url origin &>/dev/null; then
    echo "🔗 Adding GitHub remote..."
    git remote add origin https://github.com/Rishika-R-Gour/library-analytics-project.git
fi

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Your project is now on GitHub!"
    echo "🌐 Repository URL: https://github.com/Rishika-R-Gour/library-analytics-project"
    echo ""
    echo "🎯 Next steps:"
    echo "1. Visit your repository to see all files"
    echo "2. Add a description in repository settings"
    echo "3. Add topics: python, streamlit, flask, machine-learning"
    echo "4. Star your own repository to show it off!"
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo "1. Repository doesn't exist on GitHub yet"
    echo "2. Authentication required (use personal access token)"
    echo "3. Network connection issues"
    echo ""
    echo "🔧 To fix:"
    echo "1. Go to https://github.com/Rishika-R-Gour"
    echo "2. Create new repository named: library-analytics-project"
    echo "3. Make it public, don't initialize with anything"
    echo "4. Run this script again"
fi
