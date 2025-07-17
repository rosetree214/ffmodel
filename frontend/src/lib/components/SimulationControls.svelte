<script lang="ts">
  import type { SimulationRequest } from '../types';
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher<{
    simulate: SimulationRequest;
  }>();
  
  export let disabled = false;
  export let loading = false;
  
  let budget = 200;
  let scoringFormat: 'standard' | 'ppr' | 'half_ppr' = 'standard';
  let numSimulations = 1000;
  
  function handleSimulate() {
    const request: SimulationRequest = {
      budget,
      scoring_format: scoringFormat,
      num_simulations: numSimulations,
    };
    
    dispatch('simulate', request);
  }
  
  function resetToDefaults() {
    budget = 200;
    scoringFormat = 'standard';
    numSimulations = 1000;
  }
</script>

<div class="simulation-controls">
  <h3>Simulation Settings</h3>
  
  <div class="controls-grid">
    <div class="control-group">
      <label for="budget">Budget ($)</label>
      <input 
        id="budget"
        type="number" 
        bind:value={budget}
        min="50"
        max="1000"
        step="10"
        {disabled}
      />
    </div>
    
    <div class="control-group">
      <label for="scoring">Scoring Format</label>
      <select id="scoring" bind:value={scoringFormat} {disabled}>
        <option value="standard">Standard</option>
        <option value="ppr">PPR</option>
        <option value="half_ppr">Half PPR</option>
      </select>
    </div>
    
    <div class="control-group">
      <label for="simulations">Simulations</label>
      <input 
        id="simulations"
        type="number" 
        bind:value={numSimulations}
        min="100"
        max="10000"
        step="100"
        {disabled}
      />
    </div>
  </div>
  
  <div class="button-group">
    <button 
      class="simulate-button" 
      on:click={handleSimulate} 
      disabled={disabled || loading}
    >
      {loading ? 'Simulating...' : 'Simulate Draft'}
    </button>
    
    <button 
      class="reset-button" 
      on:click={resetToDefaults}
      disabled={disabled || loading}
    >
      Reset
    </button>
  </div>
  
  <div class="info">
    <p>
      <strong>Budget:</strong> Total auction budget for draft simulation
    </p>
    <p>
      <strong>Scoring:</strong> Fantasy football scoring format
    </p>
    <p>
      <strong>Simulations:</strong> Number of Monte Carlo iterations (more = more accurate)
    </p>
  </div>
</div>

<style>
  .simulation-controls {
    max-width: 600px;
    margin: 2rem auto;
    padding: 1.5rem;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  }

  h3 {
    margin-bottom: 1.5rem;
    color: #1e293b;
    text-align: center;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 0.5rem;
  }

  .controls-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .control-group {
    display: flex;
    flex-direction: column;
  }

  label {
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
  }

  input, select {
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    font-size: 1rem;
    transition: border-color 0.2s;
  }

  input:focus, select:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }

  input:disabled, select:disabled {
    background-color: #f3f4f6;
    cursor: not-allowed;
  }

  .button-group {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-bottom: 1.5rem;
  }

  .simulate-button {
    background: #2563eb;
    color: #fff;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 6px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  .simulate-button:hover:not(:disabled) {
    background: #1d4ed8;
  }

  .simulate-button:disabled {
    background: #a5b4fc;
    cursor: not-allowed;
  }

  .reset-button {
    background: #6b7280;
    color: #fff;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .reset-button:hover:not(:disabled) {
    background: #4b5563;
  }

  .reset-button:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }

  .info {
    border-top: 1px solid #e2e8f0;
    padding-top: 1rem;
  }

  .info p {
    margin: 0.5rem 0;
    font-size: 0.875rem;
    color: #6b7280;
  }

  .info strong {
    color: #374151;
  }

  @media (max-width: 640px) {
    .controls-grid {
      grid-template-columns: 1fr;
    }
    
    .button-group {
      flex-direction: column;
    }
  }
</style>