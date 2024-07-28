import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const getJobs = () => api.get('/jobs');
export const searchJobs = (query) => api.get(`/jobs/search`, { params: { query } });
export const scrapeJobs = () => api.post('/scrape');