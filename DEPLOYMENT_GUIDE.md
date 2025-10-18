# Deployment Guide: Westchester County Data Platform

## Standardized FREE Tech Stack for All Projects

This guide documents the recommended deployment stack for all interactive data visualization projects. This stack costs **$0/month** and scales to support unlimited projects.

---

## 🎯 Tech Stack Overview

### Frontend Hosting: **Netlify**
- **Cost:** FREE (100GB bandwidth/month, unlimited sites)
- **Features:** Auto-deploy from GitHub, CDN, SSL, custom domains
- **Best for:** React/Vite applications, static sites

### Backend API: **Render.com**
- **Cost:** FREE (750 hours/month per service)
- **Features:** Auto-deploy from GitHub, environment variables, SSL
- **Best for:** FastAPI, Node.js, Python backends

### Domain Management: **Namecheap**
- **Cost:** ~$10-15/year per domain
- **Features:** DNS management, CNAME records, SSL support

---

## 📦 Frontend Stack

### Technologies
- **Framework:** React 19+ with TypeScript
- **Build Tool:** Vite 7+
- **Styling:** Tailwind CSS 3.4+
- **Maps:** Leaflet + React-Leaflet
- **Charts:** Recharts
- **HTTP Client:** Axios
- **Routing:** React Router DOM

### Project Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── charts/         # Reusable chart components
│   │   ├── map/            # Map components
│   │   └── common/         # Shared UI components
│   ├── pages/
│   │   └── dashboards/     # Dashboard pages
│   ├── services/
│   │   └── api.ts          # API client
│   ├── types/              # TypeScript types
│   └── App.tsx
├── public/
├── dist/                   # Build output
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── netlify.toml            # Netlify configuration
```

---

## 🔧 Backend Stack

### Technologies
- **Framework:** FastAPI (Python)
- **Server:** Uvicorn
- **Data Processing:** Pandas, NumPy
- **Data Sources:** Census API, GTFS, OpenStreetMap, NY State Open Data

### Project Structure
```
api/
├── main.py                 # FastAPI app
├── requirements.txt        # Python dependencies
├── data/
│   ├── raw/               # Downloaded data
│   └── processed/         # Processed datasets
└── src/
    ├── data_importers/    # Data fetching scripts
    └── processors/        # Data processing logic
```

---

## 🚀 Deployment Workflow

### Step 1: Prepare Your Repository

**File Structure:**
```
your-project/
├── Technical/
│   ├── src/
│   │   ├── api/           # Backend
│   │   └── frontend/      # Frontend
│   └── scripts/
└── README.md
```

**Ensure .gitignore includes:**
```
# Dependencies
node_modules/
__pycache__/

# Environment variables
.env
.env.local
.env.production

# Build outputs
dist/
build/

# Data files (large)
data/raw/*.csv
data/raw/*.json
```

### Step 2: Deploy Backend to Render.com

1. **Sign up at https://render.com** (use GitHub OAuth)

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Select your repo

3. **Configure Service:**
   ```
   Name: your-project-api
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Root Directory: Technical/src/api
   ```

4. **Add Environment Variables:**
   - Go to "Environment" tab
   - Add all API keys and secrets:
     - `CENSUS_API_KEY`
     - `NY_STATE_APP_TOKEN`
     - `NY_STATE_SECRET_TOKEN`
     - etc.

5. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment (~2-3 minutes)
   - Copy the URL (e.g., `https://your-project-api.onrender.com`)

6. **Test API:**
   ```bash
   curl https://your-project-api.onrender.com/api/health
   ```

### Step 3: Deploy Frontend to Netlify

1. **Sign up at https://netlify.com** (use GitHub OAuth)

2. **Create netlify.toml in frontend directory:**
   ```toml
   [build]
     command = "npm run build"
     publish = "dist"

   [[redirects]]
     from = "/api/*"
     to = "https://your-project-api.onrender.com/api/:splat"
     status = 200
     force = true

   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200
   ```

3. **Update API URL in code:**
   
   In `src/services/api.ts`:
   ```typescript
   const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
   ```
   
   This automatically uses production URL when deployed.

4. **Deploy to Netlify:**
   - Click "New site from Git"
   - Choose GitHub repository
   - Configure:
     ```
     Base directory: Technical/src/frontend
     Build command: npm run build
     Publish directory: dist
     ```
   - Click "Deploy site"

5. **Get Netlify URL:**
   - Example: `https://your-project.netlify.app`

### Step 4: Configure Custom Domain

**Option A: Subdomain (e.g., westchester.nycvisualizer.com)**

1. **In Namecheap DNS:**
   - Type: CNAME Record
   - Host: `westchester`
   - Value: `your-project.netlify.app`
   - TTL: Automatic

2. **In Netlify:**
   - Go to "Domain settings"
   - Click "Add custom domain"
   - Enter: `westchester.nycvisualizer.com`
   - Netlify will auto-configure SSL (takes ~24 hours)

**Option B: Root Domain (e.g., projectname.com)**

1. **In Namecheap DNS:**
   - Type: A Record
   - Host: `@`
   - Value: Get from Netlify (usually `75.2.60.5`)
   - Add CNAME for `www` → `your-project.netlify.app`

2. **In Netlify:**
   - Add custom domain
   - Enable SSL (automatic)

### Step 5: Continuous Deployment

Both Netlify and Render auto-deploy on every push to your main branch:

1. **Make code changes locally**
2. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Update dashboard"
   git push origin main
   ```
3. **Automatic deployment happens:**
   - Netlify rebuilds frontend (~1-2 min)
   - Render rebuilds backend (~2-3 min)

---

## 🔐 Environment Variables

### Development (.env.local)
```env
VITE_API_URL=http://localhost:8000
```

### Production (Netlify Environment Variables)
```env
VITE_API_URL=https://your-project-api.onrender.com
```

### Backend (Render Environment Variables)
```env
CENSUS_API_KEY=your_census_key
NY_STATE_APP_TOKEN=your_token
NY_STATE_SECRET_TOKEN=your_secret
```

---

## 🔄 CORS Configuration

**In FastAPI (main.py):**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-project.netlify.app",
        "https://westchester.nycvisualizer.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Multiple Projects Setup

### Example: 3 Different County Platforms

**Backend Services (Render):**
- `westchester-api.onrender.com`
- `bronx-api.onrender.com`
- `queens-api.onrender.com`

**Frontend Sites (Netlify):**
- `westchester.nycvisualizer.com`
- `bronx.nycvisualizer.com`
- `queens.nycvisualizer.com`

**Cost: $0/month for all 3 projects!**

---

## 🐛 Troubleshooting

### Frontend Build Fails
- Check `package.json` scripts
- Ensure all dependencies are in `package.json`
- Check TypeScript errors: `npm run build` locally

### Backend Won't Start
- Check `requirements.txt` has all dependencies
- Verify start command uses `$PORT` variable
- Check logs in Render dashboard

### API Calls Failing
- Verify CORS configuration
- Check API URL in frontend code
- Test backend directly: `curl https://api-url/api/health`

### SSL Certificate Issues
- Wait 24 hours for DNS propagation
- Verify DNS records in Namecheap
- Check Netlify SSL status

---

## 🎯 Performance Optimization

### Frontend
- Code splitting: Use `React.lazy()` for route components
- Image optimization: Use WebP format, lazy loading
- Bundle analysis: `npm run build -- --mode analyze`

### Backend
- Caching: Implement Redis for frequently accessed data
- Database indexing: If using PostgreSQL
- Compression: Gzip responses

---

## 📈 Monitoring

### Netlify Analytics (FREE)
- Page views
- Bandwidth usage
- Top pages

### Render Metrics (FREE)
- CPU usage
- Memory usage
- Response times
- Logs

---

## 🔄 When to Upgrade

**Netlify:**
- Exceeding 100GB/month bandwidth → Upgrade to Pro ($19/month)
- Need more team members → Pro plan

**Render:**
- Need always-on service (>750 hrs/month) → Starter ($7/month)
- Need more resources → Professional ($25/month)

---

## 🎉 Benefits of This Stack

✅ **FREE** for unlimited small-medium projects  
✅ **Auto-deployment** from GitHub  
✅ **SSL** certificates included  
✅ **CDN** for fast global delivery  
✅ **Scalable** - upgrade only when needed  
✅ **Professional** - production-ready infrastructure  
✅ **Simple** - no DevOps expertise required  

---

## 📚 Additional Resources

- [Netlify Documentation](https://docs.netlify.com)
- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Vite Documentation](https://vitejs.dev)
- [React Documentation](https://react.dev)

