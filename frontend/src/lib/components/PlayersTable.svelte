<script lang="ts">
  import type { Player } from '../types';
  
  export let players: Player[] = [];
  export let loading = false;
  export let error = '';
  
  function calculateValue(player: Player): number {
    return player.adp_cost > 0 ? player.points_proj / player.adp_cost : 0;
  }
  
  function formatValue(value: number): string {
    return value.toFixed(2);
  }
  
  function sortPlayers(players: Player[], sortBy: keyof Player, ascending = false): Player[] {
    return [...players].sort((a, b) => {
      const aVal = a[sortBy];
      const bVal = b[sortBy];
      
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return ascending ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return ascending ? aVal - bVal : bVal - aVal;
      }
      
      return 0;
    });
  }
  
  let sortBy: keyof Player = 'points_proj';
  let ascending = false;
  
  $: sortedPlayers = sortPlayers(players, sortBy, ascending);
  
  function handleSort(column: keyof Player) {
    if (sortBy === column) {
      ascending = !ascending;
    } else {
      sortBy = column;
      ascending = false;
    }
  }
</script>

{#if loading}
  <div class="loading-container">
    <div class="spinner"></div>
    <p>Loading players...</p>
  </div>
{:else if error}
  <div class="error">{error}</div>
{:else if players.length === 0}
  <div class="empty-state">
    <p>No players found.</p>
  </div>
{:else}
  <div class="table-container">
    <table>
      <thead>
        <tr>
          <th>
            <button class="sort-button" on:click={() => handleSort('name')}>
              Name {sortBy === 'name' ? (ascending ? '↑' : '↓') : ''}
            </button>
          </th>
          <th>
            <button class="sort-button" on:click={() => handleSort('position')}>
              Position {sortBy === 'position' ? (ascending ? '↑' : '↓') : ''}
            </button>
          </th>
          <th>
            <button class="sort-button" on:click={() => handleSort('points_proj')}>
              Proj. Points {sortBy === 'points_proj' ? (ascending ? '↑' : '↓') : ''}
            </button>
          </th>
          <th>
            <button class="sort-button" on:click={() => handleSort('std_dev')}>
              Std Dev {sortBy === 'std_dev' ? (ascending ? '↑' : '↓') : ''}
            </button>
          </th>
          <th>
            <button class="sort-button" on:click={() => handleSort('adp_cost')}>
              ADP Cost {sortBy === 'adp_cost' ? (ascending ? '↑' : '↓') : ''}
            </button>
          </th>
          <th>EV/$</th>
        </tr>
      </thead>
      <tbody>
        {#each sortedPlayers as player}
          <tr>
            <td class="player-name">{player.name}</td>
            <td class="position position-{player.position.toLowerCase()}">{player.position}</td>
            <td class="number">{player.points_proj}</td>
            <td class="number">{player.std_dev}</td>
            <td class="number">${player.adp_cost}</td>
            <td class="number value">{formatValue(calculateValue(player))}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}

<style>
  .table-container {
    overflow-x: auto;
    margin: 2rem auto 1rem auto;
    max-width: 1000px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    padding: 1rem;
  }

  table {
    border-collapse: collapse;
    width: 100%;
    min-width: 600px;
  }

  th, td {
    border: 1px solid #e2e8f0;
    padding: 0.6em 1em;
    text-align: left;
  }

  th {
    background: #f1f5f9;
    color: #334155;
    font-weight: 600;
  }

  .sort-button {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    font-weight: inherit;
    padding: 0;
    text-align: left;
    width: 100%;
    font-size: inherit;
  }

  .sort-button:hover {
    color: #2563eb;
  }

  .number {
    text-align: right;
  }

  .player-name {
    font-weight: 500;
  }

  .position {
    font-weight: 600;
    text-align: center;
  }

  .position-qb { color: #dc2626; }
  .position-rb { color: #059669; }
  .position-wr { color: #2563eb; }
  .position-te { color: #7c3aed; }
  .position-k { color: #ea580c; }
  .position-dst { color: #374151; }

  .value {
    font-weight: 600;
    color: #059669;
  }

  tr:nth-child(even) {
    background: #f9fafb;
  }

  tr:hover {
    background: #e0e7ef;
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

  .error {
    color: #dc2626;
    background: #fee2e2;
    border: 1px solid #fca5a5;
    padding: 1em;
    border-radius: 6px;
    max-width: 600px;
    margin: 2rem auto;
    text-align: center;
  }

  .empty-state {
    text-align: center;
    padding: 2rem;
    color: #6b7280;
  }

  @media (max-width: 700px) {
    .table-container {
      padding: 0.3rem;
      max-width: 100vw;
    }
    
    table {
      min-width: 500px;
      font-size: 0.9em;
    }
    
    th, td {
      padding: 0.4em 0.5em;
    }
  }
</style>