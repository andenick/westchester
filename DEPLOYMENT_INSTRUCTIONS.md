# Westchester County Data Platform - Complete Deployment Guide

**Last Updated**: October 17, 2025
**Status**: Ready for deployment after data collection complete
**Deployment Target**: Netlify (Frontend) + Render (Backend)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: Data Collection](#phase-1-data-collection-required)
3. [Phase 2: Pre-Deployment Setup](#phase-2-pre-deployment-setup)
4. [Phase 3: Backend Deployment (Render)](#phase-3-backend-deployment-render)
5. [Phase 4: Frontend Deployment (Netlify)](#phase-4-frontend-deployment-netlify)
6. [Phase 5: Domain Configuration](#phase-5-domain-configuration)
7. [Phase 6: Post-Deployment Testing](#phase-6-post-deployment-testing)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance & Updates](#maintenance--updates)

---

## Prerequisites

### Required Accounts
- [ ] **Render.com account** (free tier available)
- [ ] **Netlify account** (free tier available)
- [ ] **Domain registrar access** (Namecheap, Google Domains, etc.)
- [ ] **GitHub account** (optional, for auto-deploy)

### Required Software (Local Development)
- [ ] **Node.js** 18.17.0+ and npm 9.8.1+
- [ ] **Python** 3.11+ with pip
- [ ] **Git** (if using repository-based deployment)

### Required Information
- [ ] **Your domain name** (e.g., westchester-data.com)
- [ ] **Subdomain for API** (e.g., api.westchester-data.com)

---

## Phase 1: Data Collection (REQUIRED)

**Status**: ⚠️ BLOCKING - Must complete before deployment

### 1.1 Download Required PDFs

See `MANUAL_DOWNLOAD_WISHLIST.md` for complete list. Priority files:

#### Budget Documents (6 PDFs)
```
Source: https://www.westchestergov.com/county-budgets
Files:
- 2025_Adopted_Operating_Budget.pdf
- 2024_Adopted_Operating_Budget.pdf
- 2023_Adopted_Operating_Budget.pdf
- 2022_Adopted_Operating_Budget.pdf
- 2021_Adopted_Operating_Budget.pdf
- 2020_Adopted_Operating_Budget.pdf

Save to: Technical/data/raw/manual_downloads/budgets/
```

#### Financial Reports (10 PDFs)
```
Source: https://finance.westchestergov.com/?id=136&view=category
Files: Annual Comprehensive Financial Reports (ACFRs) 2015-2024

Save to: Technical/data/raw/manual_downloads/financial_reports/
```

#### Tax Municipal Profiles (50 PDFs)
```
Source: https://www.tax.ny.gov/research/property/reports.htm
Municipalities: Yonkers, White Plains, New Rochelle, Mount Vernon,
               Scarsdale, Greenburgh, Harrison, Port Chester,
               Mamaroneck, Rye
Years: 2020-2024 (5 years × 10 municipalities = 50 files)

Save to: Technical/data/raw/manual_downloads/tax_profiles/
```

#### GIS Tax Parcels (1 file - RE-DOWNLOAD)
```
Source: Westchester County GIS Portal
Current file corrupted - needs re-download
Format: CSV or GeoJSON

Save to: Technical/data/raw/WCGIS.tax-parcels.csv
```

### 1.2 Extract Data from PDFs

Run PDF extraction scripts (using Robert/DALM):

```bash
# Extract budget data
cd Technical/src/data_importers
python pdf_budget_extractor.py

# Extract financial reports
python pdf_financial_extractor.py

# Extract tax profiles
python pdf_tax_profile_extractor.py
```

### 1.3 Validate Extracted Data

```bash
# Run data validation
cd Technical/src/data_importers
python validate_extracted_data.py

# Verify no sample data remains
grep -r "SAMPLE DATA" Technical/src/frontend/src/pages/dashboards/
```

**✅ Completion Criteria**: All 10 dashboards show 100% real data, no sample data warnings.

---

## Phase 2: Pre-Deployment Setup

### 2.1 Local Production Build Test

#### Test Backend Build
```bash
cd D:/Arcanum/Projects/Westchester/Technical

# Install dependencies
pip install -r requirements.txt

# Test server starts
cd src/api
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Test health endpoint
curl http://localhost:8000/api/health

# Stop server (Ctrl+C)
```

#### Test Frontend Build
```bash
cd D:/Arcanum/Projects/Westchester/Technical/src/frontend

# Install dependencies
npm install

# Run production build
npm run build

# Preview production build
npm run preview

# Verify build output in dist/ folder
ls -lh dist/
```

**✅ Expected Output**:
- Backend: API running on port 8000, `/docs` accessible
- Frontend: Build completes successfully, `dist/` folder created (~1 MB)

### 2.2 Prepare Data Files for Upload

Render requires data files to be uploaded or stored on persistent disk.

**Option A: Include in Repository**
```bash
# Add small data files to git (< 100 MB)
# WARNING: Git has file size limits (100 MB per file, 1 GB total)
# Your data is 538+ MB - DO NOT commit large GeoJSON files
```

**Option B: Upload to Render Persistent Disk** (RECOMMENDED)
```
Data files to upload manually after deployment:
- Technical/data/raw/infrastructure/*.geojson (538 MB total)
- Technical/data/raw/demographics/*.json
- Technical/data/raw/transit/*.json
- Technical/data/raw/boundaries/*.geojson
```

### 2.3 Document Your Configuration

Create a deployment checklist:

```markdown
Deployment Configuration:
- Domain: __________________ (e.g., westchester-data.com)
- API Subdomain: __________________ (e.g., api.westchester-data.com)
- Netlify Site Name: __________________ (e.g., westchester-data)
- Render Service Name: __________________ (e.g., westchester-api)
- GitHub Repository: __________________ (if using)
```

---

## Phase 3: Backend Deployment (Render)

### 3.1 Create Render Account

1. Go to https://render.com
2. Sign up with GitHub/GitLab (recommended) or email
3. Verify email address

### 3.2 Create New Web Service

**Option A: From GitHub Repository** (Recommended)
```
1. Click "New +" → "Web Service"
2. Connect GitHub repository
3. Select Westchester project repository
4. Configure build settings (see below)
```

**Option B: Manual Deployment**
```
1. Click "New +" → "Web Service"
2. Choose "Deploy from public Git repository"
3. Or upload code manually as ZIP
```

### 3.3 Configure Build Settings

**In Render Dashboard**:

| Setting | Value |
|---------|-------|
| **Name** | `westchester-api` (or your choice) |
| **Region** | Oregon (or closest to your users) |
| **Branch** | `main` |
| **Root Directory** | `(leave blank if repo root)` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r Technical/requirements.txt` |
| **Start Command** | `cd Technical/src/api && uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | `Free` (or choose paid plan) |

### 3.4 Set Environment Variables

In Render Dashboard → Environment tab, add:

```env
ENVIRONMENT=production
DEBUG=false
PYTHON_VERSION=3.11.5
API_TITLE=Westchester County Data Platform API
API_VERSION=1.0.0

# CORS Origins - UPDATE WITH YOUR NETLIFY DOMAIN
CORS_ORIGINS=https://your-site.netlify.app,https://www.your-custom-domain.com

# Optional: Rate limiting, caching, etc.
ENABLE_CACHING=true
CACHE_TTL_SECONDS=3600
```

### 3.5 Configure Persistent Disk (for Data Files)

**Important**: Free tier includes 512 MB disk. Your data is 538+ MB.

**Option 1: Paid Plan with Larger Disk**
```
1. In Render Dashboard → Settings → Disks
2. Click "Add Disk"
3. Set size to 1 GB or more
4. Mount path: /opt/render/project/src/Technical/data
5. Save
```

**Option 2: Use External Storage** (S3, Google Cloud Storage)
```python
# Modify data loading in main.py to fetch from S3
import boto3
# ... load GeoJSON from S3 instead of local disk
```

**Option 3: Optimize Data Files** (Reduce file sizes)
```bash
# Simplify GeoJSON geometries to reduce size
python Technical/scripts/simplify_geojson.py
```

### 3.6 Upload Data Files to Render Disk

After disk is created:

```bash
# Using Render CLI
render disk upload westchester-data ./Technical/data/raw/infrastructure/

# OR: Manually via SSH (paid plans only)
# OR: Include in deployment if files are < 512 MB after optimization
```

### 3.7 Deploy Backend

1. Click "Create Web Service"
2. Render will build and deploy automatically
3. Wait for build to complete (~5-10 minutes)
4. Check deployment logs for errors

**✅ Success Indicators**:
- Build completes without errors
- Service shows "Live" status
- Health check endpoint responds: `https://your-app.onrender.com/api/health`

### 3.8 Test Backend API

```bash
# Get your Render URL (e.g., https://westchester-api.onrender.com)
RENDER_URL="https://your-app-name.onrender.com"

# Test health endpoint
curl $RENDER_URL/api/health

# Test API docs
curl $RENDER_URL/docs

# Test data endpoint
curl $RENDER_URL/api/planning/sidewalk-statistics
```

**Copy your Render URL** - you'll need it for frontend configuration.

---

## Phase 4: Frontend Deployment (Netlify)

### 4.1 Create Netlify Account

1. Go to https://netlify.com
2. Sign up with GitHub (recommended) or email
3. Verify email address

### 4.2 Create Production Environment File

**Locally**, create environment file for Netlify:

```bash
cd D:/Arcanum/Projects/Westchester/Technical/src/frontend

# Copy template
cp .env.production .env.production.local

# Edit with your Render URL
# Replace YOUR-RENDER-APP-NAME with actual Render service name
```

Edit `.env.production.local`:
```env
VITE_API_URL=https://YOUR-RENDER-APP-NAME.onrender.com
VITE_APP_NAME=Westchester County Data Platform
VITE_APP_VERSION=1.0.0
VITE_APP_ENVIRONMENT=production
```

### 4.3 Build Production Frontend Locally

```bash
cd Technical/src/frontend

# Build with production environment
npm run build

# Verify dist/ folder created
ls -lh dist/
# Expected: ~1 MB total (943 KB JS, 49 KB CSS)
```

### 4.4 Deploy to Netlify

**Option A: Drag-and-Drop Deployment** (Fastest for first deploy)
```
1. Go to https://app.netlify.com
2. Click "Add new site" → "Deploy manually"
3. Drag the dist/ folder to upload area
4. Wait for deployment (~1 minute)
5. Netlify assigns URL: https://random-name-12345.netlify.app
```

**Option B: Git-Based Deployment** (Recommended for updates)
```
1. Click "Add new site" → "Import an existing project"
2. Connect to GitHub repository
3. Configure build settings:
   - Base directory: Technical/src/frontend
   - Build command: npm run build
   - Publish directory: Technical/src/frontend/dist
4. Add environment variables (see below)
5. Deploy
```

### 4.5 Configure Netlify Environment Variables

In Netlify Dashboard → Site settings → Environment variables:

```env
VITE_API_URL=https://your-app-name.onrender.com
VITE_APP_NAME=Westchester County Data Platform
VITE_APP_VERSION=1.0.0
VITE_APP_ENVIRONMENT=production
```

**Important**: Click "Save" and trigger redeploy if you added variables after first deploy.

### 4.6 Configure Netlify Settings

**Build & Deploy Settings**:
- Continuous deployment: ON (if using Git)
- Build command: `npm run build`
- Publish directory: `Technical/src/frontend/dist`
- Node version: 18.17.0 (set in `netlify.toml`)

**Build Environment**:
- NODE_VERSION: `18.17.0`
- NPM_VERSION: `9.8.1`

### 4.7 Test Frontend Deployment

```bash
# Get your Netlify URL
NETLIFY_URL="https://your-site.netlify.app"

# Visit in browser
open $NETLIFY_URL

# Check all pages load:
# - Home page
# - Planning Dashboard
# - Infrastructure Dashboard
# - Data Catalog
# - All other dashboards
```

**✅ Success Indicators**:
- Site loads without errors
- API calls succeed (check browser console)
- Maps display correctly
- All 10 dashboards functional
- No CORS errors in console

---

## Phase 5: Domain Configuration

### 5.1 Configure Custom Domain on Netlify

**In Netlify Dashboard**:
```
1. Go to Site settings → Domain management
2. Click "Add custom domain"
3. Enter your domain: westchester-data.com
4. Click "Verify"
5. Netlify will provide DNS records to configure
```

**DNS Records Needed** (examples):
```
Type    Name    Value
A       @       75.2.60.5  (Netlify load balancer IP)
CNAME   www     your-site.netlify.app
```

### 5.2 Configure API Subdomain on Render

**In Render Dashboard**:
```
1. Go to your web service → Settings → Custom Domain
2. Click "Add Custom Domain"
3. Enter: api.westchester-data.com
4. Render provides CNAME record to add to DNS
```

**DNS Record** (example):
```
Type    Name    Value
CNAME   api     your-app.onrender.com
```

### 5.3 Update DNS at Domain Registrar

**Login to your domain registrar** (Namecheap, Google Domains, etc.):

```
Add DNS records:
1. A record:     @   →  75.2.60.5 (Netlify IP, may vary)
2. CNAME record: www →  your-site.netlify.app
3. CNAME record: api →  your-app.onrender.com
```

**Wait for DNS propagation** (5 minutes to 48 hours, typically 10-30 minutes).

### 5.4 Enable HTTPS/SSL

**Netlify** (automatic):
- Netlify auto-provisions Let's Encrypt SSL certificates
- HTTPS enabled automatically after DNS propagation
- Check Site settings → Domain management → HTTPS

**Render** (automatic):
- Render auto-provisions SSL for custom domains
- Check service → Settings → Custom Domain → SSL status

### 5.5 Update CORS Configuration

**After custom domain is live**, update backend CORS:

**In Render Dashboard** → Environment variables:
```env
# Update CORS_ORIGINS with your actual domains
CORS_ORIGINS=https://westchester-data.com,https://www.westchester-data.com,https://your-site.netlify.app
```

**Save and redeploy** Render service.

Alternatively, update `Technical/src/api/config.py`:
```python
manual_production_origins = [
    "https://westchester-data.com",
    "https://www.westchester-data.com",
    "https://your-site.netlify.app",
]
```

### 5.6 Force HTTPS Redirect

**In Netlify** (automatic):
- Enabled by default in Site settings → Domain management → HTTPS
- All HTTP traffic redirected to HTTPS

---

## Phase 6: Post-Deployment Testing

### 6.1 Functional Testing

**Test all dashboards**:
```
✅ Landing Page
✅ Overview Dashboard
✅ Demographics Dashboard
✅ Transit Dashboard
✅ Infrastructure Dashboard
✅ Historical Trends Dashboard
✅ Municipality Comparison Dashboard
✅ Municipal Services Dashboard
✅ Budget Dashboard (must show 100% real data)
✅ Property Tax Dashboard (must show 100% real data)
```

### 6.2 Performance Testing

**Page Load Times**:
```bash
# Test with Lighthouse (Chrome DevTools)
# Target: Performance score > 80
# First Contentful Paint < 2 seconds
# Time to Interactive < 5 seconds
```

**API Response Times**:
```bash
# Test API endpoints
time curl https://api.westchester-data.com/api/planning/sidewalk-statistics
# Target: < 1 second
```

### 6.3 Browser Compatibility Testing

Test in multiple browsers:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

### 6.4 Mobile Responsiveness Testing

Test on mobile devices:
- [ ] iPhone (Safari)
- [ ] Android (Chrome)
- [ ] Tablet (iPad, Android tablet)

**Test viewport sizes**:
- 375px (phone)
- 768px (tablet)
- 1024px (desktop)
- 1920px (large desktop)

### 6.5 Data Accuracy Validation

**Verify real data**:
```
✅ No "SAMPLE DATA" warnings anywhere
✅ Budget data matches source PDFs
✅ Tax data matches municipal profiles
✅ Demographics match Census API
✅ Infrastructure counts match OpenStreetMap
✅ Transit stations match GTFS data
```

### 6.6 Error Monitoring Setup (Optional but Recommended)

**Sentry** (free tier available):
```bash
# Add Sentry to frontend
cd Technical/src/frontend
npm install @sentry/react

# Add to main.tsx
import * as Sentry from "@sentry/react";
Sentry.init({
  dsn: "YOUR_SENTRY_DSN",
  environment: "production",
});
```

**Render Logging**:
- Check Render Dashboard → Logs for backend errors
- Set up log retention in Render settings

---

## Troubleshooting

### Issue: Frontend Can't Connect to Backend

**Symptoms**: CORS errors in browser console, API calls failing

**Solutions**:
1. Verify CORS_ORIGINS environment variable includes your Netlify domain
2. Check Render service is "Live" and responding to health checks
3. Verify VITE_API_URL in Netlify environment variables is correct
4. Check for HTTPS mismatch (frontend HTTPS → backend HTTP won't work)

### Issue: Large GeoJSON Files Not Loading

**Symptoms**: Infrastructure dashboard blank, console shows 404 or timeout

**Solutions**:
1. Verify data files uploaded to Render persistent disk
2. Check disk mount path matches DATA_DIR in main.py
3. Optimize GeoJSON files (simplify geometries, reduce precision)
4. Consider serving large files from CDN (S3, CloudFront)

### Issue: Build Fails on Netlify

**Symptoms**: "Build failed" message, red X in Netlify dashboard

**Solutions**:
1. Check build logs for specific error messages
2. Verify Node version matches requirements (18.17.0+)
3. Run `npm run build` locally to reproduce error
4. Check for missing environment variables
5. Ensure TypeScript compilation passes (run `npx tsc` locally)

### Issue: Build Fails on Render

**Symptoms**: Render service stuck in "Building" or shows "Failed"

**Solutions**:
1. Check build logs in Render dashboard
2. Verify requirements.txt includes all dependencies
3. Check Python version (3.11+)
4. Test `pip install -r requirements.txt` locally
5. Verify start command is correct

### Issue: Slow API Response Times

**Symptoms**: Dashboards take > 5 seconds to load data

**Solutions**:
1. Enable caching in Render environment variables:
   ```env
   ENABLE_CACHING=true
   CACHE_TTL_SECONDS=3600
   ```
2. Upgrade Render plan for more resources
3. Optimize database queries (if using database)
4. Pre-generate static data files for common queries

### Issue: SSL Certificate Errors

**Symptoms**: "Not Secure" warning in browser, HTTPS not working

**Solutions**:
1. Wait for DNS propagation (up to 48 hours)
2. Check DNS records are correct
3. Verify custom domain is added in Netlify/Render dashboards
4. Force SSL renewal in platform dashboards
5. Check for mixed content warnings (HTTP resources on HTTPS page)

---

## Maintenance & Updates

### Regular Updates

**Weekly**:
- Check Render and Netlify logs for errors
- Monitor uptime and performance metrics
- Review user feedback (if available)

**Monthly**:
- Update dependencies (npm, pip packages)
- Review and update data sources
- Check for security updates

**Quarterly**:
- Collect new PDF documents (budgets, financial reports)
- Re-run data extraction and validation
- Update dashboards with latest data
- Review and optimize performance

### Updating the Application

**Frontend Updates**:
```bash
# Make changes locally
cd Technical/src/frontend
# ... edit files ...

# Test locally
npm run dev

# Build and test production build
npm run build
npm run preview

# Deploy to Netlify
# Git-based: Push to GitHub (auto-deploys)
# Manual: Upload dist/ folder to Netlify
```

**Backend Updates**:
```bash
# Make changes locally
cd Technical/src/api
# ... edit files ...

# Test locally
python -m uvicorn main:app --reload

# Deploy to Render
# Git-based: Push to GitHub (auto-deploys)
# Manual: Re-deploy in Render dashboard
```

### Data Updates

**When new PDFs are available**:
```bash
# Download new documents
# Save to Technical/data/raw/manual_downloads/

# Extract data
cd Technical/src/data_importers
python pdf_budget_extractor.py
python pdf_financial_extractor.py

# Validate
python validate_extracted_data.py

# Redeploy backend (if data structure changed)
# Frontend will automatically fetch new data via API
```

### Backup Strategy

**Code Backups**:
- Use Git with remote repository (GitHub, GitLab)
- Tag releases: `git tag v1.0.0 && git push --tags`

**Data Backups**:
```bash
# Backup extracted data
cd Technical/data/processed
tar -czf backup_$(date +%Y%m%d).tar.gz *.json *.csv

# Backup to cloud storage
# AWS S3: aws s3 cp backup.tar.gz s3://your-bucket/
# Google Drive: rclone copy backup.tar.gz gdrive:backups/
```

**Configuration Backups**:
- Document all environment variables
- Export Netlify configuration
- Export Render configuration

---

## Success Checklist

### Pre-Launch
- [ ] All ~70 PDF documents collected and processed
- [ ] Budget dashboard shows 100% real data
- [ ] Property Tax dashboard shows 100% real data
- [ ] Production build successful locally (frontend + backend)
- [ ] All TypeScript compilation errors resolved
- [ ] Data files prepared for upload (538+ MB)

### Backend Deployment (Render)
- [ ] Render account created
- [ ] Web service created and configured
- [ ] Environment variables set (CORS_ORIGINS, etc.)
- [ ] Persistent disk created and data uploaded
- [ ] Build successful, service shows "Live"
- [ ] Health endpoint responding: /api/health
- [ ] API docs accessible: /docs
- [ ] Test endpoints return correct data

### Frontend Deployment (Netlify)
- [ ] Netlify account created
- [ ] Site created and deployed
- [ ] Environment variables set (VITE_API_URL)
- [ ] Build successful, site shows "Published"
- [ ] Site loads in browser
- [ ] All dashboards functional
- [ ] No CORS errors in console
- [ ] Maps display correctly

### Domain Configuration
- [ ] Custom domain added to Netlify
- [ ] API subdomain added to Render
- [ ] DNS records configured at registrar
- [ ] SSL certificates active (HTTPS)
- [ ] CORS updated with custom domains
- [ ] HTTP → HTTPS redirect working

### Post-Deployment
- [ ] All 10 dashboards tested and functional
- [ ] Performance targets met (page load < 3 sec)
- [ ] Mobile responsiveness verified
- [ ] Browser compatibility tested (Chrome, Firefox, Safari, Edge)
- [ ] Data accuracy validated (no sample data)
- [ ] Error monitoring configured (Sentry, etc.)
- [ ] Backup strategy implemented

### Documentation
- [ ] Deployment configuration documented
- [ ] Environment variables documented
- [ ] Maintenance procedures documented
- [ ] Contact information for support documented

---

## Support & Resources

### Platform Documentation
- **Netlify Docs**: https://docs.netlify.com
- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev
- **Vite Docs**: https://vitejs.dev

### Project Documentation
- `README.md` - Project overview
- `HANDOFF_DOCUMENTATION.md` - Complete project status
- `MANUAL_DOWNLOAD_WISHLIST.md` - Data collection checklist
- `Technical/DEPLOYMENT.md` - Technical deployment notes
- `Technical/PRODUCTION_STATUS.md` - Build status

### Contact Information
- **Project Lead**: (Your name/email)
- **Technical Support**: (Support contact)
- **Domain Registrar**: (Support URL)

---

**Deployment Prepared By**: AI Agent - Westchester Data Platform
**Date**: October 17, 2025
**Next Action**: Complete Phase 1 (Data Collection), then proceed with deployment phases
**Estimated Time to Production**: 2-3 weeks (depending on data collection speed)
