#!/bin/bash
# AEGIS v2.0 - Setup Script
# This script sets up the entire AEGIS system for local development

set -e

echo "================================================"
echo "  AEGIS v2.0 - Setup Script"
echo "  Autonomous Executive & Geospatial Intelligence"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check prerequisites
echo -e "${YELLOW}[1/6] Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 not found. Please install Python 3.12+${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js not found. Please install Node.js 20+${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found. PostgreSQL must be installed separately.${NC}"
fi

echo -e "${GREEN}✓ Prerequisites check complete${NC}"
echo ""

# Step 2: Start PostgreSQL
echo -e "${YELLOW}[2/6] Starting PostgreSQL...${NC}"

if command -v docker &> /dev/null; then
    docker-compose up -d postgres
    echo "Waiting for PostgreSQL to be ready..."
    sleep 10
    echo -e "${GREEN}✓ PostgreSQL started${NC}"
else
    echo -e "${YELLOW}Docker not available. Ensure PostgreSQL is running on port 5432${NC}"
fi
echo ""

# Step 3: Setup Python environment
echo -e "${YELLOW}[3/6] Setting up Python environment...${NC}"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

# Step 4: Setup environment variables
echo -e "${YELLOW}[4/6] Configuring environment...${NC}"

if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || true
fi

echo "Enter your Google API Key (for Gemini):"
read -r api_key
if [ -n "$api_key" ]; then
    # Update or create .env with API key
    if grep -q "GOOGLE_API_KEY" .env 2>/dev/null; then
        sed -i.bak "s/GOOGLE_API_KEY=.*/GOOGLE_API_KEY=$api_key/" .env
    else
        echo "GOOGLE_API_KEY=$api_key" >> .env
    fi
    export GOOGLE_API_KEY="$api_key"
    echo -e "${GREEN}✓ API key configured${NC}"
else
    echo -e "${YELLOW}⚠ No API key provided. You can add it later to .env${NC}"
fi
echo ""

# Step 5: Setup frontend
echo -e "${YELLOW}[5/6] Setting up frontend...${NC}"

cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ..

echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
echo ""

# Step 6: Initialize database
echo -e "${YELLOW}[6/6] Initializing database...${NC}"

source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
python -c "
from src.db.engine import init_db
try:
    init_db()
    print('✓ Database initialized successfully')
except Exception as e:
    print(f'⚠ Database initialization warning: {e}')
"
echo ""

# Done
echo "================================================"
echo -e "${GREEN}  AEGIS Setup Complete!${NC}"
echo "================================================"
echo ""
echo "To start the system:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    source venv/bin/activate"
echo "    python main.py"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd frontend && npm run dev"
echo ""
echo "  Or use Docker:"
echo "    docker-compose up"
echo ""
echo "Access:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
