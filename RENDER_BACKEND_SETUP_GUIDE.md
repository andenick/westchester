# Render Backend Setup Guide
## Deploy Westchester County Data Platform API

**Last Updated**: October 17, 2025
**Estimated Time**: 15-20 minutes
**Platform**: Render.com
**Service Type**: Web Service (FastAPI + Python)

---

## Prerequisites

Before starting, ensure you have:
- [✓] Westchester project code ready to deploy
- [✓] Data files ready (GeoJSON files, ~538 MB total)
- [✓] GitHub account (optional, for Git-based deployment)
- [✓] Credit card (for paid tier with 1GB disk) OR willingness to optimize data for free tier

---

## Part 1: Create Render Account (3 minutes)

### Step 1: Sign Up for Render
1. Go to: **https://render.com**
2. Click "Get Started" or "Sign Up" (top right)
3. Choose sign-up method:
   - **Recommended**: "Sign up with GitHub" (easier deployments)
   - Alternative: "Sign up with GitLab"
   - Alternative: Email + password

4. If using GitHub:
   - Click "Authorize Render"
   - Grant permissions to access repositories

5. Complete profile:
   - Name: Your name
   - Company: Optional (or "Personal Project")
   - Click "Complete Setup"

### Step 2: Verify Email
1. Check your email inbox
2. Find "Verify your email address" from Render
3. Click verification link
4. You'll be redirected to Render dashboard

---

## Part 2: Prepare Your Code for Deployment (5 minutes)

### Step 3: Choose Deployment Method

**Option A: Git Repository** (Recommended for updates)
- Pros: Auto-deploy on git push, easier updates
- Cons: Requires GitHub/GitLab account, code must be in repo

**Option B: Manual Upload** (Quick start)
- Pros: No Git needed, deploy immediately
- Cons: Manual re-deployment needed for updates

We'll cover both methods.

### Step 4: Prepare Repository (If Using Git)

**If your code is NOT yet in Git**:

```bash
# Navigate to project root
cd D:/Arcanum/Projects/Westchester

# Initialize git (if not done)
git init

# Add all files
git add .

# Create commit
git commit -m "Initial commit - Westchester Data Platform"

# Create GitHub repository:
# 1. Go to https://github.com/new
# 2. Name: westchester-data-platform
# 3. Private or Public (your choice)
# 4. Click "Create repository"

# Link to GitHub
git remote add origin https://github.com/YOUR-USERNAME/westchester-data-platform.git
git branch -M main
git push -u origin main
```

**If your code IS in Git**:
- Just ensure latest changes are pushed to GitHub/GitLab
- Note the repository URL

---

## Part 3: Create Web Service on Render (8 minutes)

### Step 5: Create New Web Service
1. In Render dashboard, click "**New +**" button (top right)
2. Select "**Web Service**" from dropdown

### Step 6: Connect Repository (Option A - Git)

**If using GitHub**:
1. Click "**Connect GitHub account**" (if not already connected)
2. You'll see list of your repositories
3. Find "**westchester-data-platform**" (or your repo name)
4. Click "**Connect**" next to it

**If repository not visible**:
1. Click "Configure GitHub App"
2. Select repositories to grant Render access
3. Return to Render, repository should appear

**If using GitLab**:
- Similar process, connect GitLab account
- Select repository from list

### Step 6 Alternative: Manual Deployment (Option B)

**If NOT using Git**:
1. On "Create Web Service" page, select "**Public Git repository**"
2. Or click "**I have a Docker image**" if using Docker
3. For manual deployment:
   - You'll upload code as ZIP file after service creation
   - Skip to Step 7

### Step 7: Configure Build Settings

Fill in the form with these settings:

#### Basic Information
- **Name**: `westchester-api` (or your choice)
  - This becomes your URL: `westchester-api.onrender.com`
  - Can only contain lowercase letters, numbers, hyphens
  - Must be unique across all Render

- **Region**: Select closest to your users
  - **Oregon (US-West)** - West Coast USA
  - **Ohio (US-East)** - East Coast USA (recommended for Westchester, NY)
  - **Frankfurt (EU)** - Europe
  - **Singapore (AP)** - Asia Pacific

- **Branch**: `main` (or `master` if that's your default branch)
  - Render deploys this branch
  - Auto-deploys on push to this branch

#### Build & Deploy

- **Root Directory**: Leave BLANK
  - Unless your code is in subfolder
  - For Westchester project: leave blank (Technical/ folder is fine)

- **Environment**: **Python 3**
  - Render detects this from `requirements.txt`

- **Python Version**: `3.11.5`
  - Matches your local development
  - Or use `3.11` for latest 3.11.x

- **Build Command**:
  ```bash
  pip install -r Technical/requirements.txt
  ```
  - ⚠️ **Adjust path if needed** based on your repo structure
  - If requirements.txt is in root: `pip install -r requirements.txt`

- **Start Command**:
  ```bash
  cd Technical/src/api && uvicorn main:app --host 0.0.0.0 --port $PORT
  ```
  - `$PORT` is provided by Render (usually 10000)
  - ⚠️ **Adjust path** to match your project structure
  - If main.py in root: `uvicorn main:app --host 0.0.0.0 --port $PORT`

- **Health Check Path**: `/api/health`
  - Render pings this to verify service is up
  - Must return 200 OK response
  - Ensure this endpoint exists in your FastAPI code

### Step 8: Select Plan

**Free Tier** ($0/month):
- ✅ 512 MB RAM
- ✅ 512 MB Disk Storage
- ✅ Shared CPU
- ✅ 750 hours/month runtime (enough for always-on if only service)
- ❌ **TOO SMALL** for your 538MB data files!
- ⏸️ Spins down after 15 min inactivity (slow first request)

**Starter Tier** ($7/month): **RECOMMENDED**
- ✅ 512 MB RAM
- ✅ **1 GB Disk Storage** (fits your data!)
- ✅ Shared CPU
- ✅ Always-on (no spin down)
- ✅ Better performance

**Standard Tier** ($25/month):
- ✅ 2 GB RAM
- ✅ 10 GB Disk Storage
- ✅ Dedicated CPU
- ✅ Much better performance

**Recommended**: Start with **Starter ($7/month)** to fit your data files.

### Step 9: Add Persistent Disk (CRITICAL for Data Files)

**Why needed**:
- Your GeoJSON files are 538+ MB
- Free tier: 512 MB disk (too small)
- Starter tier: 1 GB disk (just enough)
- Data must persist across deployments

**How to add**:
1. Scroll to "**Disks**" section
2. Click "**+ Add Disk**"
3. Configure:
   - **Name**: `westchester-data`
   - **Mount Path**: `/opt/render/project/src/Technical/data`
     - ⚠️ **IMPORTANT**: Must match where your code reads data
     - Adjust if your data path is different
   - **Size**: `1 GB` (minimum for your data)
     - Paid plans: Can go up to 10 GB or more

4. Click "Add Disk"

**Note**: Disk pricing:
- Included in Starter/Standard plans (up to plan limit)
- Extra disk: ~$0.25/GB/month

### Step 10: Configure Environment Variables

Click "**Advanced**" to expand environment variables section.

Add these variables:

```env
# Required
ENVIRONMENT=production
DEBUG=false
PYTHON_VERSION=3.11.5

# API Configuration
API_TITLE=Westchester County Data Platform API
API_VERSION=1.0.0

# CORS - CRITICAL (update after Netlify deployment)
CORS_ORIGINS=https://your-site.netlify.app,https://www.your-domain.com

# Optional: Caching
ENABLE_CACHING=true
CACHE_TTL_SECONDS=3600

# Optional: Rate limiting (if implemented)
RATE_LIMIT_ENABLED=false
RATE_LIMIT_PER_MINUTE=60
```

**How to add each variable**:
1. Click "+ Environment Variable"
2. Key: `ENVIRONMENT`
3. Value: `production`
4. Click Add
5. Repeat for each variable

**IMPORTANT**: Update `CORS_ORIGINS` after Netlify deployment!
- Initially: Leave as `https://localhost:3000` for testing
- After Netlify: Add your `netlify.app` subdomain
- After custom domain: Add your custom domain

---

## Part 4: Deploy Service (2 minutes)

### Step 11: Review and Create
1. Scroll to bottom of form
2. Review all settings:
   - Name: `westchester-api` ✓
   - Region: Ohio (US-East) ✓
   - Plan: Starter ($7/month) ✓
   - Build command: Correct path ✓
   - Start command: Correct path ✓
   - Disk: 1 GB mounted ✓
   - Environment variables: All added ✓

2. Click "**Create Web Service**"

### Step 12: Watch Build Process
1. You'll be redirected to service dashboard
2. Build log appears automatically
3. Watch for:
   - "Installing dependencies..." (pip install)
   - "Build successful"
   - "Starting service..." (uvicorn)
   - "Service is live"

4. Build typically takes 3-5 minutes

**Common build errors**:
- Missing dependencies → Check requirements.txt
- Python version mismatch → Set PYTHON_VERSION env var
- Path errors → Verify build/start commands have correct paths

### Step 13: Verify Deployment Success
1. Look for "**Live**" status badge (green)
2. Note your service URL: `https://westchester-api.onrender.com`
   - This is your API base URL
   - Copy it - you'll need it for Netlify!

3. Test API endpoint:
   - Click "**Open**" button, or
   - Visit: `https://westchester-api.onrender.com/api/health`

4. Should see response like:
   ```json
   {
     "status": "healthy",
     "version": "1.0.0",
     "timestamp": "2025-10-17T23:45:00Z"
   }
   ```

5. Test API docs:
   - Visit: `https://westchester-api.onrender.com/docs`
   - Should see FastAPI interactive documentation

---

## Part 5: Upload Data Files to Persistent Disk

### Step 14: Access Service Shell (SSH)

**⚠️ Only available on paid plans!**

**If on Starter/Standard plan**:
1. In service dashboard, click "**Shell**" tab
2. Opens web-based terminal
3. Navigate to disk mount:
   ```bash
   cd /opt/render/project/src/Technical/data
   ```

**If on Free plan**:
- Cannot access shell
- Must include data files in Git repo (risky for large files)
- Or use external storage (S3, Google Cloud Storage)

### Step 15: Upload Data Files

**Option A: Via Git (If Data in Repo)**:
- Data automatically deployed with code
- ⚠️ GitHub has 100 MB file limit per file
- ⚠️ Repo size limit ~1 GB total
- Your 538 MB may be OK if split into multiple files

**Option B: Via Render Disk Upload** (Paid plans):
1. In Shell tab:
   ```bash
   # Create infrastructure directory
   mkdir -p /opt/render/project/src/Technical/data/raw/infrastructure

   # Upload files (use file upload widget in shell)
   # Or use curl to download from external source
   ```

**Option C: External Storage** (Any plan):
1. Upload files to AWS S3, Google Cloud Storage, etc.
2. Modify `main.py` to fetch files from S3 on startup
3. Example:
   ```python
   import boto3
   # Download GeoJSON from S3 to local disk on startup
   ```

### Step 16: Verify Data Files Loaded
1. In Shell, check files exist:
   ```bash
   ls -lh /opt/render/project/src/Technical/data/raw/infrastructure/
   ```

2. Should see:
   - roads_no_coverage.geojson (73 MB)
   - roads_one_side.geojson (205 MB)
   - roads_both_sides.geojson (12 MB)
   - tod_area_roads.geojson (248 MB)
   - tod_buffers.geojson (173 KB)

3. Test API endpoint that uses data:
   ```bash
   curl https://westchester-api.onrender.com/api/planning/sidewalk-statistics
   ```

---

## Part 6: Configure Custom Domain (Later)

### Step 17: Add Custom Domain (After DNS Setup)

**Do this AFTER**:
- ✅ Namecheap domain purchased
- ✅ Netlify frontend deployed
- ✅ Ready to configure DNS

**Steps**:
1. In Render service dashboard, go to "**Settings**" tab
2. Scroll to "**Custom Domain**" section
3. Click "**+ Add Custom Domain**"
4. Enter: `api.your-domain.com` (your API subdomain)
   - Example: `api.westchester-data.com`
5. Click "Add"

6. Render provides CNAME record:
   ```
   api.your-domain.com → westchester-api.onrender.com
   ```

7. Copy this info - you'll add it to Namecheap DNS

8. After DNS configured, SSL auto-provisions (5-30 min)

9. Verify SSL active:
   - Green lock icon next to custom domain in Render dashboard
   - Visit `https://api.your-domain.com/api/health`

---

## Part 7: Monitoring & Maintenance

### Step 18: Monitor Service Health
1. **Logs** tab:
   - View real-time application logs
   - See API requests, errors, etc.
   - Filter by log level (info, warning, error)

2. **Metrics** tab:
   - CPU usage
   - Memory usage
   - Request count
   - Response times
   - Available on Starter plan and up

3. **Events** tab:
   - Deployment history
   - Service restarts
   - Build logs

### Step 19: Set Up Alerts (Optional)

**Email Alerts**:
1. Settings → Notifications
2. Add email address
3. Enable alerts for:
   - Deployment failures
   - Service crashes
   - High error rates

**Webhook Alerts** (Advanced):
- Send alerts to Slack, Discord, etc.
- Settings → Webhooks
- Provide webhook URL from your service

### Step 20: Auto-Deploy Setup (If Using Git)

**Already configured!** If you used GitHub deployment:
- Every push to `main` branch triggers deploy
- Render automatically builds and redeploys
- Zero downtime deployments

**To disable auto-deploy**:
- Settings → Auto-Deploy → Toggle OFF
- Manual deployments only

**To manually trigger deploy**:
- Click "Manual Deploy" button
- Select branch
- Click "Deploy"

---

## Part 8: Optimization & Scaling

### Step 21: Monitor Performance
After deployment, monitor:
- API response times (<1 second target)
- Memory usage (should stay under plan limit)
- Disk usage (should stay under 1 GB)

### Step 22: Optimize If Needed

**If API is slow**:
- Upgrade to Standard plan (dedicated CPU)
- Enable caching (already configured via env vars)
- Optimize database queries
- Add CDN for static assets

**If memory usage high**:
- Upgrade plan (more RAM)
- Optimize data loading (lazy load GeoJSON)
- Use pagination for large datasets

**If disk space full**:
- Add more disk storage (Settings → Disks → Resize)
- Compress GeoJSON files (simplify geometries)
- Move large files to S3/external storage

### Step 23: Scaling Options

**Horizontal Scaling** (Multiple Instances):
- Settings → Scaling → Number of Instances
- Run 2+ instances for high availability
- Load balanced automatically
- Requires Starter plan or higher

**Vertical Scaling** (Bigger Instance):
- Upgrade plan for more CPU/RAM
- Free → Starter → Standard → Pro

---

## Troubleshooting

### Issue: Build Fails

**Error**: "Failed to install dependencies"
**Fix**:
- Check requirements.txt has correct package names
- Check Python version matches (3.11+)
- Look for conflicting package versions

**Error**: "Command not found: uvicorn"
**Fix**:
- Add `uvicorn[standard]` to requirements.txt
- Rebuild service

**Error**: "Module not found"
**Fix**:
- Ensure all imports are in requirements.txt
- Check file paths in import statements

### Issue: Service Crashes on Startup

**Error**: "Port already in use"
**Fix**:
- Use `$PORT` environment variable (provided by Render)
- Don't hardcode port 8000 in production

**Error**: "Data files not found"
**Fix**:
- Verify disk mount path matches code
- Check files uploaded to correct location
- View logs to see exact path error

### Issue: API Returns 502/503 Errors

**Cause**: Service not healthy

**Fix**:
1. Check Logs tab for errors
2. Verify health check endpoint returns 200
3. Ensure service started successfully
4. Check memory usage - may need plan upgrade

### Issue: Slow API Responses

**Cause**: Free tier spin down OR slow data loading

**Fix**:
1. Upgrade to Starter plan (no spin down)
2. Enable caching (already configured)
3. Optimize data loading (lazy load large files)
4. Add CDN for static assets

### Issue: CORS Errors

**Symptom**: Frontend can't connect to API

**Fix**:
1. Check CORS_ORIGINS environment variable
2. Must include your Netlify URL
3. Must include custom domain (if configured)
4. Redeploy after changing env vars

---

## Cost Breakdown

### Free Tier ($0/month)
- ✅ Good for testing
- ❌ **NOT ENOUGH** for your data (512 MB < 538 MB)
- Spins down after 15 min inactivity

### Starter Tier ($7/month) - RECOMMENDED
- ✅ 1 GB disk (fits your data)
- ✅ Always-on (no spin down)
- ✅ Custom domain support
- ✅ SSL included
- Total: **$7/month**

### Additional Costs
- Extra disk: ~$0.25/GB/month (if need >1 GB)
- Horizontal scaling: +$7/instance/month
- Total typical: **$7-14/month**

---

## Security Best Practices

### API Security
1. **Never commit secrets to Git**:
   - Use environment variables for API keys
   - Add `.env` to .gitignore

2. **Enable CORS properly**:
   - Only allow your domains
   - Never use `allow_origins=["*"]` in production

3. **Rate limiting** (Optional):
   - Protect against abuse
   - Set in environment variables

4. **HTTPS only**:
   - Render auto-provisions SSL
   - Never allow HTTP in production

### Account Security
1. Enable Two-Factor Authentication:
   - Account settings → Security → 2FA
   - Use authenticator app

2. Use strong password:
   - 12+ characters
   - Password manager recommended

3. Review access logs regularly:
   - Check for unauthorized deployments
   - Monitor service access

---

## Next Steps

### After Render Deployment Complete
1. ✅ Backend API deployed and live
2. ✅ Service URL copied: `https://westchester-api.onrender.com`
3. ✅ Health check verified: `/api/health` returns 200
4. ✅ API docs accessible: `/docs` works
5. → **Next**: Deploy frontend to Netlify
6. → **Guide**: `NETLIFY_FRONTEND_SETUP_GUIDE.md`

### Save This Information
```
Render Service Name: ___________________________
Service URL: https://_____________________. onrender.com
API Health Check: https://_____________________. onrender.com/api/health
API Docs: https://_____________________. onrender.com/docs
Plan: Starter ($7/month)
Region: Ohio (US-East)
Disk Size: 1 GB
```

---

**Guide Version**: 1.0
**Last Updated**: October 17, 2025
**For**: Westchester County Data Platform
**Previous Guide**: NAMECHEAP_DOMAIN_SETUP_GUIDE.md
**Next Guide**: NETLIFY_FRONTEND_SETUP_GUIDE.md
