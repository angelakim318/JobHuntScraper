import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

api.interceptors.response.use((response) => {
  return response;
}, (error) => {
  return Promise.reject(error);
});

export const getJobs = () => api.get('/jobs');
export const searchJobs = (query) => api.get(`/jobs/search`, { params: { query } });
export const scrapeJobs = (source) => api.post(`/scrape/${source}`);
export const clearDatabase = () => api.post('/clear_database');

export const login = (username, password) => api.post('/login', { username, password });
export const register = (first_name, username, password) => api.post('/register', { first_name, username, password });

export default api;
