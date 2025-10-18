# Westchester County Data Platform - Quick Start Deployment

**Fast-track guide for deploying to Netlify + Render**

---

## TL;DR - What You Need

1. **~70 PDF documents** downloaded and processed (see Phase 1)
2. **Domain name** for your website
3. **Netlify account** (free)
4. **Render account** (free or paid for larger data storage)
5. **30 minutes** for deployment (after data is ready)

---

## 5-Phase Deployment Process

### Phase 1: Data Collection (BLOCKING)
**Time**: 1-2 weeks | **Status**: ⚠️ REQUIRED BEFORE DEPLOYMENT

```bash
# Download ~70 PDFs from:
- Westchester County budget office (6 budget PDFs)
- Finance department (10 financial reports)
- NY State tax office (50 tax profiles)
- County GIS portal (1 parcel dataset)

# Save to:
Technical/data/raw/manual_downloads/
```

**Use Robert/DALM to extract data**:
```bash
cd Technical/src/data_importers
python pdf_budget_extractor.py
python validate_extracted_data.py
```

**✅ Done when**: All dashboards show 100% real data, no sample data warnings

---

### Phase 2: Backend Deployment (Render)
**Time**: 10-15 minutes | **Prerequisites**: Phase 1 complete

1. **Create Render account**: https://render.com → Sign up

2. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Choose "Public Git Repository" or upload manually

3. **Configure**:
   ```
   Name: westchester-api
   Build Command: pip install -r Technical/requirements.txt
   Start Command: cd Technical/src/api && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Set Environment Variables**:
   ```env
   ENVIRONMENT=production
   CORS_ORIGINS=https://your-site.netlify.app,https://your-domain.com
   ```

5. **Add Persistent Disk** (for 538+ MB data files):
   - Settings → Disks → Add Disk
   - Size: 1 GB
   - Mount: `/opt/render/project/src/Technical/data`

6. **Deploy**: Click "Create Web Service"

7. **Copy your Render URL**: `https://your-app.onrender.com`

**✅ Test**: Visit `https://your-app.onrender.com/api/health`

---

### Phase 3: Frontend Deployment (Netlify)
**Time**: 5-10 minutes | **Prerequisites**: Phase 2 complete

1. **Build Production Frontend**:
   ```bash
   cd Technical/src/frontend

   # Create .env.production.local
   echo "VITE_API_URL=https://your-app.onrender.com" > .env.production.local

   # Build
   npm run build
   ```

2. **Deploy to Netlify**:
   - Go to https://app.netlify.com
   - "Add new site" → "Deploy manually"
   - Drag `Technical/src/frontend/dist` folder
   - Or: Connect GitHub for auto-deploy

3. **Set Environment Variables** (Netlify dashboard):
   ```env
   VITE_API_URL=https://your-app.onrender.com
   VITE_APP_NAME=Westchester County Data Platform
   ```

4. **Copy your Netlify URL**: `https://random-name.netlify.app`

**✅ Test**: Visit your Netlify URL, verify dashboards load

---

### Phase 4: Domain Setup
**Time**: 5 minutes + DNS propagation (10-30 min) | **Prerequisites**: Phase 3 complete

1. **Add Custom Domain to Netlify**:
   - Site settings → Domain management → Add custom domain
   - Enter: `westchester-data.com` (your domain)

2. **Add API Subdomain to Render**:
   - Service → Settings → Custom Domain
   - Enter: `api.westchester-data.com`

3. **Configure DNS at Your Registrar**:
   ```
   A     @     75.2.60.5                      (Netlify IP)
   CNAME www   your-site.netlify.app          (Netlify)
   CNAME api   your-app.onrender.com          (Render)
   ```

4. **Update CORS in Render**:
   - Environment → `CORS_ORIGINS`
   - Add: `https://westchester-data.com,https://www.westchester-data.com`

5. **Wait for DNS** (10-30 minutes)

**✅ Test**: Visit `https://your-domain.com`, `https://api.your-domain.com/api/health`

---

### Phase 5: Final Validation
**Time**: 10 minutes | **Prerequisites**: Phase 4 complete

**Test Checklist**:
- [ ] All 10 dashboards load (no errors)
- [ ] No "SAMPLE DATA" warnings anywhere
- [ ] Maps display correctly
- [ ] Data exports work (Budget, Tax dashboards)
- [ ] Mobile responsive (test on phone)
- [ ] HTTPS active (green lock icon)
- [ ] API calls succeed (check browser console)

**Performance Check**:
```bash
# Page load time < 3 seconds?
# API response time < 1 second?
```

**Go Live**! 🚀

---

## File Checklist

### Configuration Files Created (✅ Already done)
- [x] `netlify.toml` - Netlify deployment config
- [x] `render.yaml` - Render deployment config
- [x] `.env.production` - Production environment template
- [x] `config.py` - Backend CORS configuration
- [x] `DEPLOYMENT_INSTRUCTIONS.md` - Complete deployment guide (comprehensive)
- [x] `pdf_budget_extractor.py` - PDF extraction script
- [x] `validate_extracted_data.py` - Data validation script

### Files You Need to Create
- [ ] `.env.production.local` - Your actual production environment (don't commit!)
- [ ] Budget JSON files (via `pdf_budget_extractor.py`)
- [ ] Tax JSON files (via PDF extraction)

---

## Common Issues & Quick Fixes

### Issue: Frontend Can't Connect to Backend
```bash
# Fix: Check CORS configuration
# In Render → Environment → CORS_ORIGINS
# Must include your Netlify domain
```

### Issue: Build Fails on Netlify
```bash
# Fix: Check Node version
# In netlify.toml → NODE_VERSION=18.17.0
```

### Issue: Data Files Not Loading
```bash
# Fix: Verify Render persistent disk is mounted
# Service → Settings → Disks → Mount path correct?
```

### Issue: SSL Not Working
```bash
# Fix: Wait for DNS propagation (up to 48 hours)
# Force SSL renewal in Netlify/Render dashboard
```

---

## Quick Commands Reference

### Local Development
```bash
# Backend
cd Technical/src/api
python -m uvicorn main:app --reload

# Frontend
cd Technical/src/frontend
npm run dev
```

### Production Build
```bash
# Frontend
cd Technical/src/frontend
npm run build

# Backend (no build needed, deployed directly)
```

### Data Extraction
```bash
# Extract budget data
cd Technical/src/data_importers
python pdf_budget_extractor.py

# Validate
python validate_extracted_data.py
```

### Deployment
```bash
# Netlify (manual)
cd Technical/src/frontend/dist
# Upload to Netlify dashboard

# Render (manual)
# Upload code via Render dashboard
```

---

## Cost Estimate

**Free Tier** (for initial launch):
- Netlify: FREE (100 GB bandwidth, 300 build minutes/month)
- Render: FREE (512 MB disk, 750 hours/month)
- **Total**: $0/month

**Recommended Tier** (for production):
- Netlify Pro: $19/month (better performance, more bandwidth)
- Render Standard: $7/month (1 GB disk, better uptime)
- Domain: ~$12/year
- **Total**: ~$26/month + $12/year

---

## Support & Resources

**Complete Guides**:
- `DEPLOYMENT_INSTRUCTIONS.md` - Full deployment guide (70 pages)
- `HANDOFF_DOCUMENTATION.md` - Project status and context
- `MANUAL_DOWNLOAD_WISHLIST.md` - Data collection checklist

**Platform Docs**:
- Netlify: https://docs.netlify.com
- Render: https://render.com/docs

**Need Help?**
1. Check `DEPLOYMENT_INSTRUCTIONS.md` Troubleshooting section
2. Review platform logs (Netlify/Render dashboards)
3. Check browser console for errors
4. Verify all environment variables are set correctly

---

## Timeline

| Phase | Time | Can Start When |
|-------|------|----------------|
| Phase 1 (Data) | 1-2 weeks | Immediately |
| Phase 2 (Backend) | 10-15 min | Phase 1 done |
| Phase 3 (Frontend) | 5-10 min | Phase 2 done |
| Phase 4 (Domain) | 5 min + wait | Phase 3 done |
| Phase 5 (Validation) | 10 min | Phase 4 done |
| **Total** | **2-3 weeks** | - |

**Critical Path**: Data collection (Phase 1) is the bottleneck.

---

**Ready to Deploy?**

1. ✅ Complete Phase 1 (collect & process ~70 PDFs)
2. ✅ Create Render account
3. ✅ Create Netlify account
4. ✅ Have domain ready
5. ✅ Follow phases 2-5 sequentially

**Questions?** See `DEPLOYMENT_INSTRUCTIONS.md` for detailed explanations.

---

**Last Updated**: October 17, 2025
**Status**: Ready for deployment after Phase 1 data collection complete
