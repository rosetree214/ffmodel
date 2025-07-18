#!/bin/bash

# FFModel Render Deployment Helper Script
# This script helps automate the deployment process

echo "🚀 FFModel Render Deployment Helper"
echo "=================================="
echo ""

# Check if git repo is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes. Please commit them first."
    git status --short
    exit 1
fi

# Check if we're on main branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "⚠️  Warning: You're not on the main branch. Switch to main first."
    echo "Current branch: $current_branch"
    exit 1
fi

echo "✅ Git repository is clean and on main branch"
echo ""

# Generate a secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

echo "🔧 Generated configuration:"
echo "SECRET_KEY=$SECRET_KEY"
echo ""

echo "📋 Manual steps to complete deployment:"
echo ""
echo "1. 🌐 Go to https://render.com and sign up/login"
echo "2. 🔗 Connect your GitHub account"
echo "3. 📊 Create PostgreSQL database:"
echo "   - Name: ffmodel-db"
echo "   - Database: ffmodel"
echo "   - Plan: Free"
echo "4. 🔴 Create Redis instance:"
echo "   - Name: ffmodel-redis"
echo "   - Plan: Free"
echo "5. 🖥️  Create Web Service:"
echo "   - Repository: rosetree214/ffmodel"
echo "   - Root Directory: backend"
echo "   - Environment: Python 3"
echo "   - Build Command: pip install -r requirements.txt && python migration_startup.py"
echo "   - Start Command: uvicorn main:app --host 0.0.0.0 --port \$PORT --workers 1"
echo "6. 🔧 Set Environment Variables:"
echo "   DATABASE_URL=<your-postgres-internal-url>"
echo "   REDIS_URL=<your-redis-internal-url>"
echo "   SECRET_KEY=$SECRET_KEY"
echo "   NETLIFY_URL=<your-netlify-url>"
echo "   ENVIRONMENT=production"
echo "   TRUSTED_HOSTS=*"
echo "   RATE_LIMIT_REQUESTS=100"
echo "   RATE_LIMIT_WINDOW=60"
echo ""
echo "7. 🚀 Deploy and monitor the build logs"
echo "8. 🧪 Test endpoints:"
echo "   - https://your-app.onrender.com/"
echo "   - https://your-app.onrender.com/api/health"
echo "   - https://your-app.onrender.com/docs"
echo ""
echo "Need help? Check DEPLOYMENT.md for detailed instructions!"
echo ""
echo "🎉 Ready to deploy! Follow the steps above."