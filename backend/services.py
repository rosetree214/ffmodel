import pandas as pd
import os
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from models import Player, Team
from schemas import PlayerResponse
import logging

logger = logging.getLogger(__name__)

class PlayerService:
    @staticmethod
    def load_players_from_csv(db: Session, csv_path: str) -> None:
        """Load players from CSV into database"""
        try:
            df = pd.read_csv(csv_path)
            
            # Clear existing players
            db.query(Player).delete()
            db.commit()
            
            players = []
            for _, row in df.iterrows():
                player = Player(
                    player_id=str(row['player_id']),
                    name=row['name'],
                    position=row['position'],
                    points_proj=float(row['points_proj']),
                    std_dev=float(row['std_dev']),
                    adp_cost=float(row['adp_cost'])
                )
                players.append(player)
            
            db.bulk_save_objects(players)
            db.commit()
            logger.info(f"Loaded {len(players)} players from CSV")
            
        except Exception as e:
            logger.error(f"Error loading players from CSV: {e}")
            db.rollback()
            raise

    @staticmethod
    def get_all_players(db: Session) -> List[Player]:
        """Get all players from database"""
        return db.query(Player).all()

    @staticmethod
    def get_player_by_id(db: Session, player_id: str) -> Optional[Player]:
        """Get player by ID"""
        return db.query(Player).filter(Player.player_id == player_id).first()

    @staticmethod
    def get_players_by_position(db: Session, position: str) -> List[Player]:
        """Get players by position"""
        return db.query(Player).filter(Player.position == position).all()

    @staticmethod
    def ensure_players_loaded(db: Session) -> None:
        """Ensure players are loaded in database, load from CSV if empty"""
        count = db.query(Player).count()
        if count == 0:
            csv_path = os.path.join(os.path.dirname(__file__), '../data/players.csv')
            if os.path.exists(csv_path):
                PlayerService.load_players_from_csv(db, csv_path)
            else:
                logger.warning("No players.csv found and no players in database")

class CacheService:
    def __init__(self):
        self._cache = {}
    
    def get(self, key: str):
        return self._cache.get(key)
    
    def set(self, key: str, value, ttl: int = 300):
        self._cache[key] = value
    
    def delete(self, key: str):
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        self._cache.clear()

# Global cache instance
cache = CacheService()