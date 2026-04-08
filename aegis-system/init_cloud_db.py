import sys
import os
from sqlalchemy import create_engine

# Import Base from your src folder
sys.path.append(os.path.dirname(__file__))
from src.db.models import Base 

# REPLACE THIS WITH THE IP FROM STEP 1
CLOUD_SQL_IP = "136.113.165.59" 
DB_USER = "aegis"
DB_PASSWORD = "aegis_secure_2024"
DB_NAME = "aegis_db"

DATABASE_URL = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{CLOUD_SQL_IP}:5432/{DB_NAME}"

def init_db():
    print(f"Connecting to {CLOUD_SQL_IP}...")
    try:
        engine = create_engine(DATABASE_URL)
        print("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ SUCCESS: Database tables created on Cloud SQL!")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("Check if your IP is authorized in Cloud SQL Console.")

if __name__ == "__main__":
    init_db()