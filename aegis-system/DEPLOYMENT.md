# AEGIS — Google Cloud Run Deployment Guide

## Quick Deploy (5 Steps)

### Step 1: Install gcloud CLI
```bash
# Download from: https://cloud.google.com/sdk/docs/install
# Then authenticate:
gcloud auth login
gcloud auth application-default login
```

### Step 2: Set Your Project
```bash
# Replace with your actual project ID
gcloud config set project YOUR_PROJECT_ID

# Verify billing is enabled
gcloud billing accounts list
gcloud billing projects describe YOUR_PROJECT_ID
```

### Step 3: Enable APIs
```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com sqladmin.googleapis.com
```

### Step 4: Deploy (Automated)
```bash
# Run the deployment script
deploy.bat    # Windows
./deploy.sh   # Linux/Mac

# Or deploy manually:
gcloud builds submit --config cloudbuild.yaml \
    --substitutions _PROJECT_ID=YOUR_PROJECT_ID,_REGION=us-central1
```

### Step 5: Set Up Database
```bash
# Create Cloud SQL PostgreSQL instance
gcloud sql instances create aegis-db \
    --database-version=POSTGRES_16 \
    --cpu=2 \
    --memory=4GB \
    --region=us-central1

# Follow CLOUDSQL_SETUP.md for extension setup
```

---

## Manual Deploy Commands

### Backend Only
```bash
gcloud run deploy aegis-backend \
    --source . \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars ^|^|^
        GOOGLE_API_KEY=YOUR_KEY,GROQ_API_KEY=YOUR_KEY,TOGETHER_API_KEY=YOUR_KEY,LLM_MODEL=gemini-2.5-flash,RED_TEAM_THRESHOLD=0.65 \
    --cpu 2 \
    --memory 2Gi \
    --timeout 300s
```

### Frontend Only
```bash
cd frontend
gcloud run deploy aegis-frontend \
    --source . \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars NEXT_PUBLIC_API_URL=https://YOUR_BACKEND_URL \
    --cpu 1 \
    --memory 512Mi
```

---

## After Deployment

1. **Frontend URL:** `gcloud run services describe aegis-frontend --region=us-central1 --format="value(status.url)"`
2. **Backend URL:** `gcloud run services describe aegis-backend --region=us-central1 --format="value(status.url)"`
3. **API Docs:** `{BACKEND_URL}/docs`

---

## Cost Estimate (Monthly)

| Service | Spec | Est. Cost |
|---|---|---|
| Cloud Run Backend | 2 CPU, 2Gi RAM, 1 min instance | ~$15-30 |
| Cloud Run Frontend | 1 CPU, 512Mi RAM, 0 min instances | ~$5-10 |
| Cloud SQL PostgreSQL | 2 CPU, 4Gi RAM | ~$45-60 |
| **Total** | | **~$65-100/month** |

With Cloud Run's free tier and scale-to-zero, actual costs will be lower for demo/hackathon usage.

---

## Troubleshooting

### Build fails
```bash
# Check build logs
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

### Service won't start
```bash
# Check logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=aegis-backend" --limit=20
```

### Database connection fails
```bash
# Test connection
gcloud sql connect aegis-db --user=aegis --quiet
# Run: SELECT 1;
```
