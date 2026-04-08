import psycopg2

# REPLACE WITH YOUR IP
CLOUD_SQL_IP = "136.113.165.59" 
DB_USER = "aegis"
DB_PASSWORD = "aegis_secure_2024"
DB_NAME = "aegis_db"

def enable_extensions():
    try:
        conn = psycopg2.connect(
            host=CLOUD_SQL_IP,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Enabling pgvector extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        print("Enabling postgis extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        
        print("✅ SUCCESS: All database extensions enabled!")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    enable_extensions()