# Netlify Frontend Setup Guide
## Deploy Westchester County Data Platform Website

**Last Updated**: October 17, 2025
**Estimated Time**: 10-15 minutes
**Platform**: Netlify.com
**Service Type**: Static Site Hosting (React + Vite)

---

## Prerequisites

Before starting, ensure you have:
- [✓] Backend deployed on Render (from previous guide)
- [✓] Render API URL copied (e.g., `https://westchester-api.onrender.com`)
- [✓] Node.js 18+ and npm installed locally
- [✓] Frontend code ready in `./Technical/src/frontend`
- [✓] GitHub account (optional, for auto-deploy)

---

## Part 1: Create Netlify Account (2 minutes)

### Step 1: Sign Up for Netlify
1. Go to: **https://www.netlify.com**
2. Click "**Sign up**" (top right)
3. Choose sign-up method:
   - **Recommended**: "Sign up with GitHub" (easier deployments)
   - Alternative: "Sign up with GitLab"
   - Alternative: "Sign up with Bitbucket"
   - Alternative: Email + password

4. If using GitHub:
   - Click "Authorize Netlify"
   - Grant permissions

5. Complete welcome screen:
   - Team name: Optional (or your name)
   - Click "Continue"

### Step 2: Verify Email (If Using Email Sign-up)
1. Check inbox for "Verify your email" from Netlify
2. Click verification link
3. Redirected to Netlify dashboard

---

## Part 2: Build Production Frontend Locally (5 minutes)

### Step 3: Configure Production Environment

Navigate to frontend directory:
```bash
cd ./Technical/src/frontend
```

Create production environment file:
```bash
# Create .env.production.local (NOT committed to Git)
# Copy from template
cp .env.production .env.production.local
```

Edit `.env.production.local` with your Render URL:
```env
# YOUR Render API URL (from previous guide)
VITE_API_URL=https://westchester-api.onrender.com

# Application info
VITE_APP_NAME=Westchester County Data Platform
VITE_APP_VERSION=1.0.0
VITE_APP_ENVIRONMENT=production

# Map defaults (optional)
VITE_MAP_DEFAULT_CENTER_LAT=41.1220
VITE_MAP_DEFAULT_CENTER_LNG=-73.7949
VITE_MAP_DEFAULT_ZOOM=10
```

**⚠️ CRITICAL**: Replace `westchester-api.onrender.com` with YOUR actual Render URL!

### Step 4: Install Dependencies (If Not Already Done)
```bash
npm install
```

Wait for installation (1-2 minutes).

### Step 5: Build Production Bundle
```bash
npm run build
```

**What this does**:
- Compiles TypeScript → JavaScript
- Bundles all React components
- Minifies code for performance
- Optimizes assets (images, CSS)
- Creates `dist/` folder with production files

**Expected output**:
```
vite v7.1.9 building for production...
✓ 957 modules transformed.
dist/index.html                  0.46 kB │ gzip:   0.29 kB
dist/assets/index-XXXXX.css     49.60 kB │ gzip:  15.49 kB
dist/assets/index-XXXXX.js     943.52 kB │ gzip: 272.13 kB
✓ built in 14.04s
```

**Build time**: ~10-20 seconds

### Step 6: Verify Build Output
```bash
# Check dist folder created
ls dist/

# Should see:
# index.html
# assets/ (folder with JS and CSS files)
# vite.svg
# data/ (if you have static data)
```

### Step 7: Test Production Build Locally (Optional)
```bash
npm run preview
```

- Opens preview server (usually http://localhost:4173)
- Test that site loads correctly
- Verify API calls work (check browser console)
- Press Ctrl+C to stop when done

---

## Part 3: Deploy to Netlify (3 minutes)

### Method A: Drag-and-Drop Deployment (Fastest for First Deploy)

#### Step 8A: Manual Deployment
1. In Netlify dashboard, click "**Add new site**" dropdown
2. Select "**Deploy manually**"
3. You'll see a drag-and-drop upload area

4. In File Explorer, navigate to:
   ```
   D:\Arcanum\Projects\Westchester\Technical\src\frontend\dist
   ```

5. **Drag the entire `dist` folder** into Netlify upload area
   - ⚠️ Drag the **FOLDER**, not individual files
   - Netlify will show upload progress

6. Wait for deployment (30 seconds - 2 minutes)
   - "Processing files..."
   - "Building site..."
   - "Site is live!"

7. Copy your site URL:
   - Format: `https://random-name-12345.netlify.app`
   - Example: `https://magnificent-kelpie-a1b2c3.netlify.app`
   - **Save this URL** - you'll need it!

#### Step 9A: Test Deployment
1. Click "Visit site" or open URL in browser
2. Verify:
   - ✓ Site loads without errors
   - ✓ All pages accessible (dashboards, maps, etc.)
   - ✓ Data loads from API (check browser console for errors)
   - ✓ No CORS errors

**If you see CORS errors**:
- Go back to Render dashboard
- Update `CORS_ORIGINS` environment variable
- Add your Netlify URL: `https://random-name-12345.netlify.app`
- Redeploy Render service

### Method B: Git-Based Deployment (Recommended for Updates)

#### Step 8B: Connect GitHub Repository
1. In Netlify dashboard, click "**Add new site**" dropdown
2. Select "**Import an existing project**"
3. Choose "**Deploy with GitHub**"
4. Click "Authorize Netlify" (if not already done)

5. Find your repository:
   - Search for "westchester" or your repo name
   - Click on repository to select it

**If repository not visible**:
- Click "Configure the Netlify app on GitHub"
- Grant access to repository
- Return to Netlify, refresh page

#### Step 9B: Configure Build Settings
Fill in deployment configuration:

**Basic Settings**:
- **Branch to deploy**: `main` (or `master`)
- **Base directory**: `Technical/src/frontend`
  - ⚠️ This is where package.json lives
  - Adjust if your structure is different

**Build Settings**:
- **Build command**: `npm run build`
- **Publish directory**: `Technical/src/frontend/dist`
  - ⚠️ Must match build output folder
  - Relative to repo root

**Advanced Settings** (Click "Show advanced"):
- **Node version**:
  - Key: `NODE_VERSION`
  - Value: `18.17.0`
  - Or leave blank to use Netlify default (18.x)

#### Step 10B: Add Environment Variables
Click "**Add environment variables**" (before deploying)

Add these variables:
```
VITE_API_URL=https://westchester-api.onrender.com
VITE_APP_NAME=Westchester County Data Platform
VITE_APP_VERSION=1.0.0
VITE_APP_ENVIRONMENT=production
```

**How to add**:
1. Click "+ Add a variable"
2. Key: `VITE_API_URL`
3. Value: Your Render URL
4. Click "Add"
5. Repeat for each variable

#### Step 11B: Deploy Site
1. Review all settings
2. Click "**Deploy site**"
3. Watch build log:
   - Installing dependencies (npm install)
   - Building site (npm run build)
   - Publishing to CDN
4. Build takes 2-5 minutes

5. After deployment:
   - Status changes to "Published"
   - Copy your site URL
   - Click "Visit site" to test

---

## Part 4: Configure Site Settings (3 minutes)

### Step 12: Update Site Name
1. In site dashboard, click "**Site settings**"
2. Under "Site information", click "**Change site name**"
3. Enter a better name:
   - Example: `westchester-data-platform`
   - Must be unique across all Netlify
   - Changes URL to: `westchester-data-platform.netlify.app`
4. Click "Save"

### Step 13: Configure Redirects (For React Router)
**Already configured** via `netlify.toml` file!

If you don't have `netlify.toml`, Netlify auto-detects SPA and adds redirect.

**Verify in dashboard**:
- Settings → Build & deploy → Post processing → Snippet injection
- Should see "Asset optimization" enabled

### Step 14: Enable HTTPS (Automatic)
**Good news**: Netlify enables HTTPS automatically!

1. Site settings → Domain management → HTTPS
2. Should see:
   - ✓ Certificate provisioned
   - ✓ HTTPS enabled
   - ✓ HTTP → HTTPS redirect enabled

**If SSL shows "Pending"**:
- Wait 5-10 minutes
- Refresh page
- If still pending after 30 min, click "Verify DNS configuration"

---

## Part 5: Update CORS on Render (Important!)

### Step 15: Add Netlify URL to CORS
Now that you have your Netlify URL, update Render backend:

1. Go to Render dashboard
2. Open your `westchester-api` service
3. Go to "**Environment**" tab
4. Find `CORS_ORIGINS` variable
5. Click "Edit"
6. Update value to include Netlify URL:
   ```
   https://westchester-data-platform.netlify.app,https://localhost:3000
   ```
   - Separate multiple URLs with commas (no spaces)
   - Include HTTPS (not HTTP)

7. Click "Save Changes"
8. Render will automatically redeploy (1-2 min)

### Step 16: Test CORS Working
1. Visit your Netlify site
2. Open browser dev tools (F12)
3. Go to Console tab
4. Look for API calls:
   - ✓ No CORS errors
   - ✓ Data loads successfully
   - ❌ If CORS errors: Double-check Render CORS_ORIGINS variable

---

## Part 6: Performance Optimization

### Step 17: Enable Asset Optimization
1. Site settings → Build & deploy → Post processing
2. Enable these optimizations:
   - ✓ **Bundle CSS**: Combines CSS files
   - ✓ **Minify CSS**: Reduces file size
   - ✓ **Minify JS**: Reduces file size
   - ✓ **Image compression**: Optimizes images
   - ✓ **Pretty URLs**: Removes `.html` from URLs

3. Click "Save"
4. Netlify applies on next deploy

### Step 18: Configure Caching Headers
**Already configured** via `netlify.toml`!

Verifies caching rules:
- Static assets (JS, CSS): Cached 1 year
- index.html: Not cached (immediate updates)
- Images: Cached appropriately

**Check in dashboard**:
- Settings → Build & deploy → Headers and redirects
- Should see custom headers from `netlify.toml`

---

## Part 7: Custom Domain Setup (Later)

### Step 19: Add Custom Domain (After DNS Configured)
**Do this AFTER Namecheap DNS is configured**

1. Site settings → Domain management → Domains
2. Click "**Add custom domain**"
3. Enter your domain: `westchester-data.com` (or `www.westchester-data.com`)
4. Netlify checks domain:
   - If owned by you: "Domain is already registered"
   - Click "Add domain"

5. Netlify provides DNS records:
   - **A record**: Your domain → Netlify IP (e.g., `75.2.60.5`)
   - **CNAME**: www → your-site.netlify.app

6. Copy these records
7. Add to Namecheap (see NAMECHEAP_DOMAIN_SETUP_GUIDE.md)

### Step 20: Verify Custom Domain
After DNS propagates (30 min - 2 hours):

1. Check domain status in Netlify:
   - Should show "Netlify DNS" or "External DNS"
   - Status: "Awaiting DNS propagation" → "Domain validated"

2. SSL auto-provisions (5-30 minutes after DNS)
   - Status changes to "Certificate active"
   - HTTPS enabled automatically

3. Test custom domain:
   - `https://westchester-data.com` - works!
   - `https://www.westchester-data.com` - works!
   - Both redirect to HTTPS

---

## Part 8: Monitoring & Analytics

### Step 21: Enable Analytics (Optional)

**Netlify Analytics** ($9/month):
- Server-side analytics (no cookies, GDPR-friendly)
- Page views, unique visitors
- Top pages, referrers
- No JavaScript required

**To enable**:
1. Site dashboard → Analytics tab
2. Click "Enable Netlify Analytics"
3. $9/month added to bill

**Free Alternatives**:

**Google Analytics** (Free):
1. Create GA4 property
2. Get tracking ID: `G-XXXXXXXXXX`
3. Add to `.env.production`:
   ```
   VITE_GA_TRACKING_ID=G-XXXXXXXXXX
   ```
4. Add tracking code to `index.html` or use React package

**Plausible** ($9/month, privacy-friendly):
- GDPR compliant
- No cookies
- Lightweight (<1 KB script)

### Step 22: Monitor Deployments
1. Site dashboard → Deploys tab
2. See deployment history:
   - Build time
   - Deploy preview
   - Production deploys
   - Failed builds (with logs)

3. Set up deploy notifications:
   - Settings → Build & deploy → Deploy notifications
   - Add webhook for Slack, Discord, email, etc.

---

## Part 9: Auto-Deploy Setup (If Using Git)

### Step 23: Configure Auto-Deploy
**Already enabled** if you used Git deployment!

Every push to `main` branch triggers deploy:
- Netlify detects commit
- Runs `npm run build`
- Publishes to CDN
- Updates site (zero downtime)

**To configure**:
1. Settings → Build & deploy → Continuous deployment
2. **Build settings**:
   - Production branch: `main`
   - Deploy previews: All branches
   - Branch deploys: Only production branch

3. **Deploy contexts**:
   - Production: Uses production settings
   - Deploy previews: Temporary URLs for testing PRs
   - Branch deploys: Test branches before merging

### Step 24: Deploy Previews (Useful for Testing)
Netlify creates preview URLs for pull requests:
- PR opened → Auto-deploys preview
- Preview URL: `deploy-preview-123--your-site.netlify.app`
- Test changes before merging
- Comment on PR with preview link

---

## Troubleshooting

### Issue: Build Fails

**Error**: "npm install failed"
**Fix**:
- Check `package.json` has correct dependencies
- Verify Node version (18+)
- Clear cache: Settings → Build & deploy → Clear cache and rebuild

**Error**: "Command not found: vite"
**Fix**:
- Check `vite` is in `devDependencies` in package.json
- Run `npm install` locally to verify
- Commit `package-lock.json` to Git

**Error**: "Build command failed"
**Fix**:
- Test build locally: `npm run build`
- Check build logs in Netlify for specific error
- Verify `dist/` folder created locally

### Issue: Site Shows 404 on Routes

**Cause**: React Router not configured correctly

**Fix**:
1. Verify `netlify.toml` has redirect rule:
   ```toml
   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200
   ```
2. Or create `_redirects` file in `public/`:
   ```
   /*    /index.html   200
   ```

### Issue: API Calls Failing (CORS)

**Symptom**: Browser console shows CORS error

**Fix**:
1. Check Render `CORS_ORIGINS` includes Netlify URL
2. Verify HTTPS (not HTTP) in CORS origins
3. Check API URL in `.env.production.local` is correct
4. Redeploy Render after changing CORS

### Issue: Environment Variables Not Working

**Symptom**: `VITE_API_URL` undefined in code

**Fix**:
1. Check variable name starts with `VITE_` (required by Vite)
2. Verify variable added in Netlify dashboard
3. Redeploy site after adding variables
4. In code, access via `import.meta.env.VITE_API_URL`

### Issue: Slow Build Times

**Cause**: Large dependencies or slow npm install

**Fix**:
1. Enable Netlify build cache:
   - Settings → Build & deploy → Build image
   - Select latest Ubuntu image
2. Optimize package.json (remove unused dependencies)
3. Use npm ci instead of npm install (faster):
   - Build command: `npm ci && npm run build`

---

## Cost Breakdown

### Free Tier ($0/month) - RECOMMENDED FOR START
- ✅ 100 GB bandwidth/month (plenty for starting out)
- ✅ 300 build minutes/month (sufficient)
- ✅ Unlimited sites
- ✅ HTTPS included
- ✅ CDN included
- ✅ Deploy previews included
- **Perfect for personal projects and low-traffic sites**

### Pro Tier ($19/month)
- ✅ 1 TB bandwidth/month
- ✅ Unlimited build minutes
- ✅ Role-based access control
- ✅ Password protection
- ✅ Split testing (A/B testing)
- **Needed for high-traffic production sites**

### Business Tier ($99/month)
- ✅ Everything in Pro
- ✅ SSO (single sign-on)
- ✅ Audit log
- ✅ Priority support
- **For enterprise use**

### Add-Ons
- Analytics: +$9/month (optional)
- Large Media: +$19/month (for big images/videos)

**Recommendation**: Start with **Free tier**, upgrade when needed.

---

## Security Best Practices

### Secure Environment Variables
1. **Never commit** `.env.production.local` to Git
   - Already in `.gitignore`
   - Contains sensitive API URLs

2. **Only use VITE_ prefix** for public vars
   - These are exposed in client-side code
   - Don't put API keys in VITE_ vars!

3. **Rotate secrets** if exposed
   - If API keys leaked, regenerate immediately
   - Update in Netlify dashboard

### Site Security Headers
**Already configured** via `netlify.toml`:
- X-Frame-Options: DENY (prevent clickjacking)
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin

**Verify**:
- Settings → Build & deploy → Headers and redirects
- Check headers from `netlify.toml` applied

### HTTPS Enforcement
1. Verify HTTPS redirect enabled:
   - Settings → Domain management → HTTPS
   - "Force HTTPS" should be ON

2. Test:
   - Visit `http://your-site.com`
   - Should redirect to `https://your-site.com`

---

## Performance Checklist

After deployment, verify:

- [ ] Site loads in < 3 seconds (test with Lighthouse)
- [ ] All assets served over HTTPS
- [ ] Images optimized (WebP format if supported)
- [ ] JavaScript minified (check dist/ files)
- [ ] CSS minified
- [ ] Caching headers configured correctly
- [ ] CDN enabled (automatic with Netlify)
- [ ] Gzip compression enabled (automatic)

**Lighthouse Test**:
1. Open site in Chrome
2. Press F12 (dev tools)
3. Go to "Lighthouse" tab
4. Click "Generate report"
5. Target scores:
   - Performance: > 90
   - Accessibility: > 90
   - Best Practices: 100
   - SEO: > 90

---

## Next Steps

### After Netlify Deployment Complete
1. ✅ Frontend deployed and live
2. ✅ Site URL copied: `https://your-site.netlify.app`
3. ✅ Environment variables configured
4. ✅ CORS updated on Render to allow Netlify URL
5. ✅ All dashboards tested and working
6. → **Next**: Configure custom domain
7. → **Guide**: Return to `NAMECHEAP_DOMAIN_SETUP_GUIDE.md` Part 3

### Save This Information
```
Netlify Site Name: ___________________________
Site URL: https://___________________________.netlify.app
Custom Domain: https://___________________________
Deploy Status: Published
HTTPS: Enabled
Auto-Deploy: Enabled (from Git)
```

---

**Guide Version**: 1.0
**Last Updated**: October 17, 2025
**For**: Westchester County Data Platform
**Previous Guide**: RENDER_BACKEND_SETUP_GUIDE.md
**Next Guide**: Return to NAMECHEAP_DOMAIN_SETUP_GUIDE.md (Part 3 - DNS)
