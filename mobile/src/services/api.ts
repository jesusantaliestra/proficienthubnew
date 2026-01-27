import axios from 'axios';
import Constants from 'expo-constants';

// API URL - change this for production
const API_BASE_URL = Constants.expoConfig?.extra?.apiUrl || 'https://your-api-url.com/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any request modifications here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - will be caught by AuthContext
    }
    return Promise.reject(error);
  }
);

export default api;