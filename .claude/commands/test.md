# Test Suite

Run comprehensive testing across all components:

## Frontend Tests
```bash
cd Technical/src/frontend
npm run dev  # Verify dev server starts
npm run build  # Verify production build succeeds
npm run lint  # Check for linting errors
```

## Backend Tests
```bash
cd Technical
python -m pytest tests/ -v
python Technical/src/api/main.py  # Verify API server starts
```

## Integration Tests
1. Start backend API
2. Start frontend dev server
3. Verify frontend can communicate with backend
4. Test key user workflows

## Mobile Responsiveness
Test on these viewports:
- iPhone SE: 375px width
- iPad: 768px width
- Desktop: 1920px width

## Performance Tests
- Measure page load times (target: < 2 seconds)
- Check Lighthouse scores
- Monitor memory usage

Document all test results in `Technical/TESTING_RESULTS.md`

