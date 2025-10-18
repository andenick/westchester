# Westchester Sidewalk Analysis - Deployment Guide

## Production Readiness Status

**Build Status**: READY FOR DEPLOYMENT
**Last Updated**: October 17, 2025

## Pre-Deployment Checklist

- [x] TypeScript compilation errors fixed (6/6)
- [x] Production build successful (943KB bundle, optimized)
- [x] Environment variable configuration complete
- [x] CORS configuration updated for production
- [x] `.env.example` file created

## Environment Configuration

### Frontend (.env)

Create `src/frontend/.env.local` for production:

```bash
# Production API URL - Update with your domain
VITE_API_URL=https://your-api-domain.com

# Application Info
VITE_APP_NAME=Westchester Sidewalk Analysis
VITE_APP_VERSION=1.0.0
```

### Backend (main.py)

Update CORS origins in `src/api/main.py:38-39`:

```python
allow_origins=[
    "http://localhost:3000",
    "http://localhost:5173",
    "https://yourdomain.com",        # Add your frontend domain
    "https://www.yourdomain.com"     # Add www version if needed
],
```

## Build Instructions

### Frontend Build

```bash
cd src/frontend
npm run build
```

**Output**: `dist/` folder with optimized static files (49.6 KB CSS, 943.5 KB JS)

### Backend Deployment

```bash
cd src/api
uvicorn main:app --host 0.0.0.0 --port 8000
```

**For production**: Use process manager (PM2, systemd) and reverse proxy (nginx)

## Data Requirements

Ensure these data files exist in `data/raw/infrastructure/`:
- roads_no_coverage.geojson (73 MB)
- roads_one_side.geojson (205 MB)
- roads_both_sides.geojson (12 MB)
- tod_area_roads.geojson (248 MB)
- tod_buffers.geojson (173 KB)
- county_wide_statistics.json
- tod_statistics.json

## Deployment Steps

### 1. Deploy Backend API

```bash
# Install dependencies
pip install fastapi uvicorn python-multipart

# Run with uvicorn (production)
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2. Deploy Frontend

```bash
# Build production bundle
cd src/frontend
npm run build

# Deploy dist/ folder to your static hosting
# Options: Vercel, Netlify, AWS S3 + CloudFront, etc.
```

### 3. Configure Domain

1. Point your domain to frontend hosting
2. Point API subdomain (e.g., api.yourdomain.com) to backend server
3. Update `.env.local` with production API URL
4. Update CORS in `main.py` with production frontend URL

## Performance Optimization

**Frontend Bundle Analysis**:
- CSS: 49.60 KB (gzipped: 15.49 KB)
- JS: 943.50 KB (gzipped: 272.11 KB)

**Optimization Recommendations**:
- Consider code-splitting for routes
- Use dynamic imports for large GeoJSON data
- Enable CDN for static assets
- Implement service worker for offline support

## Security Considerations

1. **CORS**: Only allow specific production domains
2. **Environment Variables**: Never commit `.env.local` to git
3. **API Rate Limiting**: Consider adding rate limiting to backend
4. **HTTPS**: Always use HTTPS in production

## Monitoring

**Recommended Metrics to Track**:
- API response times
- Frontend load times
- Error rates
- User engagement metrics

## Troubleshooting

### Common Issues

**Build Errors**:
- Ensure Node.js 18+ and npm 9+ installed
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`

**API Connection Issues**:
- Verify VITE_API_URL in .env.local
- Check CORS configuration matches frontend domain
- Ensure backend is running and accessible

**Data Loading Issues**:
- Verify all GeoJSON files exist in data/raw/infrastructure/
- Check file permissions on server
- Monitor API logs for specific errors

## Rollback Plan

1. Keep previous deployment artifacts
2. Document current environment variables
3. Have database backups (if applicable)
4. Keep previous git commit tagged

## Post-Deployment Verification

```bash
# Test API health
curl https://your-api-domain.com/api/health

# Test frontend
curl https://yourdomain.com

# Verify data endpoints
curl https://your-api-domain.com/api/planning/sidewalk-statistics
```

## Support

For deployment issues, check:
- Build logs in CI/CD pipeline
- Browser console for frontend errors
- Backend logs for API errors
- Network tab for failed requests

---

**Status**: PRODUCTION READY
**Next Action**: Configure production domains and deploy
