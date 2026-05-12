/**
 * API Service - Handles all API communications
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle 401 responses
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear tokens and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ==================== AUTH ENDPOINTS ====================

export const authAPI = {
  register: (data) => apiClient.post('/auth/register', data),
  login: (data) => apiClient.post('/auth/login', data),
  refreshToken: (data) => apiClient.post('/auth/refresh-token', data),
  verify: () => apiClient.get('/auth/verify'),
  logout: () => apiClient.post('/auth/logout'),
};

// ==================== TRADE ENDPOINTS ====================

export const tradesAPI = {
  create: (data) => apiClient.post('/trades', data),
  list: (params) => apiClient.get('/trades', { params }),
  getOne: (id) => apiClient.get(`/trades/${id}`),
  update: (id, data) => apiClient.put(`/trades/${id}`, data),
  delete: (id) => apiClient.delete(`/trades/${id}`),
  getStatistics: () => apiClient.get('/trades/statistics/summary'),
};

// ==================== ANALYTICS ENDPOINTS ====================

export const analyticsAPI = {
  getDashboard: () => apiClient.get('/analytics/dashboard'),
  getSummary: () => apiClient.get('/analytics/summary'),
  getMetrics: (params) => apiClient.get('/analytics/metrics', { params }),
  getEquityCurve: () => apiClient.get('/analytics/equity-curve'),
  getDrawdown: () => apiClient.get('/analytics/drawdown'),
  getStrategy: () => apiClient.get('/analytics/strategy'),
  getSession: () => apiClient.get('/analytics/session'),
};

// ==================== ML ENDPOINTS ====================

export const mlAPI = {
  getPredictions: (data) => apiClient.post('/ml/predictions', data),
  getRiskDetection: (data) => apiClient.post('/ml/risk-detection', data),
  getPatternAnalysis: (data) => apiClient.post('/ml/pattern-analysis', data),
  getModelPerformance: () => apiClient.get('/ml/model-performance'),
  retrain: () => apiClient.post('/ml/retrain'),
  getFeatures: () => apiClient.get('/ml/features'),
};

// ==================== JOURNAL ENDPOINTS ====================

export const journalsAPI = {
  create: (data) => apiClient.post('/journals', data),
  list: (params) => apiClient.get('/journals', { params }),
  getSummary: () => apiClient.get('/journals/summary'),
  getOne: (id) => apiClient.get(`/journals/${id}`),
  update: (id, data) => apiClient.put(`/journals/${id}`, data),
  delete: (id) => apiClient.delete(`/journals/${id}`),
  getAnalysis: (id) => apiClient.get(`/journals/${id}/analysis`),
};

export default apiClient;
