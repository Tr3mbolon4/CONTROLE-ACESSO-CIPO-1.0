import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

// Helper function to extract error message from API response
export const getErrorMessage = (error, defaultMsg = 'Erro desconhecido') => {
  const detail = error?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map(d => d.msg || d.message || d).join(', ');
  if (detail && typeof detail === 'object') return detail.msg || detail.message || defaultMsg;
  return error?.message || defaultMsg;
};

const api = axios.create({
  baseURL: `${API}/api`,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        await axios.post(`${API}/api/auth/refresh`, {}, { withCredentials: true });
        return api(originalRequest);
      } catch (refreshError) {
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
  refresh: () => api.post('/auth/refresh'),
};

// Users
export const usersAPI = {
  list: () => api.get('/users'),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
};

// Visitors
export const visitorsAPI = {
  list: (params) => api.get('/visitors', { params }),
  get: (id) => api.get(`/visitors/${id}`),
  create: (data) => api.post('/visitors', data),
  update: (id, data) => api.put(`/visitors/${id}`, data),
  delete: (id) => api.delete(`/visitors/${id}`),
};

// Fleet
export const fleetAPI = {
  list: (params) => api.get('/fleet', { params }),
  get: (id) => api.get(`/fleet/${id}`),
  create: (data) => api.post('/fleet', data),
  return: (id, data) => api.post(`/fleet/${id}/return`, data),
  delete: (id) => api.delete(`/fleet/${id}`),
  uploadPhoto: (id, formData, params) => api.post(`/fleet/${id}/photos`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    params,
  }),
  getPhotoUrl: (fleetId, photoId) => `${API}/api/fleet/${fleetId}/photos/${photoId}`,
};

// Employees
export const employeesAPI = {
  list: (params) => api.get('/employees', { params }),
  get: (id) => api.get(`/employees/${id}`),
  create: (data) => api.post('/employees', data),
  update: (id, data) => api.put(`/employees/${id}`, data),
  delete: (id) => api.delete(`/employees/${id}`),
};

// Directors
export const directorsAPI = {
  list: (params) => api.get('/directors', { params }),
  get: (id) => api.get(`/directors/${id}`),
  create: (data) => api.post('/directors', data),
  update: (id, data) => api.put(`/directors/${id}`, data),
  delete: (id) => api.delete(`/directors/${id}`),
};

// Carregamentos
export const carregamentosAPI = {
  list: (params) => api.get('/carregamentos', { params }),
  get: (id) => api.get(`/carregamentos/${id}`),
  create: (data) => api.post('/carregamentos', data),
  update: (id, data) => api.put(`/carregamentos/${id}`, data),
  delete: (id) => api.delete(`/carregamentos/${id}`),
  uploadPhoto: (id, formData, params) => api.post(`/carregamentos/${id}/photos`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    params,
  }),
  getPhotoUrl: (carregamentoId, photoId) => `${API}/api/carregamentos/${carregamentoId}/photos/${photoId}`,
};

// Agendamentos
export const agendamentosAPI = {
  list: (params) => api.get('/agendamentos', { params }),
  listHoje: () => api.get('/agendamentos/hoje'),
  get: (id) => api.get(`/agendamentos/${id}`),
  create: (data) => api.post('/agendamentos', data),
  update: (id, data) => api.put(`/agendamentos/${id}`, data),
  delete: (id) => api.delete(`/agendamentos/${id}`),
  darEntrada: (id) => api.post(`/agendamentos/${id}/dar-entrada`),
};

// Dashboard
export const dashboardAPI = {
  get: () => api.get('/dashboard'),
};

// History
export const historyAPI = {
  list: (params) => api.get('/history', { params }),
};

// Reports
export const reportsAPI = {
  visitors: (params) => api.get('/reports/visitors', { params }),
  fleet: (params) => api.get('/reports/fleet', { params }),
  employees: (params) => api.get('/reports/employees', { params }),
  directors: (params) => api.get('/reports/directors', { params }),
  carregamentos: (params) => api.get('/reports/carregamentos', { params }),
};

export default api;
