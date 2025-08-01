# NuiFlo WorkForce API - Deployment Guide

## 🚀 **Recommended: Railway Deployment**

Railway is the best choice for development deployment with minimal setup and cost.

### **Step 1: Setup Railway Account**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Get $5/month free credit

### **Step 2: Deploy from GitHub**
1. **Push your code** to GitHub repository
2. **Connect Railway** to your GitHub repo
3. **Select** the `workforce_api` folder as root
4. **Railway auto-detects** Python and installs dependencies

### **Step 3: Configure Environment Variables**
In Railway dashboard, add these environment variables:

```bash
# Database (keep your existing Supabase)
DB_USER=postgres.pyuwxaocmnbaipqjdlrv
DB_PASSWORD=%4044FerryDock  
DB_HOST=aws-0-ap-southeast-2.pooler.supabase.com
DB_PORT=5432
DB_NAME=postgres

# App Configuration
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=["https://your-frontend-domain.com", "http://localhost:5173"]

# Railway provides PORT automatically
```

### **Step 4: Custom Domain (Optional)**
- Railway provides: `https://your-app-name.railway.app`
- Add custom domain in Railway dashboard
- SSL certificate included automatically

---

## 🎯 **Alternative Platforms:**

### **Render Deployment**
```yaml
# render.yaml
services:
  - type: web
    name: nuiflo-workforce-api
    env: python
    buildCommand: "pip install uv && uv pip install --system -r pyproject.toml"
    startCommand: "uvicorn workforce_api.main:app --host 0.0.0.0 --port $PORT"
    plan: free
    healthCheckPath: /health/ping
```

### **Fly.io Deployment**
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch --no-deploy
fly deploy
```

### **DigitalOcean App Platform**
- **Connect GitHub repo**
- **Select Python** as runtime
- **Set build command**: `pip install uv && uv pip install --system -r pyproject.toml`
- **Set run command**: `uvicorn workforce_api.main:app --host 0.0.0.0 --port $PORT`

---

## 🔧 **Environment Configuration**

### **Production Environment Variables:**
```bash
# Required
DB_USER=your_supabase_user
DB_PASSWORD=your_encoded_password
DB_HOST=your_supabase_host
DB_PORT=5432
DB_NAME=postgres

# Optional - Alternative to individual DB vars
DATABASE_URL=postgresql+psycopg2://user:pass@host:port/db

# App Config
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=["https://your-frontend.com"]
PORT=8000  # Usually auto-set by platform
```

### **Development vs Production:**
```bash
# Development (.env file)
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Production (platform environment variables)  
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=["https://your-app.vercel.app"]
```

---

## 🛠️ **Deployment Files Included:**

- ✅ `railway.json` - Railway configuration
- ✅ `Procfile` - Process configuration (Heroku-style)
- ✅ `Dockerfile` - Container deployment
- ✅ `.dockerignore` - Exclude unnecessary files
- ✅ Updated `config.py` - Production environment support

---

## 📋 **Pre-Deployment Checklist:**

- [ ] Code pushed to GitHub repository
- [ ] Environment variables configured
- [ ] Database (Supabase) accessible from internet
- [ ] CORS origins updated for production domain
- [ ] Health check endpoint working (`/health/ping`)

---

## 🔗 **Post-Deployment:**

### **1. Test Deployment:**
```bash
# Replace with your deployed URL
curl https://your-app.railway.app/health/status
curl https://your-app.railway.app/api/v1/teams/
```

### **2. Update Frontend:**
```typescript
// Update your frontend API base URL
const API_BASE_URL = "https://your-app.railway.app";
```

### **3. Update Swagger Documentation:**
Your API docs will be available at:
- `https://your-app.railway.app/docs`
- `https://your-app.railway.app/openapi.json`

---

## 💰 **Cost Estimates:**

| Platform | Free Tier | Paid Tier | Notes |
|----------|-----------|-----------|--------|
| **Railway** | $5/month credit | $5-20/month | Best for development |
| **Render** | Free tier available | $7/month | Good performance |
| **Fly.io** | 3 free VMs | $2-10/month | Global edge deployment |
| **DigitalOcean** | No free tier | $5/month | Simple and reliable |

**Recommendation**: Start with Railway's free credit, then migrate to AWS/Azure when ready for production scaling.

---

## 🚨 **Important Notes:**

1. **Keep Supabase**: Your existing database works perfectly with any deployment platform
2. **Environment Variables**: Never commit sensitive data like passwords to Git
3. **CORS Configuration**: Update allowed origins for your frontend domain
4. **Health Checks**: All platforms support `/health/ping` for monitoring
5. **SSL/HTTPS**: Automatically provided by all recommended platforms

Ready to deploy! 🚀 