"""
Database migration script for Render deployment startup
"""
import os
import sys
import logging
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run database migrations on startup"""
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL not found in environment variables")
            return False
        
        # Create engine to test connection
        engine = create_engine(database_url)
        
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
        
        # Run Alembic migrations
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        logger.info("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
        
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Database error during migration: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during migration: {e}")
        return False

def initialize_sample_data():
    """Initialize sample data if database is empty"""
    try:
        from services import PlayerService
        from db import SessionLocal
        from models import Player
        
        db = SessionLocal()
        try:
            # Check if players exist
            count = db.query(Player).count()
            if count == 0:
                logger.info("No players found, attempting to load sample data...")
                csv_path = os.path.join(os.path.dirname(__file__), 'data', 'players.csv')
                if os.path.exists(csv_path):
                    PlayerService.load_players_from_csv(db, csv_path)
                    logger.info("Sample data loaded successfully")
                else:
                    logger.warning("No sample data file found")
            else:
                logger.info(f"Database already contains {count} players")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error loading sample data: {e}")

if __name__ == "__main__":
    success = run_migrations()
    if success:
        initialize_sample_data()
        logger.info("Database initialization complete")
        sys.exit(0)
    else:
        logger.error("Database initialization failed")
        sys.exit(1)