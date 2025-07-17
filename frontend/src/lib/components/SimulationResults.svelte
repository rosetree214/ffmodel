<script lang="ts">
  import type { SimulationResponse } from '../types';
  
  export let results: SimulationResponse | null = null;
  export let loading = false;
  
  function getTopPerformers(results: SimulationResponse, count = 10) {
    return results.results.slice(0, count);
  }
  
  function getBoomBustPlayers(results: SimulationResponse) {
    return results.results
      .filter(player => player.boom_pct > 25 || player.bust_pct > 25)
      .sort((a, b) => b.boom_pct - a.boom_pct);
  }
  
  function formatPercentage(value: number): string {
    return `${value.toFixed(1)}%`;
  }
</script>

{#if loading}
  <div class="loading-container">
    <div class="spinner"></div>
    <p>Running simulation...</p>
  </div>
{:else if results}
  <div class="results-container">
    <h2>Simulation Results</h2>
    
    <div class="metadata">
      <div class="stat">
        <span class="label">Players Analyzed:</span>
        <span class="value">{results.metadata.num_players}</span>
      </div>
      <div class="stat">
        <span class="label">Simulations Run:</span>
        <span class="value">{results.metadata.num_simulations.toLocaleString()}</span>
      </div>
      <div class="stat">
        <span class="label">Scoring Format:</span>
        <span class="value">{results.metadata.scoring_format.toUpperCase()}</span>
      </div>
      <div class="stat">
        <span class="label">Budget:</span>
        <span class="value">${results.metadata.budget}</span>
      </div>
      {#if results.metadata.optimized}
        <div class="stat">
          <span class="label">Optimization:</span>
          <span class="value optimized">✓ Vectorized</span>
        </div>
      {/if}
    </div>
    
    <div class="results-grid">
      <div class="result-section">
        <h3>Top Performers</h3>
        <div class="players-grid">
          {#each getTopPerformers(results) as player}
            <div class="player-card">
              <div class="player-header">
                <span class="player-name">{player.name}</span>
                <span class="player-mean">{player.mean} pts</span>
              </div>
              <div class="player-stats">
                <div class="stat-item">
                  <span class="stat-label">Std Dev:</span>
                  <span class="stat-value">{player.std}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Boom:</span>
                  <span class="stat-value boom">{formatPercentage(player.boom_pct)}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Bust:</span>
                  <span class="stat-value bust">{formatPercentage(player.bust_pct)}</span>
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>
      
      <div class="result-section">
        <h3>Boom/Bust Analysis</h3>
        <div class="boom-bust-list">
          {#each getBoomBustPlayers(results) as player}
            <div class="boom-bust-item">
              <div class="player-info">
                <span class="name">{player.name}</span>
                <span class="mean">{player.mean} pts</span>
              </div>
              <div class="percentages">
                <span class="boom">Boom: {formatPercentage(player.boom_pct)}</span>
                <span class="bust">Bust: {formatPercentage(player.bust_pct)}</span>
              </div>
            </div>
          {/each}
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  .results-container {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 1rem;
  }

  h2 {
    text-align: center;
    color: #1e293b;
    margin-bottom: 1.5rem;
  }

  .metadata {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    justify-content: center;
    margin-bottom: 2rem;
    padding: 1rem;
    background: #f8fafc;
    border-radius: 8px;
  }

  .stat {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .label {
    font-size: 0.875rem;
    color: #6b7280;
    margin-bottom: 0.25rem;
  }

  .value {
    font-weight: 600;
    color: #1e293b;
  }

  .optimized {
    color: #059669;
  }

  .results-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
  }

  .result-section {
    background: #fff;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  }

  .result-section h3 {
    margin-bottom: 1rem;
    color: #1e293b;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 0.5rem;
  }

  .players-grid {
    display: grid;
    gap: 1rem;
  }

  .player-card {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 1rem;
    background: #f9fafb;
  }

  .player-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .player-name {
    font-weight: 600;
    color: #1e293b;
  }

  .player-mean {
    font-weight: 700;
    color: #2563eb;
  }

  .player-stats {
    display: flex;
    gap: 1rem;
    font-size: 0.875rem;
  }

  .stat-item {
    display: flex;
    flex-direction: column;
  }

  .stat-label {
    color: #6b7280;
    font-size: 0.75rem;
  }

  .stat-value {
    font-weight: 600;
  }

  .boom {
    color: #059669;
  }

  .bust {
    color: #dc2626;
  }

  .boom-bust-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .boom-bust-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    background: #f9fafb;
  }

  .player-info {
    display: flex;
    flex-direction: column;
  }

  .name {
    font-weight: 600;
    color: #1e293b;
  }

  .mean {
    font-size: 0.875rem;
    color: #6b7280;
  }

  .percentages {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    text-align: right;
    font-size: 0.875rem;
    font-weight: 600;
  }

  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
  }

  .spinner {
    margin: 0 auto 1rem auto;
    border: 4px solid #e5e7eb;
    border-top: 4px solid #2563eb;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  @media (max-width: 768px) {
    .results-grid {
      grid-template-columns: 1fr;
    }
    
    .metadata {
      flex-direction: column;
      gap: 0.5rem;
    }
    
    .stat {
      flex-direction: row;
      justify-content: space-between;
    }
  }
</style>