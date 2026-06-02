import axios from 'axios'

// Resolve the API base URL.
// - In development the Vite dev server proxies `/api/*` to the backend
//   (stripping the `/api` prefix), so a relative base works.
// - In a production build (e.g. GitHub Pages) there is no proxy, so point
//   directly at the deployed backend via the build-time VITE_API_URL.
const baseURL =
  import.meta.env.PROD && import.meta.env.VITE_API_URL
    ? import.meta.env.VITE_API_URL
    : '/api'

// Create axios instance with base configuration
export const apiClient = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add any request modifications here
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Handle unauthorized
      console.error('Unauthorized access')
    } else if (error.response?.status >= 500) {
      // Handle server errors
      console.error('Server error:', error.response?.data)
    }
    
    return Promise.reject(error)
  }
)

// API endpoints
export const api = {
  // Health check
  health: () => apiClient.get('/health'),

  // Simulation control
  initializeSimulation: (config: any) => apiClient.post('/simulation/initialize', config),
  controlSimulation: (action: string) => apiClient.post('/simulation/control', { action }),
  getSimulationStatus: () => apiClient.get('/simulation/status'),

  // Data access
  getAgents: (agentId?: string) => 
    agentId ? apiClient.get(`/agents/${agentId}`) : apiClient.get('/agents'),
  getCulturalData: () => apiClient.get('/culture'),
  getEconomicData: () => apiClient.get('/economy'),
  getNetworkData: () => apiClient.get('/network'),
  getWorldSummary: () => apiClient.get('/world'),

  // Real-time data
  getRealtimeStatus: () => apiClient.get('/realtime/status'),
  getRealtimeNetwork: () => apiClient.get('/realtime/network'),
  getRealtimeEconomy: () => apiClient.get('/realtime/economy'),
  getRealtimeCulture: () => apiClient.get('/realtime/culture'),

  // Snapshots
  takeSnapshot: (name?: string) => apiClient.post('/snapshots', { name }),
  listSnapshots: () => apiClient.get('/snapshots'),
  loadSnapshot: (snapshotFile: string) => apiClient.post('/snapshots/load', snapshotFile),

  // Statistics
  getPerformanceStats: () => apiClient.get('/stats/performance'),
  getSimulationHistory: () => apiClient.get('/stats/history'),

  // Utility
  getConfig: () => apiClient.get('/config'),
  resetSimulation: () => apiClient.post('/reset'),
}

export default apiClient
