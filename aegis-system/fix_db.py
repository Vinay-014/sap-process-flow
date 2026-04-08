"""
AEGIS Database Fix Utility
Resolves common database initialization issues.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.db.engine import engine, init_db
from sqlalchemy import text

def check_connection():
    """Test database connection."""
    print("Testing database connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure PostgreSQL is running: docker-compose up -d postgres")
        print("  2. Check .env DATABASE_URL matches your setup")
        print("  3. Verify credentials: aegis / aegis_secure_2024")
        return False

def reset_database():
    """Drop and recreate all tables."""
    print("\nResetting database...")
    try:
        from src.db.models import Base
        Base.metadata.drop_all(bind=engine)
        print("✓ All tables dropped")
        Base.metadata.create_all(bind=engine)
        print("✓ All tables recreated")

        # Enable extensions
        with engine.connect() as conn:
            for ext in [
                "CREATE EXTENSION IF NOT EXISTS vector;",
                "CREATE EXTENSION IF NOT EXISTS postgis;",
                "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
            ]:
                try:
                    conn.execute(text(ext))
                    conn.commit()
                except Exception as e:
                    print(f"  Warning: {e}")

        print("✓ Database reset complete")
        return True
    except Exception as e:
        print(f"✗ Database reset failed: {e}")
        return False

def show_tables():
    """List all tables in the database."""
    print("\nDatabase tables:")
    try:
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;"
            ))
            tables = [row[0] for row in result.fetchall()]
            if tables:
                for table in tables:
                    print(f"  - {table}")
            else:
                print("  (no tables found)")
        return True
    except Exception as e:
        print(f"✗ Failed to list tables: {e}")
        return False

def show_stats():
    """Show database statistics."""
    print("\nDatabase statistics:")
    try:
        with engine.connect() as conn:
            tables = {
                "missions": "Mission records",
                "task_trees": "Task tree roots",
                "task_tree_nodes": "Task nodes",
                "canaries": "Canary entries",
                "intel_reports": "Intel with embeddings",
                "spatial_events": "Geospatial events",
                "agent_logs": "Agent execution logs",
                "debate_rounds": "Adversarial debate rounds",
            }
            for table, desc in tables.items():
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print(f"  {table:25s} {count:5d} records  ({desc})")
                except:
                    print(f"  {table:25s}   N/A    ({desc})")
        return True
    except Exception as e:
        print(f"✗ Failed to get stats: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("  AEGIS Database Fix Utility")
    print("=" * 50)
    print()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        print("Commands: check, reset, tables, stats")
        command = input("Enter command (or press Enter for 'check'): ").strip() or "check"

    if command == "check":
        check_connection()
    elif command == "reset":
        if input("This will DELETE all data. Continue? (y/n): ").lower() == "y":
            reset_database()
    elif command == "tables":
        check_connection() and show_tables()
    elif command == "stats":
        check_connection() and show_stats()
    else:
        print(f"Unknown command: {command}")
        print("Available: check, reset, tables, stats")
