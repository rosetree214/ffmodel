import os
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from sqlalchemy.orm import Session
from typing import List

from db import get_db, engine
from models import Base, Player
from schemas import (
    PlayerResponse, 
    SimulationRequest, 
    SimulationResponse, 
    ErrorResponse
)
from services import PlayerService
from monte_carlo import run_optimized_simulation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting FFModel API")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    yield
    # Shutdown
    logger.info("Shutting down FFModel API")

app = FastAPI(
    title="FFModel API",
    description="Fantasy Football Modeling Platform API",
    version="1.0.0",
    lifespan=lifespan
)

origins = [
    os.getenv('NETLIFY_URL', 'http://localhost:5173'),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add monitoring middleware
from monitoring import monitoring_middleware
app.middleware("http")(monitoring_middleware)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP {exc.status_code} error: {exc.detail}")
    return await http_exception_handler(request, exc)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred"
        ).dict()
    )

@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check endpoint"""
    from monitoring import health_checker
    
    # Basic service health
    health_status = {
        "status": "healthy",
        "service": "ffmodel-api",
        "timestamp": time.time()
    }
    
    # Database health
    db_health = health_checker.check_database_health(db)
    health_status["database"] = db_health
    
    # Cache health
    cache_health = health_checker.check_cache_health()
    health_status["cache"] = cache_health
    
    # System health
    system_health = health_checker.get_system_health()
    health_status["system"] = system_health
    
    # Overall status
    is_healthy = (
        db_health.get("status") == "healthy" and
        cache_health.get("status") == "healthy" and
        "error" not in system_health
    )
    
    health_status["status"] = "healthy" if is_healthy else "unhealthy"
    
    return health_status

@app.get("/api/metrics")
async def get_metrics():
    """Get application metrics"""
    from monitoring import metrics
    
    return {
        "service": "ffmodel-api",
        "timestamp": time.time(),
        "metrics": metrics.get_metrics()
    }

@app.get("/api/players", response_model=List[PlayerResponse])
async def get_players(db: Session = Depends(get_db)):
    try:
        logger.info("Fetching all players")
        PlayerService.ensure_players_loaded(db)
        players = PlayerService.get_all_players(db)
        logger.info(f"Retrieved {len(players)} players")
        return players
    except Exception as e:
        logger.error(f"Error fetching players: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch players")

@app.get("/api/players/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: str, db: Session = Depends(get_db)):
    try:
        logger.info(f"Fetching player with ID: {player_id}")
        player = PlayerService.get_player_by_id(db, player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        return player
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching player {player_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch player")

@app.post("/api/simulate", response_model=SimulationResponse)
async def simulate_draft(request: SimulationRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Starting simulation with settings: {request.dict()}")
        PlayerService.ensure_players_loaded(db)
        players = PlayerService.get_all_players(db)
        
        if not players:
            raise HTTPException(status_code=400, detail="No players available for simulation")
        
        results = run_optimized_simulation(players, request)
        logger.info(f"Simulation completed for {len(players)} players")
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running simulation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to run simulation") 