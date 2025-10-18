@echo off
REM Westchester County Data Platform - One-Click Startup
REM This script starts both the API backend and frontend application

echo ====================================================================
echo  Westchester County Data Platform - Local Startup
echo ====================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ and try again
    pause
    exit /b 1
)

echo Step 1: Checking Python environment...
if not exist "Technical\venv\" (
    echo Creating Python virtual environment...
    pushd Technical
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    popd
    echo ✓ Python environment created
) else (
    echo ✓ Python environment exists
)

echo.

echo Step 2: Checking frontend dependencies...
if not exist "Technical\src\frontend\node_modules\" (
    echo Installing frontend dependencies...
    pushd Technical\src\frontend
    call npm install
    popd
    echo ✓ Frontend dependencies installed
) else (
    echo ✓ Frontend dependencies exist
)

echo.

echo Step 3: Starting API backend...
start "Westchester API" cmd /k "pushd Technical && venv\Scripts\activate && pushd src\api && python main.py && popd && popd"

timeout /t 2 >nul

echo ✓ API started on http://localhost:8000
echo   API Docs: http://localhost:8000/docs

echo.

echo Step 4: Starting frontend application...
start "Westchester Frontend" cmd /k "pushd Technical\src\frontend && npm run dev && popd"

timeout /t 3 >nul

echo.

echo ====================================================================
echo  ✓ Westchester County Data Platform is starting!
echo ====================================================================
echo.

echo  Frontend: http://localhost:3000 (or check terminal for actual port)
echo  API:      http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo.

echo  Press any key to close this window (servers will keep running)
echo  To stop servers, close the API and Frontend terminal windows
echo ====================================================================
pause