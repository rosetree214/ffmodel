export interface Player {
  player_id: string;
  name: string;
  position: string;
  points_proj: number;
  std_dev: number;
  adp_cost: number;
}

export interface SimulationResult {
  player_id: string;
  name: string;
  mean: number;
  std: number;
  boom_pct: number;
  bust_pct: number;
}

export interface SimulationResponse {
  results: SimulationResult[];
  metadata: {
    num_simulations: number;
    num_players: number;
    scoring_format: string;
    budget: number;
    cache_key: string;
    optimized?: boolean;
  };
}

export interface SimulationRequest {
  budget?: number;
  scoring_format?: 'standard' | 'ppr' | 'half_ppr';
  num_simulations?: number;
  adp_overrides?: Record<string, number>;
}

export interface ApiError {
  error: string;
  detail?: string;
  code?: number;
}