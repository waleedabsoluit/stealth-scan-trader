/**
 * API client for communicating with the STEALTH Bot backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
  
  // Signals
  getSignals: () => apiClient.get('/api/signals'),
  
  // Modules
  getModules: () => apiClient.get('/api/modules'),
  toggleModule: (moduleName: string) => apiClient.post(`/api/modules/${moduleName}/toggle`),
  
  // Configuration
  getConfig: () => apiClient.get('/api/config'),
  updateConfig: (config: any) => apiClient.put('/api/config', config),
  
  // Performance
  getPerformance: () => apiClient.get('/api/performance'),
  
  // Risk
  getRisk: () => apiClient.get('/api/risk'),
  
  // Market Data
  get: (url: string) => apiClient.get(url),
  post: (url: string, data?: any) => apiClient.post(url, data),
};

export default api;