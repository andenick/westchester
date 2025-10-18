# Complete Deployment Checklist
## Westchester County Data Platform - From Zero to Live

**Created**: October 17, 2025
**Purpose**: One-page checklist to track deployment progress
**Estimated Total Time**: 2-3 hours

---

## Overview

This checklist combines all deployment guides into one trackable list.
Check off items as you complete them.

---

## Phase 1: Domain Purchase (30 min)

**Guide**: `NAMECHEAP_DOMAIN_SETUP_GUIDE.md` - Part 1 & 2

- [ ] Create Namecheap account
- [ ] Search for domain name
- [ ] Purchase domain (~$12-15/year)
- [ ] Enable WhoisGuard (domain privacy)
- [ ] Enable Auto-Renew
- [ ] Enable Domain Lock
- [ ] Save domain credentials securely

**Domain Name**: ___________________________
**Purchase Date**: ___________________________
**Expiration Date**: ___________________________

---

## Phase 2: Render Backend Deployment (20 min)

**Guide**: `RENDER_BACKEND_SETUP_GUIDE.md`

### Account Setup
- [ ] Create Render account
- [ ] Verify email address
- [ ] Connect GitHub (if using Git deployment)

### Service Configuration
- [ ] Create new Web Service
- [ ] Configure build settings:
  - Build command: `pip install -r Technical/requirements.txt`
  - Start command: `cd Technical/src/api && uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Select plan: Starter ($7/month) or Free
- [ ] Add persistent disk (1 GB for data files)
- [ ] Add environment variables:
  ```
  ENVIRONMENT=production
  DEBUG=false
  CORS_ORIGINS=https://localhost:3000
  ```

### Deployment
- [ ] Click "Create Web Service"
- [ ] Watch build complete successfully
- [ ] Verify service shows "Live" status
- [ ] Copy Render URL: `https://________________.onrender.com`

### Testing
- [ ] Test health endpoint: `/api/health`
- [ ] Test API docs: `/docs`
- [ ] Upload data files to persistent disk (if needed)

**Render Service URL**: https://___________________________. onrender.com

---

## Phase 3: Netlify Frontend Deployment (15 min)

**Guide**: `NETLIFY_FRONTEND_SETUP_GUIDE.md`

### Account Setup
- [ ] Create Netlify account
- [ ] Verify email address
- [ ] Connect GitHub (if using Git deployment)

### Local Build
- [ ] Navigate to frontend folder
- [ ] Create `.env.production.local` with Render URL:
  ```
  VITE_API_URL=https://your-app.onrender.com
  ```
- [ ] Run `npm install` (if needed)
- [ ] Run `npm run build`
- [ ] Verify `dist/` folder created

### Deployment
Choose one method:

**Method A: Drag-and-Drop** (faster for first deploy)
- [ ] Click "Deploy manually"
- [ ] Drag `dist/` folder to Netlify
- [ ] Wait for deployment complete
- [ ] Copy Netlify URL: `https://________________.netlify.app`

**Method B: Git-Based** (better for updates)
- [ ] Click "Import an existing project"
- [ ] Connect GitHub repository
- [ ] Configure build settings:
  - Base directory: `Technical/src/frontend`
  - Build command: `npm run build`
  - Publish directory: `Technical/src/frontend/dist`
- [ ] Add environment variables (same as .env.production.local)
- [ ] Deploy site
- [ ] Copy Netlify URL: `https://________________.netlify.app`

### Site Configuration
- [ ] Update site name (Settings → Site information)
- [ ] Verify HTTPS enabled automatically
- [ ] Test all dashboards load correctly

**Netlify Site URL**: https://___________________________. netlify.app

---

## Phase 4: Connect Frontend & Backend (5 min)

**Update CORS on Render**:
- [ ] Go to Render service → Environment tab
- [ ] Update `CORS_ORIGINS` variable:
  ```
  https://your-site.netlify.app,https://localhost:3000
  ```
- [ ] Save changes (Render auto-redeploys)
- [ ] Wait for redeploy complete (1-2 min)

**Test Connection**:
- [ ] Visit Netlify site
- [ ] Open browser dev tools (F12)
- [ ] Check Console tab for errors
- [ ] Verify data loads from API (no CORS errors)
- [ ] Test all 10 dashboards work

---

## Phase 5: Custom Domain Configuration (30 min)

**Guide**: `NAMECHEAP_DOMAIN_SETUP_GUIDE.md` - Part 3

### Netlify Domain Setup
- [ ] In Netlify: Site settings → Domain management
- [ ] Click "Add custom domain"
- [ ] Enter your domain: `your-domain.com`
- [ ] Netlify provides DNS records:
  - A record: @ → 75.2.60.5 (or Netlify's current IP)
  - CNAME: www → your-site.netlify.app

### Render Domain Setup
- [ ] In Render: Service → Settings → Custom Domain
- [ ] Add custom domain: `api.your-domain.com`
- [ ] Render provides CNAME record:
  - CNAME: api → your-app.onrender.com

### Namecheap DNS Configuration
- [ ] Log in to Namecheap
- [ ] Go to domain → Manage → Advanced DNS
- [ ] Add DNS records:
  ```
  Type    Host    Value
  A       @       75.2.60.5 (Netlify IP)
  CNAME   www     your-site.netlify.app
  CNAME   api     your-app.onrender.com
  ```
- [ ] Save all changes
- [ ] Wait for DNS propagation (30 min - 2 hours)

### Verify DNS Propagation
- [ ] Check dnschecker.org for your domain
- [ ] Wait until most locations show green checkmarks
- [ ] Test: `nslookup your-domain.com` returns Netlify IP

### SSL Certificate Verification
- [ ] In Netlify: Check HTTPS status → "Certificate active"
- [ ] In Render: Check Custom Domain → "SSL active"
- [ ] Visit `https://your-domain.com` → Green lock icon
- [ ] Visit `https://api.your-domain.com/api/health` → Green lock icon

### Update CORS with Custom Domain
- [ ] In Render: Update `CORS_ORIGINS` to include custom domain:
  ```
  https://your-domain.com,https://www.your-domain.com,https://your-site.netlify.app
  ```
- [ ] Save and wait for redeploy

---

## Phase 6: Final Testing & Launch (15 min)

### Functional Testing
Test all features on production site:

**All Dashboards**:
- [ ] Landing page loads
- [ ] Overview Dashboard
- [ ] Demographics Dashboard
- [ ] Transit Dashboard
- [ ] Infrastructure Dashboard
- [ ] Historical Trends Dashboard
- [ ] Municipality Comparison Dashboard
- [ ] Municipal Services Dashboard
- [ ] Budget Dashboard
- [ ] Property Tax Dashboard

**API Connectivity**:
- [ ] No CORS errors in browser console
- [ ] Data loads successfully on all dashboards
- [ ] Maps display correctly
- [ ] Charts render properly

**Mobile Responsiveness**:
- [ ] Test on phone (or Chrome dev tools mobile view)
- [ ] Test on tablet
- [ ] All dashboards responsive
- [ ] Navigation works on mobile

**Performance**:
- [ ] Page load time < 3 seconds
- [ ] API response time < 1 second
- [ ] Lighthouse performance score > 80

### Security Verification
- [ ] HTTPS enabled on main site
- [ ] HTTPS enabled on API
- [ ] HTTP → HTTPS redirect works
- [ ] No mixed content warnings
- [ ] Security headers present (check browser dev tools → Network)

### SEO & Meta Tags (Optional)
- [ ] Page titles set correctly
- [ ] Meta descriptions present
- [ ] Open Graph tags for social sharing
- [ ] Favicon displays

---

## Phase 7: Monitoring & Maintenance Setup (10 min)

### Error Monitoring (Optional)
- [ ] Set up Sentry (free tier) for error tracking
- [ ] Add Sentry DSN to environment variables
- [ ] Test error reporting

### Analytics (Optional)
- [ ] Enable Netlify Analytics ($9/month)
- OR
- [ ] Set up Google Analytics (free)
- [ ] Add tracking ID to environment variables
- [ ] Verify tracking works

### Uptime Monitoring (Optional)
- [ ] Set up UptimeRobot (free) for uptime checks
- [ ] Add alerts via email/Slack

### Deployment Notifications
- [ ] Netlify: Settings → Build notifications
- [ ] Add email/Slack webhook for deploy notifications
- [ ] Render: Settings → Notifications
- [ ] Add email for deploy failures

---

## Post-Launch Checklist

### Documentation
- [ ] Save all URLs, credentials, API keys
- [ ] Document deployment process for future reference
- [ ] Update README.md with production URL
- [ ] Create runbook for common issues

### Backup Strategy
- [ ] Ensure code is in Git repository
- [ ] Tag release: `git tag v1.0.0`
- [ ] Push to GitHub: `git push --tags`
- [ ] Backup extracted data files
- [ ] Export environment variables to secure location

### Team Handoff (If Applicable)
- [ ] Share deployment guides with team
- [ ] Provide access to Namecheap account
- [ ] Provide access to Render account
- [ ] Provide access to Netlify account
- [ ] Document who is responsible for renewals

---

## Quick Reference

### Important URLs

**Production Site**:
- Main: https://___________________________
- www: https://www.___________________________
- API: https://api.___________________________

**Admin Dashboards**:
- Netlify: https://app.netlify.com
- Render: https://dashboard.render.com
- Namecheap: https://ap.www.namecheap.com

### Credentials Location
```
Namecheap: [Password Manager]
Render: [Password Manager]
Netlify: [Password Manager]
GitHub: [Password Manager]
```

### Monthly Costs
```
Domain (Namecheap): $12-15/year = ~$1.25/month
Render Starter: $7/month
Netlify Free: $0/month
----------------------------
Total: ~$8.25/month (first year)
       ~$10/month (after first year, WhoisGuard renewal)
```

### Support Contacts
```
Namecheap Support: Live chat 24/7 in dashboard
Render Support: support@render.com
Netlify Support: Community forum + paid support on Pro tier
```

---

## Troubleshooting Quick Reference

### Site Not Loading
1. Check Netlify deploy status → Must be "Published"
2. Check DNS propagation → dnschecker.org
3. Clear browser cache → Ctrl+Shift+Delete
4. Try incognito mode

### CORS Errors
1. Check Render CORS_ORIGINS includes your domain
2. Must use HTTPS (not HTTP)
3. Redeploy Render after changing env vars
4. Wait 1-2 min for redeploy

### SSL Not Working
1. Wait for DNS propagation (up to 48 hours)
2. Verify DNS records correct
3. In Netlify: "Verify DNS configuration"
4. In Render: Remove and re-add custom domain

### API Returns 503
1. Check Render service status → Must be "Live"
2. Check Render logs for errors
3. Verify health check endpoint works
4. Check data files uploaded to disk

---

## Completion Certificate

When all items checked:

```
🎉 DEPLOYMENT COMPLETE! 🎉

Project: Westchester County Data Platform
Production URL: https://___________________________
API URL: https://api.___________________________

Deployed By: ___________________________
Date Completed: ___________________________
Total Time: _______ hours

Status: ✅ LIVE IN PRODUCTION
```

---

**Next Steps After Launch**:
1. Monitor site performance for first week
2. Collect user feedback
3. Plan future enhancements
4. Set up regular maintenance schedule
5. Celebrate! 🎉

---

**Guide Version**: 1.0
**Last Updated**: October 17, 2025
**Part of**: Westchester County Data Platform Deployment Guides
