import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use(async (config) => {
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
}, async (error) => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(`${API_BASE_URL}/refresh`, {}, {
            headers: {
                'Authorization': `Bearer ${refreshToken}`
            }
        });
        if (response.status === 200) {
            localStorage.setItem('token', response.data.access_token);
            axios.defaults.headers.common['Authorization'] = 'Bearer ' + response.data.access_token;
            return api(originalRequest);
        }
    }
    return Promise.reject(error);
});

export const getJobs = () => api.get('/jobs');
export const searchJobs = (query) => api.get(`/jobs/search`, { params: { query } });
export const scrapeJobs = () => api.post('/scrape');

export default api;
