# Your Deployment Commands - Quick Reference
## For andenick/westchester Project

**Date**: October 17, 2025
**GitHub**: https://github.com/andenick/westchester
**Render**: Connected to YouTube account

---

## Step 1: Push Code to GitHub (First Time)

Open Command Prompt or PowerShell, then run these commands **in order**:

```bash
# Navigate to project
cd D:\Arcanum\Projects\Westchester

# Initialize Git (first time only)
git init

# Configure Git user (first time only - use your email)
git config --global user.name "andenick"
git config --global user.email "your-github-email@example.com"

# Stage all files
git add .

# Create first commit
git commit -m "Initial commit - Westchester County Data Platform"

# Connect to your GitHub repo
git remote add origin https://github.com/andenick/westchester.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

**If git push asks for password**:
- GitHub requires Personal Access Token (not password)
- Create token: https://github.com/settings/tokens
- Click "Generate new token (classic)"
- Select scope: `repo` (full control)
- Copy token and use as password

---

## Step 2: Configure Render Service

### Go to Render Dashboard
https://dashboard.render.com

### Find Your Service
Click on the service you created (or create new Web Service if you haven't)

### Configure Build Settings

**Copy these EXACT values**:

```
Name:
westchester-api

Region:
Ohio (US-East)

Branch:
main

Root Directory:
(leave BLANK)

Build Command:
pip install -r Technical/requirements.txt

Start Command:
cd Technical/src/api && uvicorn main:app --host 0.0.0.0 --port $PORT

Health Check Path:
/api/health
```

### Add Environment Variables

Click "Advanced" → Add these variables:

```
ENVIRONMENT = production
DEBUG = false
PYTHON_VERSION = 3.11.5
CORS_ORIGINS = http://localhost:3000,http://localhost:5173
API_TITLE = Westchester County Data Platform API
API_VERSION = 1.0.0
ENABLE_CACHING = true
CACHE_TTL_SECONDS = 3600
```

### Deploy

Click "Create Web Service" or "Save Changes"

Wait 3-5 minutes for build to complete.

---

## Step 3: Verify Render Deployment

### Check Service Status

Should show: **"Live"** (green)

### Copy Your Service URL

Example: `https://westchester-api.onrender.com`
(Your actual URL will be different - write it down!)

**Your Render URL**: https://_____________________________.onrender.com

### Test API

Visit these URLs in your browser:

1. **Health Check**:
   ```
   https://your-service.onrender.com/api/health
   ```
   Should return: `{"status":"healthy","version":"1.0.0"}`

2. **API Docs**:
   ```
   https://your-service.onrender.com/docs
   ```
   Should show FastAPI documentation page

---

## Step 4: Build Frontend for Netlify

### Navigate to Frontend

```bash
cd D:\Arcanum\Projects\Westchester\Technical\src\frontend
```

### Create Environment File

```bash
# Copy template
copy .env.production .env.production.local
```

### Edit Environment File

Open `.env.production.local` in Notepad and change:

```env
VITE_API_URL=https://YOUR-ACTUAL-RENDER-URL.onrender.com
```

Replace `YOUR-ACTUAL-RENDER-URL` with your actual Render service URL!

### Install Dependencies (if not done)

```bash
npm install
```

### Build Production Version

```bash
npm run build
```

Wait ~15 seconds. Should see: "✓ built in XX.XXs"

### Verify Build

```bash
dir dist
```

Should see:
- `index.html`
- `assets` folder
- Other files

---

## Step 5: Deploy to Netlify

### Go to Netlify

1. Open: https://www.netlify.com
2. Sign up / Log in (use GitHub account)

### Deploy Site

1. Click "Add new site" → "Deploy manually"
2. **Drag the entire `dist` folder** from:
   ```
   D:\Arcanum\Projects\Westchester\Technical\src\frontend\dist
   ```
   Into the Netlify upload area

3. Wait 1-2 minutes for deployment

4. Copy your Netlify URL:
   ```
   https://random-name-12345.netlify.app
   ```

**Your Netlify URL**: https://_____________________________.netlify.app

---

## Step 6: Update CORS on Render

### Go Back to Render

1. Open your service: https://dashboard.render.com
2. Click on `westchester-api` service
3. Go to "Environment" tab

### Update CORS_ORIGINS

1. Find `CORS_ORIGINS` variable
2. Click "Edit"
3. Update value to:
   ```
   https://your-netlify-url.netlify.app,http://localhost:3000
   ```
   Replace `your-netlify-url` with your actual Netlify URL!

4. Click "Save Changes"
5. Render will automatically redeploy (wait 1-2 min)

---

## Step 7: Test Everything

### Test Your Website

Visit your Netlify URL: `https://your-site.netlify.app`

### Check All Dashboards Work

1. Landing page loads ✓
2. Overview Dashboard ✓
3. Demographics Dashboard ✓
4. Transit Dashboard ✓
5. Infrastructure Dashboard ✓
6. Historical Trends Dashboard ✓
7. Municipality Comparison ✓
8. Municipal Services ✓
9. Budget Dashboard ✓
10. Property Tax Dashboard ✓

### Check Browser Console

1. Press F12 (open dev tools)
2. Go to "Console" tab
3. Should see NO red errors
4. Should see NO CORS errors

If you see CORS errors:
- Double-check Render CORS_ORIGINS includes your Netlify URL
- Wait for Render redeploy to complete
- Refresh your Netlify site

---

## Future Updates

### When You Make Code Changes

```bash
cd D:\Arcanum\Projects\Westchester

# Make your changes to code files
# ...

# Stage changes
git add .

# Commit with description
git commit -m "Description of what you changed"

# Push to GitHub
git push

# Render will auto-deploy backend (wait 2-3 min)
```

### Update Frontend

```bash
cd Technical\src\frontend

# Make changes to frontend code
# ...

# Rebuild
npm run build

# Drag new dist folder to Netlify (overwrites old deployment)
```

---

## Costs

**Current Setup (Free Tier)**:
- Render Free: $0/month
- Netlify Free: $0/month
- **Total**: $0/month

**Limitations**:
- Render spins down after 15 min (slow first request)
- Render disk: 512 MB (too small for all data files)
- No custom domain on Render free tier

**To Upgrade (When Ready)**:
- Render Starter: $7/month
  - 1 GB disk (fits all data)
  - Always-on (no spin down)
  - Better performance

---

## Your Project URLs

Fill these in after deployment:

```
GitHub Repository:
https://github.com/andenick/westchester

Render Service:
https://________________________________.onrender.com

Render API Health:
https://________________________________.onrender.com/api/health

Render API Docs:
https://________________________________.onrender.com/docs

Netlify Site:
https://________________________________.netlify.app

Production Site (after custom domain):
https://________________________________
```

---

## Troubleshooting

### Git push fails
- Create GitHub Personal Access Token
- Use token as password when prompted

### Render build fails
- Check Logs tab in Render dashboard
- Verify requirements.txt path is correct
- Ensure all dependencies listed

### Frontend shows blank page
- Check browser console for errors (F12)
- Verify VITE_API_URL in .env.production.local is correct
- Rebuild: `npm run build`

### CORS errors in browser
- Update Render CORS_ORIGINS to include Netlify URL
- Wait for Render to redeploy
- Refresh browser (Ctrl+Shift+R)

### API returns 503 error
- Check Render service status (should be "Live")
- Free tier spins down - first request takes 30-60 sec
- Check Logs tab for errors

---

## Quick Links

**Render Dashboard**: https://dashboard.render.com
**Netlify Dashboard**: https://app.netlify.com
**GitHub Repository**: https://github.com/andenick/westchester
**GitHub Tokens**: https://github.com/settings/tokens

**Guides**:
- `RENDER_CONFIGURATION_FOR_YOUR_GITHUB.md` - Detailed Render setup
- `NETLIFY_FRONTEND_SETUP_GUIDE.md` - Detailed Netlify setup
- `COMPLETE_DEPLOYMENT_CHECKLIST.md` - Full deployment checklist

---

## Next Steps

After basic deployment works:
1. ✅ Get a domain from Namecheap (~$12/year)
2. ✅ Configure DNS for custom domain
3. ✅ Upgrade Render to Starter ($7/month) for full data
4. ✅ Extract budget data from PDFs
5. ✅ Remove sample data warnings

**You're ready to deploy!** 🚀

Start with Step 1 above (push to GitHub).
