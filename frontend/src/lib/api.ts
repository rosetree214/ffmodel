import type { Player, SimulationResponse, SimulationRequest, ApiError } from './types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class ApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_URL}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData: ApiError = await response.json().catch(() => ({
          error: 'Request failed',
          detail: `HTTP ${response.status}: ${response.statusText}`,
        }));
        throw new Error(errorData.detail || errorData.error || 'Unknown API error');
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error or invalid response');
    }
  }

  async getPlayers(): Promise<Player[]> {
    return this.request<Player[]>('/players');
  }

  async getPlayer(playerId: string): Promise<Player> {
    return this.request<Player>(`/players/${playerId}`);
  }

  async simulateDraft(request: SimulationRequest = {}): Promise<SimulationResponse> {
    return this.request<SimulationResponse>('/simulate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.request<{ status: string; service: string }>('/health');
  }
}

export const api = new ApiService();
export default api;