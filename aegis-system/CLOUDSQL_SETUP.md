# Cloud SQL PostgreSQL Setup for AEGIS

## 1. Create Cloud SQL Instance (via Console or gcloud)

```bash
# Create PostgreSQL instance
gcloud sql instances create aegis-db \
    --database-version=POSTGRES_16 \
    --cpu=2 \
    --memory=4GB \
    --region=us-central1 \
    --root-password=YOUR_ROOT_PASSWORD

# Create database
gcloud sql databases create aegis_db --instance=aegis-db
```

## 2. Enable pgvector and PostGIS Extensions

```bash
# Connect to instance
gcloud sql connect aegis-db --user=postgres --quiet

# Run these SQL commands:
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

# Create application user
CREATE USER aegis WITH PASSWORD 'aegis_secure_2024';
GRANT ALL PRIVILEGES ON DATABASE aegis_db TO aegis;
\c aegis_db
GRANT ALL ON SCHEMA public TO aegis;
```

## 3. Get Connection String

```bash
gcloud sql instances describe aegis-db --format="value(ipAddresses[0].ipAddress)"
# Returns: 35.222.XXX.XXX

# Cloud SQL Auth Proxy connection string:
DATABASE_URL=postgresql+psycopg2://aegis:aegis_secure_2024@/aegis_db?host=/cloudsql/PROJECT_ID:REGION:aegis-db
```

## 4. Update Cloud Run Backend Environment Variable

```bash
gcloud run services update aegis-backend \
    --region=us-central1 \
    --update-env-vars DATABASE_URL="postgresql+psycopg2://aegis:aegis_secure_2024@/aegis_db?host=/cloudsql=PROJECT_ID:us-central1:aegis-db"
```

## 5. Initialize Database Schema

```bash
# Run migration via Cloud Run job or local connection
gcloud sql connect aegis-db --user=aegis --quiet
# Then run: python -c "from src.db.engine import init_db; init_db()"
```

## Alternative: Use Existing Billing Account Project

If you already have a project with billing enabled:

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable sqladmin.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Then proceed with deployment
```
