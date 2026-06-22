# 🚀 FirstAid Platform - Deployment Guide

## Deployment Overview

This guide covers deploying FirstAid from development to production environments.

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:
- [ ] All tests passing (see TESTING_GUIDE.md)
- [ ] No console errors
- [ ] Environment variables configured
- [ ] Database backups created
- [ ] Security review completed
- [ ] Performance optimized
- [ ] Documentation updated

---

## 🏠 Local Development (Current Setup)

### Status: ✅ Running on localhost:3000 and localhost:5000

**Configuration:**
```
Frontend: http://localhost:3000
Backend: http://localhost:5000/api
Environment: development
Database: JSON files
```

**Start Commands:**
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python run.py

# Terminal 2 - Frontend
cd frontend
npm start
```

---

## 🐳 Docker Deployment

### Step 1: Create Backend Dockerfile

**File: `backend/Dockerfile`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create upload directory
RUN mkdir -p uploads

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "run:app"]
```

### Step 2: Create Frontend Dockerfile

**File: `frontend/Dockerfile`**
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build app
RUN npm run build

# Production image
FROM node:18-alpine

WORKDIR /app

# Install serve
RUN npm install -g serve

# Copy build from builder
COPY --from=build /app/build ./build

# Expose port
EXPOSE 3000

# Run app
CMD ["serve", "-s", "build", "-l", "3000"]
```

### Step 3: Create Docker Compose

**File: `docker-compose.yml`**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - FLASK_PORT=5000
    volumes:
      - ./backend/uploads:/app/uploads
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:5000/api
    depends_on:
      - backend
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Deploy with Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## ☁️ Heroku Deployment

### Backend Deployment

**Step 1: Create Heroku App**
```bash
heroku create firstaid-api
heroku buildpacks:add heroku/python
```

**Step 2: Create Procfile**

**File: `backend/Procfile`**
```
web: gunicorn --workers 4 --timeout 120 run:app
```

**Step 3: Set Environment Variables**
```bash
heroku config:set JWT_SECRET_KEY=your-production-secret-key
heroku config:set FLASK_ENV=production
```

**Step 4: Deploy**
```bash
cd backend
git push heroku main
```

### Frontend Deployment

**Step 1: Create Heroku App**
```bash
heroku create firstaid-app
heroku buildpacks:add heroku/nodejs
```

**Step 2: Set Build Variable**
```bash
heroku config:set REACT_APP_API_URL=https://firstaid-api.herokuapp.com/api
```

**Step 3: Create Procfile**

**File: `frontend/Procfile`**
```
web: npm run build && npm start
```

**Step 4: Deploy**
```bash
cd frontend
git push heroku main
```

---

## 🌐 AWS Deployment

### Option A: Elastic Beanstalk

**Backend on Elastic Beanstalk:**
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 firstaid-backend

# Create environment
eb create firstaid-backend-env

# Deploy
eb deploy

# Open app
eb open
```

**Frontend on S3 + CloudFront:**
```bash
# Build
cd frontend
npm run build

# Create S3 bucket
aws s3 mb s3://firstaid-frontend

# Upload
aws s3 sync build/ s3://firstaid-frontend/

# Create CloudFront distribution
# (Through AWS Console or CLI)
```

### Option B: ECS (Elastic Container Service)

```bash
# Create ECR repositories
aws ecr create-repository --repository-name firstaid-backend
aws ecr create-repository --repository-name firstaid-frontend

# Build and push images
docker build -t firstaid-backend ./backend
docker tag firstaid-backend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/firstaid-backend:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/firstaid-backend:latest

# Deploy via ECS (through Console or CloudFormation)
```

---

## 🔧 Production Configuration

### Backend .env (Production)

```env
FLASK_ENV=production
FLASK_PORT=5000
JWT_SECRET_KEY=your-super-secret-production-key-change-this-123456
DATABASE_URL=postgresql://user:password@host:5432/firstaid
DEBUG=False
CORS_ORIGIN=https://yourdomain.com
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
MAX_UPLOAD_SIZE=50
LOG_LEVEL=INFO
```

### Frontend .env (Production)

```env
REACT_APP_API_URL=https://api.yourdomain.com/api
REACT_APP_ENV=production
REACT_APP_ENABLE_PHARMACY=true
REACT_APP_ENABLE_DERMATOLOGY=true
```

---

## 🔒 Production Security

### Backend Security

**1. Install Helmet (headers protection)**
```bash
pip install flask-limiter
pip install werkzeug-local-ssl
```

**2. Enable HTTPS**
```python
# In run.py
if __name__ == '__main__':
    app.run(ssl_context='adhoc')  # or with certificates
```

**3. Add Rate Limiting**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/pharmacy/scan', methods=['POST'])
@limiter.limit("10 per hour")
def scan():
    ...
```

**4. Update CORS**
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### Frontend Security

**1. Add Security Headers (via server)**
```nginx
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

**2. CSP Headers**
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;
```

**3. HTTPS Redirect**
```nginx
if ($scheme != "https") {
    return 301 https://$server_name$request_uri;
}
```

---

## 📊 Database Migration (Future)

When moving from JSON to SQL database:

### Step 1: Create Schema

```sql
CREATE TABLE medicines (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    generic_name VARCHAR(255),
    type VARCHAR(100),
    composition TEXT,
    usage TEXT,
    dosage TEXT,
    side_effects JSON,
    warnings JSON,
    interactions JSON,
    storage TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skin_diseases (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    scientific_name VARCHAR(255),
    description TEXT,
    causes JSON,
    symptoms JSON,
    treatments JSON,
    prevention JSON,
    severity VARCHAR(20),
    affected_areas JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pharmacy_scans (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    medicine_id VARCHAR(50),
    confidence FLOAT,
    extracted_text TEXT,
    image_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (medicine_id) REFERENCES medicines(id)
);

CREATE TABLE skin_analyses (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    disease_id VARCHAR(50),
    severity VARCHAR(20),
    confidence FLOAT,
    body_part VARCHAR(100),
    image_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (disease_id) REFERENCES skin_diseases(id)
);
```

### Step 2: Migrate Data

```python
import json
import psycopg2
from datetime import datetime

# Load JSON data
with open('database/medicines.json') as f:
    medicines = json.load(f)['medicines']

# Connect to PostgreSQL
conn = psycopg2.connect("dbname=firstaid user=postgres")
cur = conn.cursor()

# Migrate medicines
for med in medicines:
    cur.execute("""
        INSERT INTO medicines 
        (id, name, generic_name, type, composition, usage, dosage, side_effects, warnings, interactions, storage)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        med['id'],
        med['name'],
        med.get('generic_name'),
        med.get('type'),
        med.get('composition'),
        med.get('usage'),
        med.get('dosage'),
        json.dumps(med.get('side_effects', [])),
        json.dumps(med.get('warnings', [])),
        json.dumps(med.get('interactions', [])),
        med.get('storage')
    ))

conn.commit()
cur.close()
conn.close()
```

---

## 📈 Performance Optimization

### Backend Optimization

**1. Enable Caching**
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/api/pharmacy/medicine/<med_id>')
@cache.cached(timeout=3600)
def get_medicine(med_id):
    ...
```

**2. Database Indexing**
```sql
CREATE INDEX idx_medicines_name ON medicines(name);
CREATE INDEX idx_pharmacy_scans_user ON pharmacy_scans(user_id);
CREATE INDEX idx_skin_analyses_user ON skin_analyses(user_id);
```

**3. CDN for Static Files**
- Use CloudFlare or AWS CloudFront
- Cache images and CSS
- Minify JavaScript/CSS

### Frontend Optimization

**1. Code Splitting**
```javascript
const PharmacyPage = lazy(() => import('./pages/PharmacyPage'));
const DermatologyPage = lazy(() => import('./pages/DermatologyPage'));
```

**2. Image Optimization**
- Use WebP format
- Compress before upload
- Lazy load images

**3. Bundle Analysis**
```bash
npm install --save-dev webpack-bundle-analyzer
npm run analyze
```

---

## 🔄 Continuous Deployment (CI/CD)

### GitHub Actions Workflow

**File: `.github/workflows/deploy.yml`**
```yaml
name: Deploy FirstAid

on:
  push:
    branches: [main, production]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/production'
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
          heroku_app_name: "firstaid-api"
          heroku_email: "your@email.com"
```

---

## 🔍 Monitoring & Logging

### Backend Monitoring

**1. Enable Logging**
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.errorhandler(500)
def handle_error(e):
    logger.error(f"Server error: {str(e)}")
    return {'error': 'Internal server error'}, 500
```

**2. Add Sentry for Error Tracking**
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://xxx@sentry.io/xxx",
    integrations=[FlaskIntegration()]
)
```

### Frontend Monitoring

**1. Add Google Analytics**
```javascript
import ReactGA from 'react-ga';

ReactGA.initialize('GA_MEASUREMENT_ID');
ReactGA.pageview(window.location.pathname);
```

**2. Error Tracking with Rollbar**
```javascript
import Rollbar from 'rollbar';

const rollbar = new Rollbar({
  accessToken: 'your_post_server_item_token',
  environment: 'production'
});
```

---

## 📋 Deployment Checklist

Before going live:

### Security
- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] Environment variables secured
- [ ] Database credentials encrypted
- [ ] JWT secret changed
- [ ] Rate limiting enabled
- [ ] File upload validation
- [ ] Input sanitization

### Performance
- [ ] Caching enabled
- [ ] Database indexed
- [ ] Assets minified
- [ ] CDN configured
- [ ] Load testing passed
- [ ] Slow queries identified
- [ ] Images optimized

### Monitoring
- [ ] Error tracking setup
- [ ] Logs aggregation setup
- [ ] Performance monitoring
- [ ] Uptime monitoring
- [ ] Alert systems configured

### Backup
- [ ] Database backups automated
- [ ] File backups setup
- [ ] Disaster recovery plan
- [ ] Rollback procedure documented

### Documentation
- [ ] Deployment guide written
- [ ] Troubleshooting updated
- [ ] Team trained
- [ ] Runbooks created

---

## 🚨 Rollback Procedure

If deployment fails:

```bash
# Heroku Rollback
heroku releases
heroku rollback v10

# Docker Rollback
docker-compose down
git checkout previous-commit
docker-compose up -d

# AWS Rollback
aws elasticbeanstalk abort-environment-update --environment-name firstaid-prod
```

---

## 📞 Post-Deployment

After deployment:

1. **Verify Services**
   - [ ] Frontend loads
   - [ ] Backend responds
   - [ ] API endpoints working
   - [ ] Database connected
   - [ ] File uploads working

2. **Run Smoke Tests**
   - [ ] User registration
   - [ ] User login
   - [ ] Medicine scan
   - [ ] Skin analysis
   - [ ] View history

3. **Monitor Performance**
   - [ ] Check response times
   - [ ] Monitor error rates
   - [ ] Track user sessions
   - [ ] Check resource usage

4. **Notify Users**
   - [ ] Send announcement
   - [ ] Update status page
   - [ ] Monitor feedback

---

## 🎯 Scaling Strategies

### Horizontal Scaling
- Load balancer (Nginx, HAProxy)
- Multiple backend instances
- Database replication
- Redis cache cluster

### Vertical Scaling
- Increase instance size
- Upgrade server resources
- Optimize database queries

### Database Scaling
- Read replicas
- Sharding
- Connection pooling

---

## 📚 Additional Resources

- Docker Docs: https://docs.docker.com
- Heroku Docs: https://devcenter.heroku.com
- AWS Docs: https://docs.aws.amazon.com
- Flask Docs: https://flask.palletsprojects.com
- React Docs: https://react.dev

---

## ✅ Deployment Success

After completing deployment:
- ✅ Platform live and accessible
- ✅ All features working
- ✅ Users can register and login
- ✅ Scanning and analysis working
- ✅ Performance acceptable
- ✅ Monitoring active
- ✅ Backups running

---

**🎉 Congratulations! FirstAid is now in production!**

For issues, see deployment logs and monitoring dashboards.
