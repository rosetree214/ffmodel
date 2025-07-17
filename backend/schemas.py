from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class Position(str, Enum):
    QB = "QB"
    RB = "RB"
    WR = "WR"
    TE = "TE"
    K = "K"
    DST = "DST"

class ScoringFormat(str, Enum):
    STANDARD = "standard"
    PPR = "ppr"
    HALF_PPR = "half_ppr"

class PlayerResponse(BaseModel):
    player_id: str
    name: str
    position: Position
    points_proj: float
    std_dev: float
    adp_cost: float
    
    class Config:
        from_attributes = True

class SimulationRequest(BaseModel):
    budget: Optional[int] = Field(default=200, ge=50, le=1000)
    scoring_format: Optional[ScoringFormat] = ScoringFormat.STANDARD
    num_simulations: Optional[int] = Field(default=1000, ge=100, le=10000)
    adp_overrides: Optional[Dict[str, float]] = None

class SimulationResult(BaseModel):
    player_id: str
    name: str
    mean: float
    std: float
    boom_pct: float
    bust_pct: float

class SimulationResponse(BaseModel):
    results: List[SimulationResult]
    metadata: Dict[str, Any]

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[int] = None