import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post('/users/register/', data),
  login: (data) => api.post('/users/login/', data),
  getProfile: () => api.get('/users/profile/'),
  updateProfile: (data) => api.patch('/users/profile/', data),
  getMyOrders: () => api.get('/users/my-orders/'),
  getMyPayments: () => api.get('/users/my-payments/'),
};

export const productAPI = {
  list: (params) => api.get('/products/', { params }),
  get: (id) => api.get(`/products/${id}/`),
  create: (data) => api.post('/products/', data),
  update: (id, data) => api.patch(`/products/${id}/`, data),
  delete: (id) => api.delete(`/products/${id}/`),
  getCategories: () => api.get('/products/categories/'),
  getCategoryHierarchy: () => api.get('/products/categories/hierarchy/'),
  getRecommendations: (id) => api.get(`/products/${id}/recommendations/`),
};

export const orderAPI = {
  list: () => api.get('/orders/'),
  create: (data) => api.post('/orders/', data),
  get: (id) => api.get(`/orders/${id}/`),
  cancel: (id) => api.post(`/orders/${id}/cancel/`),
  checkout: (id, data) => api.post(`/orders/${id}/checkout/`, data),
};

export const paymentAPI = {
  list: () => api.get('/payments/'),
  get: (id) => api.get(`/payments/${id}/`),
  verify: (id) => api.get(`/payments/${id}/verify/`),
  confirm: (data) => api.post('/payments/confirm/', data),
};

export default api;
