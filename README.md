# 🚀 Pharmyrus V5.0 - Railway Production

Brazilian Patent Intelligence Platform for Pharmaceutical Patents

## 📋 Quick Deploy to Railway

### 1️⃣ Prepare Repository
```bash
cd pharmyrus-v5-railway

# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit - Pharmyrus V5.0 Railway ready"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/pharmyrus-v5.git
git branch -M main
git push -u origin main
```

### 2️⃣ Deploy on Railway

#### Option A: Connect GitHub Repository (Recommended)
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository: `pharmyrus-v5`
4. Railway will auto-detect the Dockerfile
5. Click **"Deploy"**

#### Option B: Railway CLI
```bash
# Install Railway CLI (if not installed)
curl -fsSL https://railway.app/install.sh | sh

# Login
railway login

# Link to existing project (or create new)
railway link

# Deploy
railway up
```

### 3️⃣ Configure Environment (Optional)

Railway auto-injects `$PORT` variable. Additional variables can be set:

```bash
railway variables set LOG_LEVEL=info
railway variables set RAILWAY_ENVIRONMENT=production
```

### 4️⃣ Verify Deployment

```bash
# Get deployment URL
railway domain

# Check health endpoint
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "5.0.0",
  "timestamp": "2025-12-19T...",
  "port": 45612
}
```

### 5️⃣ Monitor Logs

```bash
railway logs --tail 100 --follow
```

Expected success logs:
```
Starting Container
INFO:     Started server process [1]
INFO:     Waiting for application startup.
🚀 Pharmyrus V5.0 Starting...
   Environment: production
   Port: 45612
   Version: 5.0.0
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:45612
```

## 🏗️ Project Structure

```
pharmyrus-v5-railway/
├── app/
│   └── main.py          # FastAPI application
├── Dockerfile           # Production Docker image
├── requirements.txt     # Python dependencies
├── railway.json         # Railway configuration
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🔌 API Endpoints

### Health & Status
- `GET /` - API information
- `GET /health` - Health check (used by Railway)
- `GET /api/v5/status` - API status and features

### Patent Search
- `POST /api/v5/search` - Search Brazilian patents for a molecule

Example request:
```bash
curl -X POST https://your-app.railway.app/api/v5/search \
  -H "Content-Type: application/json" \
  -d '{
    "nome_molecula": "Darolutamide",
    "nome_comercial": "Nubeqa",
    "pais_alvo": "BR"
  }'
```

### API Documentation
- `GET /docs` - Interactive Swagger UI
- `GET /redoc` - ReDoc documentation

## 🔧 Technical Details

### Runtime Configuration
- **Python**: 3.11-slim
- **Framework**: FastAPI 0.109.0
- **Server**: Uvicorn 0.27.0
- **Workers**: 1 (optimized for Railway)
- **Timeout**: 120s keep-alive
- **Port**: Dynamic (Railway injects `$PORT`)

### Health Check
- **Path**: `/health`
- **Interval**: 30s
- **Timeout**: 10s
- **Start Period**: 40s
- **Retries**: 3

### Dependencies
- FastAPI & Uvicorn (web framework)
- Pydantic (data validation)
- HTTPX & Requests (HTTP clients)
- Cloudscraper (web scraping)
- Firebase Admin (Firestore integration)
- Pandas (data processing)

## 🐛 Troubleshooting

### Build Fails
```bash
# Check Railway logs
railway logs --deployment

# Verify Dockerfile syntax
docker build -t pharmyrus-test .
```

### Health Check Fails
```bash
# Check if app is listening on correct port
railway logs | grep "Uvicorn running"

# Should show: Uvicorn running on http://0.0.0.0:XXXXX
```

### Port Issues
Railway automatically injects `$PORT` environment variable.
The Dockerfile CMD uses: `--port ${PORT:-8000}`

This expands to the actual port number (e.g., 45612).

## 📊 Next Steps

Once deployed successfully:
1. ✅ Verify `/health` endpoint responds
2. ✅ Test `/api/v5/search` with sample molecule
3. 🔄 Integrate PubChem API for molecule data
4. 🔄 Add EPO OPS API for patent families
5. 🔄 Implement Google Patents search
6. 🔄 Connect INPI crawler for BR patents
7. 🔄 Add Firestore for result caching

## 📞 Support

- **Issues**: Create issue on GitHub repository
- **Railway Docs**: https://docs.railway.app
- **API Docs**: https://your-app.railway.app/docs

---

**Version**: 5.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: 2025-12-19
