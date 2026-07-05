import axios, { type AxiosInstance } from 'axios';
import { useTenantStore } from '@/stores/tenant';

export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const tenant = useTenantStore();
  if (tenant.id) {
    config.headers['X-Tenant-ID'] = tenant.id;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);
