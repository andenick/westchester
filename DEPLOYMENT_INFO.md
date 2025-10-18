# Deployment Information
## Westchester County Data Platform

**Deployment Date**: October 17, 2025
**Deployed By**: andenick
**Repository**: https://github.com/andenick/westchester

---

## Production URLs

**Frontend (Netlify)**: https://westchester-county-data.netlify.app
**Backend API (Render)**: https://westchester-api.onrender.com
**API Documentation**: https://westchester-api.onrender.com/docs
**API Health Check**: https://westchester-api.onrender.com/api/health

---

## Account Information

**GitHub**:
- Account: andenick
- Repository: https://github.com/andenick/westchester
- Branch: main

**Render**:
- Account: Connected to YouTube account
- Service Name: westchester-api
- Service URL: https://westchester-api.onrender.com
- Plan: Free Tier ($0/month)

**Netlify**:
- Account: andenick's team
- Site Name: westchester-county-data
- Site URL: https://westchester-county-data.netlify.app
- Plan: Free Tier ($0/month)

---

## Current Configuration

### Backend (Render)
```
Environment: production
Python Version: 3.11.5
Build Command: pip install -r Technical/requirements.txt
Start Command: cd Technical/src/api && uvicorn main:app --host 0.0.0.0 --port $PORT
Health Check: /api/health
```

### Frontend (Netlify)
```
Build Command: npm run build
Publish Directory: Technical/src/frontend/dist
Node Version: 18.17.0
```

---

## Environment Variables

### Render (Backend)
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

*Note: Update CORS_ORIGINS after Netlify deployment*

### Netlify (Frontend)
```env
VITE_API_URL=https://[your-render-url].onrender.com
VITE_APP_NAME=Westchester County Data Platform
VITE_APP_VERSION=1.0.0
VITE_APP_ENVIRONMENT=production
```

---

## Current Status

**Deployment Stage**: ✅ DEPLOYED TO PRODUCTION
**Deployment Date**: October 18, 2025
**Data Completeness**: Partial
- ✅ Small data files included in repo
- ❌ Large GeoJSON files excluded (742 MB total)
- ✅ Budget PDFs downloaded (6 files, 73 MB)
- ⚠️ Budget data not yet extracted (sample data in dashboard)
- ⚠️ Property tax data showing sample data warnings

---

## Known Limitations (Free Tier)

### Render Free Tier
- **Disk Space**: 512 MB (insufficient for 742 MB data files)
- **Spin Down**: Service sleeps after 15 min inactivity
- **First Request**: 30-60 seconds wake-up time
- **Performance**: Shared CPU (slower)

### Data Files Excluded
Large GeoJSON files not deployed on free tier:
- `roads_no_coverage.geojson` (73 MB)
- `roads_one_side.geojson` (205 MB)
- `roads_both_sides.geojson` (12 MB)
- `tod_area_roads.geojson` (248 MB)
- `county_wide_coverage.geojson` (289 MB)

**Impact**: Infrastructure/planning dashboards will show "data not available" messages

---

## Upgrade Path

### To Get Full Data (Recommended When Ready)

**Option 1: Upgrade Render to Starter**
- Cost: $7/month
- Benefits:
  - 1 GB disk space (fits all data)
  - Always-on (no spin down)
  - Better performance
  - Persistent disk for data storage

**Steps**:
1. In Render dashboard → Service → Settings
2. Change Plan → Select "Starter"
3. Add Persistent Disk:
   - Size: 1 GB
   - Mount path: `/opt/render/project/src/Technical/data`
4. Upload large GeoJSON files to disk
5. Redeploy service

**Option 2: External Storage**
- Use AWS S3 or Google Cloud Storage
- Modify API to fetch files from cloud
- Keep Render on free tier

---

## Cost Summary

### Current (Free Tier)
- GitHub: $0/month (public repository)
- Render Free: $0/month
- Netlify Free: $0/month
- **Total: $0/month** 🎉

### With Full Data (Starter Tier)
- GitHub: $0/month
- Render Starter: $7/month
- Netlify Free: $0/month
- **Total: $7/month**

### With Custom Domain
- GitHub: $0/month
- Render Starter: $7/month
- Netlify Free: $0/month
- Namecheap Domain: ~$1/month ($12-15/year)
- **Total: ~$8/month**

---

## Deployment History

| Date | Action | Details |
|------|--------|---------|
| 2025-10-17 | Initial setup | Repository created, guides prepared |
| 2025-10-18 | First deploy | Code pushed to GitHub |
| 2025-10-18 | Backend deployed | Render service live at westchester-api.onrender.com |
| 2025-10-18 | Frontend deployed | Netlify site live at westchester-county-data.netlify.app |
| 2025-10-18 | CORS configured | Frontend/backend connected successfully |
| 2025-10-18 | Phase 7 fixes | Added missing pages, fixed transit data |

---

## Maintenance Tasks

### Regular Updates
- **Weekly**: Check service status, review logs
- **Monthly**: Review performance metrics, update dependencies
- **Quarterly**: Extract new budget data (as PDFs released)

### Future Enhancements
1. Extract budget data from existing 6 PDFs
2. Remove sample data warnings from dashboards
3. Upgrade to Starter tier for full data
4. Purchase custom domain
5. Collect and process property tax PDFs
6. Set up monitoring and alerts

---

## Support Contacts

**Platform Support**:
- Render: support@render.com, https://render.com/docs
- Netlify: Community forum, https://answers.netlify.com
- GitHub: https://docs.github.com

**Project Documentation**:
- See `YOUR_DEPLOYMENT_COMMANDS.md` for deployment steps
- See `COMPLETE_DEPLOYMENT_CHECKLIST.md` for full checklist
- See deployment guides in project root

---

## Troubleshooting

### Common Issues

**Build fails on Render**:
- Check logs for specific error
- Verify requirements.txt is correct
- Ensure Python version matches (3.11+)

**CORS errors on frontend**:
- Update Render CORS_ORIGINS with Netlify URL
- Redeploy Render service
- Clear browser cache

**Service shows 503 error**:
- Free tier may be spinning down (wait 30-60 sec)
- Check service status in Render dashboard
- Review logs for startup errors

**Frontend shows blank page**:
- Check browser console for errors
- Verify VITE_API_URL is correct
- Rebuild frontend with correct env vars

---

## Rollback Procedure

If deployment fails:

**GitHub**:
```bash
git revert HEAD
git push
```

**Render**:
- Dashboard → Events → Previous deploy → "Redeploy"

**Netlify**:
- Deploys → Previous deploy → "Publish deploy"

---

**Last Updated**: October 17, 2025
**Status**: Ready for initial deployment
**Next Steps**: Follow YOUR_DEPLOYMENT_COMMANDS.md for deployment instructions
