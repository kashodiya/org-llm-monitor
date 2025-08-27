



import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Health check
  healthCheck: () => api.get('/api/health'),

  // Websites
  getWebsites: (activeOnly = true) => api.get(`/api/websites?active_only=${activeOnly}`),
  createWebsite: (websiteData) => api.post('/api/websites', websiteData),
  deleteWebsite: (websiteId) => api.delete(`/api/websites/${websiteId}`),

  // Monitoring
  startMonitoring: (data = {}) => api.post('/api/monitoring/start', data),
  getMonitoringStatus: () => api.get('/api/monitoring/status'),
  setupScheduledMonitoring: (intervalHours = 6) => 
    api.post(`/api/monitoring/schedule?interval_hours=${intervalHours}`),
  stopScheduledMonitoring: () => api.post('/api/monitoring/stop'),

  // Analysis Results
  getAnalysisResults: (limit = 50) => api.get(`/api/analysis/results?limit=${limit}`),
  getMisrepresentationsSummary: () => api.get('/api/analysis/summary'),

  // Questions
  createQuestion: (questionData) => api.post('/api/questions', questionData),
  getQuestionsForWebsite: (websiteId) => api.get(`/api/questions/${websiteId}`),

  // Dashboard
  getDashboardStats: () => api.get('/api/dashboard/stats'),
};

export default api;




