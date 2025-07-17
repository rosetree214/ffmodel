<script lang="ts">
  import { onMount } from 'svelte';
  import type { Player, SimulationResponse, SimulationRequest } from '../lib/types';
  import { api } from '../lib/api';
  import PlayersTable from '../lib/components/PlayersTable.svelte';
  import SimulationControls from '../lib/components/SimulationControls.svelte';
  import SimulationResults from '../lib/components/SimulationResults.svelte';
  
  let players: Player[] = [];
  let loading = true;
  let error = '';
  let simulationResults: SimulationResponse | null = null;
  let simulating = false;
  
  onMount(async () => {
    await loadPlayers();
  });
  
  async function loadPlayers() {
    loading = true;
    error = '';
    try {
      players = await api.getPlayers();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Unknown error loading players.';
    } finally {
      loading = false;
    }
  }
  
  async function handleSimulate(event: CustomEvent<SimulationRequest>) {
    simulationResults = null;
    simulating = true;
    error = '';
    
    try {
      simulationResults = await api.simulateDraft(event.detail);
    } catch (e) {
      error = e instanceof Error ? e.message : 'Unknown error running simulation.';
    } finally {
      simulating = false;
    }
  }
</script>

<main>
  <h1>Fantasy Football Dashboard</h1>
  
  {#if error}
    <div class="error">{error}</div>
  {/if}
  
  <PlayersTable {players} {loading} {error} />
  
  {#if players.length > 0}
    <SimulationControls 
      disabled={loading || simulating}
      loading={simulating}
      on:simulate={handleSimulate}
    />
  {/if}
  
  <SimulationResults results={simulationResults} loading={simulating} />
</main>

<style>
  :global(body) {
    font-family: system-ui, sans-serif;
    background: #f8fafc;
    margin: 0;
    line-height: 1.5;
  }
  
  main {
    min-height: 100vh;
    padding: 1rem;
  }
  
  h1 {
    text-align: center;
    margin: 1.5rem 0;
    color: #1e293b;
    font-size: 2.5rem;
    font-weight: 700;
  }
  
  .error {
    color: #dc2626;
    background: #fee2e2;
    border: 1px solid #fca5a5;
    padding: 1rem;
    border-radius: 6px;
    max-width: 600px;
    margin: 2rem auto;
    text-align: center;
    font-weight: 500;
  }
  
  @media (max-width: 640px) {
    h1 {
      font-size: 2rem;
    }
    
    main {
      padding: 0.5rem;
    }
  }
</style>
