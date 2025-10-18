# Render Configuration Guide for Your GitHub Repository
## Westchester County Data Platform

**Your GitHub Repository**: https://github.com/andenick/westchester
**Render Account**: Connected to YouTube account
**Service Type**: Free tier

---

## Current Situation

You have:
- ✅ Render account created and connected to GitHub
- ✅ GitHub repository: `andenick/westchester`
- ✅ Free Render service started
- ⚠️ Local project NOT yet pushed to GitHub
- ⚠️ Render service needs configuration

---

## Step 1: Prepare Local Project for Git (5 minutes)

### 1.1 Initialize Git Repository

Open Command Prompt or PowerShell and navigate to project:

```bash
cd D:\Arcanum\Projects\Westchester
```

Initialize Git:

```bash
git init
```

### 1.2 Configure Git User (First Time Only)

If you haven't configured Git before:

```bash
git config --global user.name "andenick"
git config --global user.email "your-email@example.com"
```

Replace `your-email@example.com` with the email you use for GitHub.

### 1.3 Add All Project Files

```bash
git add .
```

This stages all files for commit.

### 1.4 Create Initial Commit

```bash
git commit -m "Initial commit - Westchester County Data Platform"
```

### 1.5 Connect to Your GitHub Repository

```bash
git remote add origin https://github.com/andenick/westchester.git
```

### 1.6 Set Main Branch

```bash
git branch -M main
```

### 1.7 Push to GitHub

```bash
git push -u origin main
```

**If prompted for authentication**:
- GitHub now requires Personal Access Token (not password)
- Follow instructions in Step 1.8 below if push fails

### 1.8 Create GitHub Personal Access Token (If Needed)

If git push fails with authentication error:

1. Go to GitHub: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Note: `Westchester Deployment`
4. Expiration: 90 days (or longer)
5. Select scopes:
   - ✅ `repo` (Full control of private repositories)
6. Click "Generate token"
7. **COPY THE TOKEN IMMEDIATELY** (you won't see it again!)
8. Use token as password when git push asks for credentials

---

## Step 2: Configure Render Web Service (10 minutes)

### 2.1 Access Your Render Service

1. Go to https://dashboard.render.com
2. You should see your service listed
3. Click on the service name

**If you haven't created the service yet**:
1. Click "New +" → "Web Service"
2. Select your GitHub repository: `andenick/westchester`
3. Continue to configuration below

### 2.2 Configure Build Settings

Fill in these EXACT settings:

**Basic Settings**:
```
Name: westchester-api
(Or whatever you named it - note the URL it creates)

Region: Ohio (US-East)
(Closest to Westchester, NY)

Branch: main
(This should match your GitHub branch)
```

**Build & Deploy**:
```
Root Directory: (leave BLANK)

Environment: Python 3

Build Command:
pip install -r Technical/requirements.txt

Start Command:
cd Technical/src/api && uvicorn main:app --host 0.0.0.0 --port $PORT

Health Check Path:
/api/health
```

**⚠️ IMPORTANT**: Copy these commands exactly!

### 2.3 Select Plan

Since you're on Free tier:

```
Plan: Free
- 512 MB RAM
- 512 MB Disk
- Spins down after 15 min inactivity
- 750 hours/month
```

**⚠️ DATA FILE WARNING**:
Your GeoJSON files are 538 MB total - they won't fit on free tier disk (512 MB limit).

**Solutions**:
1. **Option A**: Upgrade to Starter ($7/month) for 1 GB disk
2. **Option B**: Optimize data files to fit under 512 MB
3. **Option C**: Use external storage (AWS S3) for large files

**For now**: Let's deploy without the large data files and add them later.

### 2.4 Add Environment Variables

Click "Advanced" to expand environment variables.

Add these variables (click "+ Add Environment Variable" for each):

```env
ENVIRONMENT=production

DEBUG=false

PYTHON_VERSION=3.11.5

API_TITLE=Westchester County Data Platform API

API_VERSION=1.0.0

CORS_ORIGINS=http://localhost:3000,http://localhost:5173

ENABLE_CACHING=true

CACHE_TTL_SECONDS=3600
```

**Note**: We'll update `CORS_ORIGINS` later after Netlify deployment.

### 2.5 Deploy Service

1. Scroll to bottom
2. Click "Create Web Service" (if new) or "Save Changes" (if editing)
3. Render will start building your service

---

## Step 3: Monitor Deployment (5 minutes)

### 3.1 Watch Build Logs

You'll see:
- "Cloning repository..."
- "Installing dependencies..." (pip install)
- "Build succeeded"
- "Starting service..." (uvicorn)

**Build typically takes 3-5 minutes**.

### 3.2 Common Errors You Might See

**Error**: "No such file or directory: Technical/requirements.txt"
**Fix**: Ensure requirements.txt is in your GitHub repo at the correct path

**Error**: "Module 'main' not found"
**Fix**: Check start command path is correct for your project structure

**Error**: "Port already in use"
**Fix**: Make sure you're using `$PORT` variable (provided by Render)

### 3.3 Verify Deployment Success

Once build completes:

1. Look for "Live" status (green badge)
2. Copy your service URL: `https://westchester-api.onrender.com`
   - (Or whatever name you chose)
   - **SAVE THIS URL** - you need it for Netlify!

3. Test the API:
   - Click "Open" button or visit URL directly
   - Should see API response or redirect to `/docs`

4. Test health endpoint:
   - Visit: `https://your-service.onrender.com/api/health`
   - Should return:
     ```json
     {"status": "healthy", "version": "1.0.0"}
     ```

5. Test API documentation:
   - Visit: `https://your-service.onrender.com/docs`
   - Should see FastAPI interactive documentation

---

## Step 4: Handle Data Files (Important!)

### Current Situation
Your infrastructure GeoJSON files (538 MB) won't fit on free tier.

### Solution A: Exclude Large Files (Quick Fix)

Create `.gitignore` if not exists, add:

```
# Large data files - deploy separately
Technical/data/raw/infrastructure/*.geojson
Technical/data/raw/infrastructure/roads*.geojson
Technical/data/raw/infrastructure/tod*.geojson
```

This prevents large files from being pushed to GitHub.

**Then update API code** to handle missing files gracefully:

```python
# In Technical/src/api/main.py
# Add error handling for missing data files

@app.get("/api/planning/roads-no-coverage")
async def get_roads_no_coverage():
    file_path = DATA_DIR / "raw/infrastructure/roads_no_coverage.geojson"

    if not file_path.exists():
        # Return empty dataset with message
        return {
            "type": "FeatureCollection",
            "features": [],
            "message": "Data file not available on free tier - upgrade for full data"
        }

    # Load and return data as normal
    ...
```

### Solution B: Upgrade to Starter Plan ($7/month)

**Benefits**:
- 1 GB disk (fits all your data)
- Always-on (no spin down)
- Better performance
- Persistent disk for data files

**To upgrade**:
1. In Render dashboard → Service → Settings
2. Scroll to "Plan"
3. Click "Change Plan"
4. Select "Starter" ($7/month)
5. Add payment method
6. Click "Upgrade"

**Then add Persistent Disk**:
1. Settings → Disks → Add Disk
2. Name: `westchester-data`
3. Mount Path: `/opt/render/project/src/Technical/data`
4. Size: 1 GB
5. Save

### Solution C: Use External Storage (Advanced)

Upload files to AWS S3, Google Cloud Storage, etc.
Modify API to fetch from cloud storage.

**Recommended for now**: Use Solution A (exclude large files) to get deployed quickly.
Upgrade to Starter later when ready for full data.

---

## Step 5: Save Important Information

**Fill this out and save**:

```
Render Service Name: ___________________________

Service URL: https://___________________________.onrender.com

Health Check URL: https://___________________________.onrender.com/api/health

API Docs URL: https://___________________________.onrender.com/docs

Plan: Free (or Starter if upgraded)

Deploy Status: Live / Building / Failed

GitHub Repository: https://github.com/andenick/westchester

Last Deploy: ___________________________
```

---

## Step 6: Next Steps

### Immediate Actions

1. ✅ Verify service is "Live" in Render dashboard
2. ✅ Test health endpoint returns 200 OK
3. ✅ Copy service URL for Netlify configuration
4. → **Next**: Deploy frontend to Netlify

### Before Netlify Deployment

Make sure you have:
- ✅ Render service URL saved
- ✅ Service showing "Live" status
- ✅ API health check working
- ✅ API docs accessible

### Netlify Configuration

When deploying to Netlify, you'll need your Render URL for the environment variable:

```env
VITE_API_URL=https://your-service.onrender.com
```

---

## Troubleshooting

### Issue: Build Fails on Render

**Check**:
1. Build logs for specific error
2. Verify `requirements.txt` exists at correct path
3. Ensure all Python dependencies are listed
4. Check Python version (3.11+)

**Common fixes**:
```bash
# Locally test that requirements.txt works:
pip install -r Technical/requirements.txt

# If errors, fix requirements.txt and push update:
git add Technical/requirements.txt
git commit -m "Fix requirements.txt"
git push
```

Render will auto-deploy on push.

### Issue: Service Crashes on Startup

**Check Logs**:
1. Render dashboard → Logs tab
2. Look for error messages
3. Common issues:
   - Port not using `$PORT` variable
   - Import errors (missing dependencies)
   - Data files not found

**Fix**:
Update code, commit, and push:
```bash
git add .
git commit -m "Fix startup crash"
git push
```

### Issue: Health Check Failing

**Verify** your API has health endpoint:

```python
# In Technical/src/api/main.py
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
```

### Issue: 502/503 Errors

**Causes**:
- Service not healthy
- Build failed
- Start command incorrect

**Fix**:
1. Check service status (should be "Live")
2. Review logs for errors
3. Verify start command matches your project structure

### Issue: Free Tier Spins Down

**Behavior**:
- After 15 minutes of inactivity, service sleeps
- First request takes 30-60 seconds to wake up
- Subsequent requests are fast

**Solutions**:
1. Accept this limitation (free tier trade-off)
2. Upgrade to Starter ($7/month) for always-on
3. Use external ping service to keep alive (UptimeRobot)

---

## Free Tier Limitations

Be aware:

- ✅ 750 hours/month runtime (enough for single service)
- ✅ Automatic HTTPS/SSL
- ✅ Automatic deploys from GitHub
- ❌ 512 MB disk (too small for your data)
- ❌ Spins down after 15 min inactivity
- ❌ Shared CPU (slower performance)
- ❌ No custom domain support on free tier

**When to upgrade to Starter ($7/month)**:
- Need all data files (1 GB disk)
- Want always-on (no spin down)
- Better performance needed
- Ready for custom domain (api.your-domain.com)

---

## Auto-Deploy Setup

**Already configured!** Since you connected GitHub:

- Every push to `main` branch triggers auto-deploy
- Render rebuilds and redeploys automatically
- Zero downtime deployments
- View deploy history in "Events" tab

**To manually trigger deploy**:
1. Dashboard → Manual Deploy
2. Select branch: `main`
3. Click "Deploy"

**To disable auto-deploy**:
1. Settings → Build & Deploy
2. Toggle "Auto-Deploy" off
3. Only manual deploys

---

## Quick Commands Reference

### Push Updates to Render

```bash
cd D:\Arcanum\Projects\Westchester

# Make changes to your code
# ...

# Stage changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to GitHub (triggers auto-deploy)
git push
```

### Check Deploy Status

```bash
# Watch in Render dashboard → Logs tab
# Or visit service URL to see if changes live
```

### Roll Back to Previous Version

```bash
# In Render dashboard:
# 1. Go to "Events" tab
# 2. Find previous successful deploy
# 3. Click "Redeploy" next to that version
```

---

## Next: Deploy Frontend to Netlify

Once your Render backend is deployed and working:

1. **Copy your Render service URL**:
   - Example: `https://westchester-api.onrender.com`

2. **Follow Netlify guide**:
   - Open: `NETLIFY_FRONTEND_SETUP_GUIDE.md`
   - You'll need the Render URL for environment variables

3. **Update CORS after Netlify deployed**:
   - Come back to Render
   - Update `CORS_ORIGINS` environment variable
   - Add your Netlify URL

---

## Support

**Render Documentation**: https://render.com/docs
**Community Forum**: https://community.render.com
**Support Email**: support@render.com

**Your GitHub Repository**: https://github.com/andenick/westchester
**Render Dashboard**: https://dashboard.render.com

---

**Guide Created**: October 17, 2025
**For**: andenick/westchester project
**Next Guide**: NETLIFY_FRONTEND_SETUP_GUIDE.md
