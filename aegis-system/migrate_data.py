import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base, Mission, AgentLog, SpatialEvent, IntelReport # Add all your models here

# LOCAL DB (SQLite or whatever you used locally)
# If you used SQLite locally:
LOCAL_DB_URL = "sqlite:///./aegis_local.db" # Check your local .env for the exact local DB name

# CLOUD DB
CLOUD_SQL_IP = "136.113.165.59" 
CLOUD_DB_URL = f"postgresql+pg8000://aegis:aegis_secure_2024@{CLOUD_SQL_IP}:5432/aegis_db"

def migrate():
    print("Connecting to local and cloud databases...")
    try:
        local_engine = create_engine(LOCAL_DB_URL)
        cloud_engine = create_engine(CLOUD_DB_URL)
        
        LocalSession = sessionmaker(bind=local_engine)
        CloudSession = sessionmaker(bind=cloud_engine)
        
        local_sess = LocalSession()
        cloud_sess = CloudSession()
        
        # 1. Fetch all missions from local
        missions = local_sess.query(Mission).all()
        print(f"Found {len(missions)} missions locally.")
        
        for m in missions:
            # Check if already exists in cloud to avoid duplicates
            if not cloud_sess.query(Mission).filter(Mission.id == m.id).first():
                cloud_sess.add(m)
                
        cloud_sess.commit()
        print("✅ SUCCESS: Missions migrated to Cloud SQL!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        local_sess.close()
        cloud_sess.close()

if __name__ == "__main__":
    migrate()