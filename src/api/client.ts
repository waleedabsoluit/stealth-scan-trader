/**
 * API client for communicating with the STEALTH Bot backend
 */
import axios from 'axios';

// Use relative URL for same-origin requests in production
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

/**
 * API endpoints
 */
export const api = {
  // Health check
  health: () => apiClient.get('/health'),
  
  // Bot Control
  bot: {
    getStatus: () => apiClient.get('/api/bot/status'),
    toggleAutoTrade: () => apiClient.post('/api/bot/autotrade/toggle'),
    toggleScanning: () => apiClient.post('/api/bot/scanning/toggle'),
    scanOnce: () => apiClient.post('/api/bot/scan-once'),
    reset: () => apiClient.post('/api/bot/reset'),
  },
  
  // Signals
  getSignals: () => apiClient.get('/api/signals'),
  executeSignal: (signalId: string) => apiClient.post(`/api/signals/${signalId}/execute`),
  
  // Modules
  getModules: () => apiClient.get('/api/modules'),
  toggleModule: (moduleName: string) => apiClient.post(`/api/modules/${moduleName}/toggle`),
  getModuleDetails: (moduleName: string) => apiClient.get(`/api/modules/${moduleName}`),
  configureModule: (moduleName: string, config: any) => apiClient.post(`/api/modules/${moduleName}/configure`, config),
  restartModules: () => apiClient.post('/api/modules/restart'),
  
  // Configuration
  getConfig: () => apiClient.get('/api/config'),
  updateConfig: (config: any) => apiClient.put('/api/config', config),
  
  // Performance
  getPerformance: () => apiClient.get('/api/performance'),
  
  // Risk
  getRisk: () => apiClient.get('/api/risk'),
  updateRiskSettings: (settings: any) => apiClient.post('/api/risk/settings', settings),
  
  // Market Data
  getMarketQuotes: (symbols: string[]) => apiClient.post('/api/market/quotes', symbols),
  getMarketStatus: () => apiClient.get('/api/market/status'),
  
  // Generic
  get: (url: string) => apiClient.get(url),
  post: (url: string, data?: any) => apiClient.post(url, data),
  put: (url: string, data?: any) => apiClient.put(url, data),
  delete: (url: string) => apiClient.delete(url),
};

export default api;