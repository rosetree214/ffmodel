from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    
    # Relationship
    players = relationship("Player", back_populates="team")

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    player_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    position = Column(String, nullable=False, index=True)
    points_proj = Column(Float, nullable=False)
    std_dev = Column(Float, nullable=False)
    adp_cost = Column(Float, nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    team = relationship("Team", back_populates="players")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_player_position_cost', 'position', 'adp_cost'),
        Index('idx_player_projection', 'points_proj'),
    )

class DraftConfig(Base):
    __tablename__ = 'draft_configs'
    id = Column(Integer, primary_key=True)
    budget = Column(Integer, nullable=False)
    scoring_format = Column(String, nullable=False)
    adp_overrides = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class SimulationCache(Base):
    __tablename__ = 'simulation_cache'
    id = Column(Integer, primary_key=True)
    cache_key = Column(String, unique=True, nullable=False, index=True)
    result = Column(String, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False) 