@echo off
REM AEGIS v2.0 - Windows Setup Script
REM This script sets up the entire AEGIS system for local development

echo ================================================
echo   AEGIS v2.0 - Setup Script
echo   Autonomous Executive ^& Geospatial Intelligence
echo ================================================
echo.

REM Step 1: Check prerequisites
echo [1/6] Checking prerequisites...

python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3 not found. Please install Python 3.12+
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js not found. Please install Node.js 20+
    pause
    exit /b 1
)

echo [OK] Prerequisites check complete
echo.

REM Step 2: Start PostgreSQL
echo [2/6] Starting PostgreSQL...

docker --version >nul 2>&1
if not errorlevel 1 (
    docker-compose up -d postgres
    echo Waiting for PostgreSQL to be ready...
    timeout /t 10 /nobreak >nul
    echo [OK] PostgreSQL started
) else (
    echo Docker not available. Ensure PostgreSQL is running on port 5432
)
echo.

REM Step 3: Setup Python environment
echo [3/6] Setting up Python environment...

if not exist "venv" (
    python -m venv venv
)

call venv\Scripts\activate

pip install -r requirements.txt --quiet
echo [OK] Python dependencies installed
echo.

REM Step 4: Setup environment variables
echo [4/6] Configuring environment...

set /p api_key="Enter your Google API Key (for Gemini): "
if not "%api_key%"=="" (
    echo GOOGLE_API_KEY=%api_key%> .env
    set GOOGLE_API_KEY=%api_key%
    echo [OK] API key configured
) else (
    echo [!] No API key provided. You can add it later to .env
)
echo.

REM Step 5: Setup frontend
echo [5/6] Setting up frontend...

cd frontend
if not exist "node_modules" (
    call npm install
)
cd ..

echo [OK] Frontend dependencies installed
echo.

REM Step 6: Initialize database
echo [6/6] Initializing database...

call venv\Scripts\activate
python -c "from src.db.engine import init_db; init_db()"
echo.

REM Done
echo ================================================
echo   AEGIS Setup Complete!
echo ================================================
echo.
echo To start the system:
echo.
echo   Terminal 1 (Backend):
echo     venv\Scripts\activate
echo     python main.py
echo.
echo   Terminal 2 (Frontend):
echo     cd frontend ^&^& npm run dev
echo.
echo   Or use Docker:
echo     docker-compose up
echo.
echo Access:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
pause
