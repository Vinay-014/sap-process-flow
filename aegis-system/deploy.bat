@echo off
REM AEGIS Cloud Run Deployment Script (Windows)
REM Reads API keys from .env file automatically

echo =====================================================
echo   AEGIS - Google Cloud Run Deployment
echo =====================================================
echo.

REM Step 1: Set your project ID
set /p PROJECT_ID=Enter your Google Cloud Project ID: 

REM Step 2: Set region
set /p REGION=Enter region (default: us-central1): 
if "%REGION%"=="" set REGION=us-central1

REM Step 3: Read API keys from .env file
for /f "tokens=1,* delims==" %%a in ('findstr "GOOGLE_API_KEY=" .env') do set GOOGLE_API_KEY=%%b
for /f "tokens=1,* delims==" %%a in ('findstr "GROQ_API_KEY=" .env') do set GROQ_API_KEY=%%b
for /f "tokens=1,* delims==" %%a in ('findstr "TOGETHER_API_KEY=" .env') do set TOGETHER_API_KEY=%%b

echo.
echo [1/6] Setting project...
gcloud config set project %PROJECT_ID%

echo [2/6] Enabling required APIs...
gcloud services enable run.googleapis.com cloudbuild.googleapis.com sqladmin.googleapis.com artifactregistry.googleapis.com

echo [3/6] Building and deploying backend...
gcloud builds submit --config cloudbuild.yaml --substitutions _PROJECT_ID=%PROJECT_ID%,_REGION=%REGION%,_GOOGLE_API_KEY=%GOOGLE_API_KEY%,_GROQ_API_KEY=%GROQ_API_KEY%,_TOGETHER_API_KEY=%TOGETHER_API_KEY%

echo.
echo [4/6] Getting deployment URLs...
for /f "tokens=*" %%a in ('gcloud run services describe aegis-backend --region=%REGION% --format="value(status.url)"') do set BACKEND_URL=%%a
for /f "tokens=*" %%a in ('gcloud run services describe aegis-frontend --region=%REGION% --format="value(status.url)"') do set FRONTEND_URL=%%a

echo.
echo =====================================================
echo   DEPLOYMENT COMPLETE
echo =====================================================
echo   Frontend: %FRONTEND_URL%
echo   Backend:  %BACKEND_URL%
echo   API Docs: %BACKEND_URL%/docs
echo.
echo   Database: Configure Cloud SQL PostgreSQL per CLOUDSQL_SETUP.md
echo   Connection: Cloud Run auto-connects via Unix socket
echo =====================================================
pause
