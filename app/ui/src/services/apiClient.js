export const API_BASE_URL = import.meta.env.DEV ? 'http://127.0.0.1:8001/api' : '/api';

export const apiClient = {
  login: async (username, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      if (!response.ok) throw new Error('Login failed');
      return await response.json();
    } catch (error) {
      console.error('API Error (login):', error);
      throw error;
    }
  },

  getHealth: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) throw new Error('Health check failed');
      return await response.json();
    } catch (error) {
      console.error('API Error (getHealth):', error);
      throw error;
    }
  },

  getModelInfo: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/model-info`);
      if (!response.ok) throw new Error('Failed to fetch model info');
      return await response.json();
    } catch (error) {
      console.error('API Error (getModelInfo):', error);
      throw error;
    }
  },

  predict: async (features) => {
    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ features }),
      });
      
      // We still want to parse the response even if it's a 4xx/5xx for structured error handling
      // but in this API design, insufficient_history is returned as a 200 OK with status="insufficient_history"
      if (!response.ok && response.status !== 422) {
         throw new Error(`HTTP Error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Error (predict):', error);
      throw error;
    }
  },

  explain: async (features) => {
    try {
      const response = await fetch(`${API_BASE_URL}/explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ features }),
      });
      if (!response.ok && response.status !== 422) {
         throw new Error(`HTTP Error: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API Error (explain):', error);
      throw error;
    }
  },

  getEnergyDrivers: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/energy-drivers`);
      if (!response.ok) throw new Error('Failed to fetch energy drivers');
      return await response.json();
    } catch (error) {
      console.error('API Error (getEnergyDrivers):', error);
      throw error;
    }
  },

  getRecommendations: async (features) => {
    try {
      const response = await fetch(`${API_BASE_URL}/recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ features }),
      });
      if (!response.ok && response.status !== 422) {
         throw new Error(`HTTP Error: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API Error (getRecommendations):', error);
      throw error;
    }
  },

  getBuildings: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/buildings`);
      if (!response.ok) throw new Error('Failed to fetch buildings');
      return await response.json();
    } catch (error) {
      console.error('API Error (getBuildings):', error);
      throw error;
    }
  },

  getReports: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/reports`);
      if (!response.ok) throw new Error('Failed to fetch reports');
      return await response.json();
    } catch (error) {
      console.error('API Error (getReports):', error);
      throw error;
    }
  }
};
