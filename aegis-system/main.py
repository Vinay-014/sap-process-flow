"""
AEGIS Command Center - Main Application Entry Point
FastAPI application with WebSocket, CORS, middleware, and database initialization.
"""

import os
import json
import uvicorn
import asyncio
import logging
import traceback
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.api.router import router
from src.db.engine import init_db, engine
from src.config import settings
from src.websocket_manager import websocket_manager
from src.data_fabric import data_fabric
from src.webhook_engine import webhook_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("aegis.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup, background tasks, shutdown."""
    logger.info("AEGIS Command Center starting up...")
    try:
        # 1. Initialize DB tables
        init_db()
        logger.info("Database initialized successfully")

        # 2. Auto-Seed Database if empty (so platform isn't empty on fresh deploy)
        try:
            from src.db.session import SessionLocal
            from src.db.models import Mission
            from src.data.seed_data import seed_database
            
            db = SessionLocal()
            mission_count = db.query(Mission).count()
            if mission_count == 0:
                logger.info("Database is empty. Seeding with initial demo data...")
                seed_database()
                logger.info("Database seeded successfully with 500+ entities.")
            else:
                logger.info(f"Database already contains {mission_count} missions. Skipping seed.")
            db.close()
        except Exception as e:
            logger.warning(f"Auto-seed skipped or failed (non-critical): {e}")

    except Exception as e:
        logger.error(f"CRITICAL DATABASE STARTUP ERROR: {str(e)}", exc_info=True)

    # Pre-warm connection
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
            logger.info("Database connection verified")
    except Exception as e:
        logger.warning(f"Database pre-warm failed (non-critical): {e}")

    # Start background monitoring
    asyncio.create_task(background_monitoring())

    logger.info("AEGIS Command Center ONLINE - Mode: ADVERSARIAL_WORKFLOW")
    yield

    # Shutdown
    logger.info("AEGIS Command Center shutting down...")


async def background_monitoring():
    """Continuous background intelligence gathering."""
    while True:
        try:
            intel = await data_fabric.fetch_intelligence()
            await websocket_manager.broadcast("intel", {
                "type": "intel_update",
                "data": intel,
            })
            logger.info(f"Background intel: {intel['total_intel']} items, {intel['threat_intel']} threats")
        except Exception as e:
            logger.error(f"Background monitoring error: {e}")
        await asyncio.sleep(300)  # Fetch every 5 minutes


# Create FastAPI application
app = FastAPI(
    title="AEGIS Command Center",
    version="3.0.0-PRODUCTION",
    description="Autonomous Executive & Geospatial Intelligence System - Enterprise OS",
    lifespan=lifespan
)

# CORS middleware for Next.js frontend
# Fixed: allow_credentials must be False when allow_origins is ["*"] to avoid browser CORS blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)


@app.websocket("/ws/{connection_id}")
async def websocket_endpoint(websocket: WebSocket, connection_id: str):
    """WebSocket endpoint for real-time updates."""
    channels = ["cop", "missions", "agents", "intel", "threats"]
    await websocket_manager.connect(websocket, connection_id, channels)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle client messages
            try:
                message = json.loads(data)
                if message.get("type") == "subscribe":
                    for ch in message.get("channels", []):
                        if ch in websocket_manager.subscribers:
                            websocket_manager.subscribers[ch].add(connection_id)
            except:
                pass
    except WebSocketDisconnect:
        await websocket_manager.disconnect(connection_id)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler with CORS headers."""
    logger.error(f"Unhandled exception on {request.url}: {exc}")
    logger.error(traceback.format_exc())
    response = JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if app.debug else "An unexpected error occurred",
            "endpoint": str(request.url)
        }
    )
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


@app.get("/")
def root():
    """Professional root endpoint for the API."""
    return {
        "message": "AEGIS Command Center API",
        "version": "3.0.0-PRODUCTION",
        "documentation": "/docs",
        "health": "/ping",
        "status": "Ready for integration"
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """Return empty 204 to prevent favicon 404 errors in browser."""
    from fastapi.responses import Response
    return Response(status_code=204)


@app.get("/ping")
def ping():
    """Health check endpoint."""
    return {
        "status": "AEGIS ONLINE",
        "mode": "ADVERSARIAL_WORKFLOW_ACTIVE",
        "version": "3.0.0-PRODUCTION",
    }


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
        ws="websockets",
    )
