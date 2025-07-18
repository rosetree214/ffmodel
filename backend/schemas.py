import re
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


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


class PlayerCSVInput(BaseModel):
    player_id: str
    name: str
    position: str
    points_proj: float
    std_dev: float
    adp_cost: float

    @validator("player_id")
    def validate_player_id(cls, v):
        if not v or not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError("Player ID must be a non-empty string")
        return v.strip()

    @validator("name")
    def validate_name(cls, v):
        if not v or not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError("Player name must be a non-empty string")
        # Remove potential HTML/script tags
        clean_name = re.sub(r"<[^>]*>", "", v.strip())
        if len(clean_name) > 100:
            raise ValueError("Player name must be less than 100 characters")
        return clean_name

    @validator("position")
    def validate_position(cls, v):
        valid_positions = ["QB", "RB", "WR", "TE", "K", "DST"]
        if v not in valid_positions:
            raise ValueError(f"Position must be one of {valid_positions}")
        return v

    @validator("points_proj", "std_dev", "adp_cost")
    def validate_numeric_fields(cls, v, field):
        if not isinstance(v, (int, float)) or v < 0:
            raise ValueError(f"{field.name} must be a non-negative number")
        if field.name == "points_proj" and v > 500:
            raise ValueError("Points projection seems unrealistically high")
        if field.name == "std_dev" and v > 200:
            raise ValueError("Standard deviation seems unrealistically high")
        if field.name == "adp_cost" and v > 1000:
            raise ValueError("ADP cost seems unrealistically high")
        return float(v)


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[int] = None
