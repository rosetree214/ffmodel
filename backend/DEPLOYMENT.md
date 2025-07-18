# FFModel Backend Deployment Guide

## Render Deployment Setup

### Prerequisites
- GitHub repository with the FFModel backend code
- Render account (https://render.com)

### Step 1: Create Render Services

#### 1.1 Create PostgreSQL Database
1. Go to Render Dashboard
2. Click "New" → "PostgreSQL"
3. Configure:
   - Name: `ffmodel-db`
   - Database Name: `ffmodel`
   - User: `ffmodel_user`
   - Plan: Free (for development)
4. Click "Create Database"
5. Note the Internal Database URL (starts with `postgresql://`)

#### 1.2 Create Redis Instance
1. Click "New" → "Redis"
2. Configure:
   - Name: `ffmodel-redis`
   - Plan: Free
3. Click "Create Redis"
4. Note the Internal Redis URL

#### 1.3 Create Web Service
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - Name: `ffmodel-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt && python migration_startup.py`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`
   - Plan: Free

### Step 2: Configure Environment Variables

Add these environment variables in the Render dashboard:

```bash
# Required Variables
DATABASE_URL=<your-postgres-internal-url>
REDIS_URL=<your-redis-internal-url>
SECRET_KEY=<generate-a-strong-secret-key>
NETLIFY_URL=<your-netlify-frontend-url>

# Optional Variables
ENVIRONMENT=production
TRUSTED_HOSTS=*
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
REDIS_PASSWORD=<your-redis-password-if-set>
```

### Step 3: Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Monitor the build logs for any errors
4. Once deployed, test the health endpoint: `https://your-app.onrender.com/api/health`

### Step 4: Initialize Database

The `migration_startup.py` script will automatically:
1. Run Alembic migrations
2. Load sample data from `data/players.csv` (if available)

### Step 5: Configure Frontend

Update your Netlify environment variables:
```bash
VITE_API_URL=https://your-render-backend.onrender.com/api
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify DATABASE_URL is correct
   - Ensure PostgreSQL service is running
   - Check firewall/network settings

2. **Redis Connection Error**
   - Verify REDIS_URL is correct
   - Check if Redis password is required

3. **Build Failures**
   - Check Python version compatibility
   - Verify all dependencies in requirements.txt
   - Review build logs for specific errors

4. **CORS Issues**
   - Verify NETLIFY_URL is set correctly
   - Check CORS configuration in main.py

### Health Check Endpoints

- `/api/health` - Comprehensive health check
- `/api/metrics` - Application metrics
- `/` - Basic service info

### Monitoring

- Use Render's built-in monitoring
- Monitor logs via Render dashboard
- Set up alerts for service downtime

### Scaling

For production use:
- Upgrade to paid plans for better performance
- Consider using managed PostgreSQL
- Implement proper monitoring and alerting
- Add database backups

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| DATABASE_URL | Yes | PostgreSQL connection string | postgresql://user:pass@host:5432/db |
| REDIS_URL | Yes | Redis connection string | redis://host:6379 |
| SECRET_KEY | Yes | Secret key for security | random-secret-key |
| NETLIFY_URL | Yes | Frontend URL for CORS | https://myapp.netlify.app |
| ENVIRONMENT | No | Environment name | production |
| TRUSTED_HOSTS | No | Allowed hosts | * |
| RATE_LIMIT_REQUESTS | No | Rate limit requests | 100 |
| RATE_LIMIT_WINDOW | No | Rate limit window (seconds) | 60 |
| REDIS_PASSWORD | No | Redis password if auth enabled | password |

## Production Checklist

- [ ] Database configured with backups
- [ ] Redis configured
- [ ] Environment variables set
- [ ] CORS configured for production domain
- [ ] Health checks working
- [ ] Monitoring setup
- [ ] Error tracking configured
- [ ] Performance monitoring enabled
- [ ] Security headers configured
- [ ] Rate limiting enabled