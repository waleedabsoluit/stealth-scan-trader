"""
STEALTH Bot FastAPI Backend
Main API server with health check and market data endpoints
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import json
from pathlib import Path
from contextlib import asynccontextmanager

# Import routes
from backend.api.routes.bot import router as bot_router
from backend.api.routes.market import router as market_router
from backend.api.routes.modules import router as modules_router
from backend.api.routes.signals import router as signals_router
from backend.api.routes.performance import router as performance_router
from backend.api.routes.risk import router as risk_router
from backend.api.routes.config import router as config_router
from backend.api.routes.logs import router as logs_router
from backend.api.routes.orchestration import router as orchestration_router

# Import logging setup
from backend.infra.file_logger import setup_file_logging, get_logger
from backend.infra.request_logger import LoggingRoute

# Import database
from backend.database import init_db

# Setup comprehensive logging
setup_file_logging(log_dir='logs', level=logging.INFO)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting STEALTH Bot API...")
    init_db()
    logger.info("✅ Database initialized")
    yield
    # Shutdown
    logger.info("🛑 Shutting down STEALTH Bot API...")


app = FastAPI(
    title="STEALTH Bot API", 
    version="1.0.0",
    # Use custom route class for request logging
    route_class=LoggingRoute,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bot_router, prefix="/api")
app.include_router(market_router, prefix="/api")
app.include_router(modules_router, prefix="/api")
app.include_router(signals_router, prefix="/api")
app.include_router(performance_router, prefix="/api")
app.include_router(risk_router, prefix="/api")
app.include_router(config_router, prefix="/api")
app.include_router(logs_router, prefix="/api")
app.include_router(orchestration_router, prefix="/api")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "success",
        "data": {
            "healthy": True,
            "timestamp": datetime.now().isoformat(),
            "service": "STEALTH Bot API",
            "version": "1.0.0"
        }
    }


@app.get("/api/health")
async def api_health_check():
    """API health check endpoint for Docker"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)