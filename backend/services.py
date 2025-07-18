import logging
import os
from typing import List, Optional

import pandas as pd
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from models import Player, Team
from schemas import PlayerCSVInput, PlayerResponse

logger = logging.getLogger(__name__)


class PlayerService:
    @staticmethod
    def load_players_from_csv(db: Session, csv_path: str) -> None:
        """Load players from CSV into database with validation"""
        try:
            df = pd.read_csv(csv_path)

            # Validate CSV structure
            required_columns = [
                "player_id",
                "name",
                "position",
                "points_proj",
                "std_dev",
                "adp_cost",
            ]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            # Clear existing players
            db.query(Player).delete()
            db.commit()

            players = []
            validation_errors = []

            for idx, row in df.iterrows():
                try:
                    # Validate each row using Pydantic
                    validated_data = PlayerCSVInput(
                        player_id=str(row["player_id"]),
                        name=str(row["name"]),
                        position=str(row["position"]),
                        points_proj=float(row["points_proj"]),
                        std_dev=float(row["std_dev"]),
                        adp_cost=float(row["adp_cost"]),
                    )

                    player = Player(
                        player_id=validated_data.player_id,
                        name=validated_data.name,
                        position=validated_data.position,
                        points_proj=validated_data.points_proj,
                        std_dev=validated_data.std_dev,
                        adp_cost=validated_data.adp_cost,
                    )
                    players.append(player)

                except ValidationError as ve:
                    validation_errors.append(f"Row {idx + 1}: {ve}")
                    logger.warning(f"Validation error in row {idx + 1}: {ve}")
                except (ValueError, TypeError) as e:
                    validation_errors.append(f"Row {idx + 1}: {e}")
                    logger.warning(f"Data error in row {idx + 1}: {e}")

            if validation_errors:
                error_summary = f"Found {len(validation_errors)} validation errors"
                logger.error(error_summary)
                raise ValueError(f"{error_summary}. First few errors: {validation_errors[:5]}")

            db.bulk_save_objects(players)
            db.commit()
            logger.info(f"Successfully loaded {len(players)} players from CSV")

        except FileNotFoundError:
            logger.error(f"CSV file not found: {csv_path}")
            raise
        except pd.errors.EmptyDataError:
            logger.error(f"CSV file is empty: {csv_path}")
            raise ValueError("CSV file is empty")
        except pd.errors.ParserError as e:
            logger.error(f"CSV parsing error: {e}")
            raise ValueError(f"CSV parsing error: {e}")
        except SQLAlchemyError as e:
            logger.error(f"Database error loading players: {e}")
            db.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading players from CSV: {e}")
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
        try:
            count = db.query(Player).count()
            if count == 0:
                csv_path = os.path.join(os.path.dirname(__file__), "../data/players.csv")
                if os.path.exists(csv_path):
                    # Use a lock to prevent concurrent loading
                    import threading

                    if not hasattr(PlayerService, "_loading_lock"):
                        PlayerService._loading_lock = threading.Lock()

                    with PlayerService._loading_lock:
                        # Double-check after acquiring lock
                        count = db.query(Player).count()
                        if count == 0:
                            PlayerService.load_players_from_csv(db, csv_path)
                else:
                    logger.warning("No players.csv found and no players in database")
        except SQLAlchemyError as e:
            logger.error(f"Database error checking player count: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error ensuring players loaded: {e}")
            raise


import json

import redis


class CacheService:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            # For local development, use a basic Redis URL
            redis_url = "redis://localhost:6379"
            logger.warning("REDIS_URL not set, using default localhost connection")

        # Parse Redis URL to add authentication if needed
        redis_password = os.getenv("REDIS_PASSWORD")
        if redis_password and "@" not in redis_url:
            # Add password to URL if not already present
            redis_url = redis_url.replace("redis://", f"redis://:{redis_password}@")

        try:
            self._redis = redis.from_url(
                redis_url,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            # Test connection
            self._redis.ping()
            logger.info("Redis connection established successfully")
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Redis initialization error: {e}")
            raise

    def get(self, key: str):
        try:
            value = self._redis.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value.decode("utf-8")
            return None
        except redis.ConnectionError as e:
            logger.error(f"Redis get operation failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value, ttl: int = 300):
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            self._redis.set(key, value, ex=ttl)
        except redis.ConnectionError as e:
            logger.error(f"Redis set operation failed: {e}")
        except Exception as e:
            logger.error(f"Cache set error: {e}")

    def delete(self, key: str):
        try:
            self._redis.delete(key)
        except redis.ConnectionError as e:
            logger.error(f"Redis delete operation failed: {e}")
        except Exception as e:
            logger.error(f"Cache delete error: {e}")

    def clear(self):
        try:
            self._redis.flushdb()
        except redis.ConnectionError as e:
            logger.error(f"Redis clear operation failed: {e}")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")


# Global cache instance
cache = CacheService()
