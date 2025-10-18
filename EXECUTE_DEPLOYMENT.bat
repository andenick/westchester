@echo off
REM Westchester County Data Platform - Deployment Script
REM This script will guide you through deploying to GitHub, Render, and Netlify

echo ================================================================================
echo WESTCHESTER COUNTY DATA PLATFORM - DEPLOYMENT SCRIPT
echo ================================================================================
echo.
echo This script will help you deploy your project step-by-step.
echo Each step will pause for your confirmation.
echo.
pause

REM ============================================================================
REM PHASE 1: GIT INITIALIZATION
REM ============================================================================

echo.
echo ================================================================================
echo PHASE 1: INITIALIZING GIT REPOSITORY
echo ================================================================================
echo.

cd /d D:\Arcanum\Projects\Westchester

echo Step 1.1: Initializing Git...
git init
if %errorlevel% neq 0 (
    echo ERROR: Git initialization failed!
    pause
    exit /b 1
)

echo.
echo Step 1.2: Configuring Git user...
echo.
echo Please enter your GitHub username:
set /p GIT_USERNAME="Username: "
echo.
echo Please enter your GitHub email:
set /p GIT_EMAIL="Email: "

git config user.name "%GIT_USERNAME%"
git config user.email "%GIT_EMAIL%"

echo.
echo Git configured successfully!
echo Username: %GIT_USERNAME%
echo Email: %GIT_EMAIL%
echo.
pause

REM ============================================================================
REM PHASE 2: ADDING FILES TO GIT
REM ============================================================================

echo.
echo ================================================================================
echo PHASE 2: STAGING FILES FOR COMMIT
echo ================================================================================
echo.
echo This will add all files to Git (large .geojson files will be excluded)
echo.
pause

git add .
if %errorlevel% neq 0 (
    echo ERROR: Git add failed!
    pause
    exit /b 1
)

echo.
echo Files staged successfully!
echo.
pause

REM ============================================================================
REM PHASE 3: CREATING INITIAL COMMIT
REM ============================================================================

echo.
echo ================================================================================
echo PHASE 3: CREATING INITIAL COMMIT
echo ================================================================================
echo.

git commit -m "Initial commit - Westchester County Data Platform

- Complete frontend (React + TypeScript + Vite)
- Complete backend (FastAPI + Python)
- Deployment configurations (Netlify + Render)
- Documentation and guides
- Budget PDFs (6 files)
- Small data files included
- Large GeoJSON files excluded (deploy separately)"

if %errorlevel% neq 0 (
    echo ERROR: Git commit failed!
    pause
    exit /b 1
)

echo.
echo Commit created successfully!
echo.
pause

REM ============================================================================
REM PHASE 4: CONNECTING TO GITHUB
REM ============================================================================

echo.
echo ================================================================================
echo PHASE 4: CONNECTING TO GITHUB REPOSITORY
echo ================================================================================
echo.

git remote add origin https://github.com/andenick/westchester.git
git branch -M main

echo.
echo Repository connected: https://github.com/andenick/westchester
echo.
pause

REM ============================================================================
REM PHASE 5: PUSHING TO GITHUB
REM ============================================================================

echo.
echo ================================================================================
echo PHASE 5: PUSHING TO GITHUB
echo ================================================================================
echo.
echo IMPORTANT: GitHub requires a Personal Access Token (not password)
echo.
echo If you don't have one:
echo 1. Go to: https://github.com/settings/tokens
echo 2. Click "Generate new token (classic)"
echo 3. Select scope: "repo" (full control)
echo 4. Copy the token
echo 5. Use token as password when prompted below
echo.
echo Ready to push? (This may take a few minutes)
pause

git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo ================================================================================
    echo AUTHENTICATION FAILED
    echo ================================================================================
    echo.
    echo GitHub requires a Personal Access Token.
    echo.
    echo TO CREATE TOKEN:
    echo 1. Open: https://github.com/settings/tokens
    echo 2. Click "Generate new token (classic)"
    echo 3. Note: "Westchester Deployment"
    echo 4. Expiration: 90 days (or longer)
    echo 5. Select: [x] repo (full control)
    echo 6. Click "Generate token"
    echo 7. COPY THE TOKEN (you won't see it again!)
    echo.
    echo Then retry this script or run manually:
    echo   git push -u origin main
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo SUCCESS! CODE PUSHED TO GITHUB
echo ================================================================================
echo.
echo Repository: https://github.com/andenick/westchester
echo.
echo NEXT STEPS:
echo 1. Go to Render dashboard: https://dashboard.render.com
echo 2. Create new Web Service or configure existing one
echo 3. Follow instructions in: YOUR_DEPLOYMENT_COMMANDS.md
echo.
pause

REM ============================================================================
REM PHASE 6: DEPLOYMENT INSTRUCTIONS
REM ============================================================================

echo.
echo ================================================================================
echo NEXT: DEPLOY TO RENDER AND NETLIFY
echo ================================================================================
echo.
echo Your code is now on GitHub!
echo.
echo TO COMPLETE DEPLOYMENT:
echo.
echo 1. RENDER (Backend API):
echo    - Go to: https://dashboard.render.com
echo    - Create Web Service from GitHub repo: andenick/westchester
echo    - Follow settings in YOUR_DEPLOYMENT_COMMANDS.md
echo    - Copy your Render URL when deployed
echo.
echo 2. NETLIFY (Frontend):
echo    - First, build frontend with Render URL
echo    - cd Technical\src\frontend
echo    - Create .env.production.local (use template)
echo    - npm run build
echo    - Drag dist\ folder to https://app.netlify.com
echo.
echo 3. CONNECT THEM:
echo    - Update Render CORS_ORIGINS with Netlify URL
echo    - Test your site!
echo.
echo See YOUR_DEPLOYMENT_COMMANDS.md for detailed instructions.
echo.
pause

echo.
echo ================================================================================
echo DEPLOYMENT SCRIPT COMPLETE
echo ================================================================================
echo.
echo Git repository initialized and pushed to GitHub successfully!
echo.
echo Your repository: https://github.com/andenick/westchester
echo.
echo Next steps: Follow YOUR_DEPLOYMENT_COMMANDS.md (Phase 3 onwards)
echo.
pause
