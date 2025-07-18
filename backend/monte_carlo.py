import hashlib
import json
import logging
from typing import Any, Dict, List

import numpy as np

from models import Player
from schemas import SimulationRequest, SimulationResult
from services import cache

logger = logging.getLogger(__name__)


def generate_cache_key(players: List[Player], settings: SimulationRequest) -> str:
    """Generate a unique cache key for simulation parameters"""
    player_data = [(p.player_id, p.points_proj, p.std_dev, p.adp_cost) for p in players]
    key_data = {"players": player_data, "settings": settings.dict()}
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()


def run_simulation(players: List[Player], settings: SimulationRequest = None) -> Dict[str, Any]:
    """Run Monte Carlo simulation with caching"""
    if settings is None:
        settings = SimulationRequest()

    # Check cache first
    cache_key = generate_cache_key(players, settings)
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"Cache hit for simulation key: {cache_key}")
        return cached_result

    logger.info(
        f"Running simulation for {len(players)} players with {settings.num_simulations} iterations"
    )

    # Set random seed for reproducibility
    np.random.seed(42)

    results = []
    for player in players:
        # Apply ADP overrides if provided
        adp_cost = player.adp_cost
        if settings.adp_overrides and player.player_id in settings.adp_overrides:
            adp_cost = settings.adp_overrides[player.player_id]

        # Generate random points based on projection and standard deviation
        points = np.random.normal(player.points_proj, player.std_dev, settings.num_simulations)

        # Calculate statistics
        mean = np.mean(points)
        std = np.std(points)
        boom_threshold = player.points_proj + player.std_dev
        bust_threshold = player.points_proj - player.std_dev

        boom_pct = np.mean(points > boom_threshold) * 100
        bust_pct = np.mean(points < bust_threshold) * 100

        # Calculate value metrics (currently unused but available for future features)
        # value_per_dollar = player.points_proj / adp_cost if adp_cost > 0 else 0

        result = SimulationResult(
            player_id=player.player_id,
            name=player.name,
            mean=round(mean, 2),
            std=round(std, 2),
            boom_pct=round(boom_pct, 1),
            bust_pct=round(bust_pct, 1),
        )
        results.append(result)

    # Sort by projected points descending
    results.sort(key=lambda x: x.mean, reverse=True)

    response = {
        "results": [r.dict() for r in results],
        "metadata": {
            "num_simulations": settings.num_simulations,
            "num_players": len(players),
            "scoring_format": settings.scoring_format,
            "budget": settings.budget,
            "cache_key": cache_key,
        },
    }

    # Cache the result for 5 minutes
    cache.set(cache_key, response, ttl=300)
    logger.info(f"Cached simulation result with key: {cache_key}")

    return response


def run_optimized_simulation(
    players: List[Player], settings: SimulationRequest = None
) -> Dict[str, Any]:
    """Vectorized Monte Carlo simulation for better performance"""
    if settings is None:
        settings = SimulationRequest()

    # Check cache first
    cache_key = generate_cache_key(players, settings)
    cached_result = cache.get(cache_key)
    if cached_result:
        logger.info(f"Cache hit for optimized simulation key: {cache_key}")
        return cached_result

    logger.info(f"Running optimized simulation for {len(players)} players")

    # Vectorized approach - generate all simulations at once
    np.random.seed(42)

    # Create arrays for all players
    projections = np.array([p.points_proj for p in players])
    std_devs = np.array([p.std_dev for p in players])

    # Generate all random samples at once (players x simulations)
    random_samples = np.random.normal(
        projections[:, np.newaxis],
        std_devs[:, np.newaxis],
        (len(players), settings.num_simulations),
    )

    # Calculate statistics vectorized
    means = np.mean(random_samples, axis=1)
    stds = np.std(random_samples, axis=1)

    # Calculate boom/bust percentages
    boom_thresholds = projections + std_devs
    bust_thresholds = projections - std_devs

    boom_pcts = np.mean(random_samples > boom_thresholds[:, np.newaxis], axis=1) * 100
    bust_pcts = np.mean(random_samples < bust_thresholds[:, np.newaxis], axis=1) * 100

    # Build results
    results = []
    for i, player in enumerate(players):
        result = SimulationResult(
            player_id=player.player_id,
            name=player.name,
            mean=round(means[i], 2),
            std=round(stds[i], 2),
            boom_pct=round(boom_pcts[i], 1),
            bust_pct=round(bust_pcts[i], 1),
        )
        results.append(result)

    # Sort by projected points descending
    results.sort(key=lambda x: x.mean, reverse=True)

    response = {
        "results": [r.dict() for r in results],
        "metadata": {
            "num_simulations": settings.num_simulations,
            "num_players": len(players),
            "scoring_format": settings.scoring_format,
            "budget": settings.budget,
            "cache_key": cache_key,
            "optimized": True,
        },
    }

    # Cache the result for 5 minutes
    cache.set(cache_key, response, ttl=300)
    logger.info(f"Cached optimized simulation result with key: {cache_key}")

    return response
