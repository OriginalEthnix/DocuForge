import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { AuthTokens } from '@/types';

// Resolve API base URL:
// 1. Check VITE_API_URL or alternative VITE_* backend variables.
// 2. If present, normalize (strip trailing slash, ensure protocol https://, guarantee /api path).
// 3. If absent, fall back to '/api' (proxied by Vite dev server to localhost:8000 during local development).
const rawApiUrl = (
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_BACKEND_URL ||
  import.meta.env.VITE_RENDER_URL ||
  import.meta.env.VITE_SERVER_URL ||
  ''
).trim();

export const BASE_URL: string = (() => {
  if (rawApiUrl) {
    let cleaned = rawApiUrl.replace(/\/+$/, '');
    // Ensure scheme if user entered domain without https://
    if (!cleaned.startsWith('http://') && !cleaned.startsWith('https://')) {
      cleaned = `https://${cleaned}`;
    }
    return cleaned.endsWith('/api') ? cleaned : `${cleaned}/api`;
  }
  return '/api';
})();

if (import.meta.env.PROD && !rawApiUrl && typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
  console.warn(
    '[DocuForge AI] VITE_API_URL is not set in this production build. API requests are falling back to ' +
    BASE_URL +
    ' on ' +
    window.location.origin +
    ', which requires a backend reverse-proxy or deployed API server.'
  );
}

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000, // 2 minutes for AI generation
});

// ─── Request Interceptor — Attach token ───────────────────────────────────────
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ─── Response Interceptor — Handle 401 / token refresh ────────────────────────
let isRefreshing = false;
let failedQueue: Array<{ resolve: (v: any) => void; reject: (e: any) => void }> = [];

function processQueue(error: any, token: string | null = null) {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
  failedQueue = [];
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Do NOT attempt token refresh or page reload for login/register endpoints
    const isAuthEndpoint =
      originalRequest?.url?.includes('/auth/login') ||
      originalRequest?.url?.includes('/auth/register');

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        isRefreshing = false;
        clearTokens();
        window.location.href = '/login';
        return Promise.reject(error);
      }

      try {
        const res = await axios.post<AuthTokens>(`${BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });
        const { access_token, refresh_token } = res.data;
        setTokens(access_token, refresh_token);
        processQueue(null, access_token);
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        clearTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export function setTokens(accessToken: string, refreshToken: string) {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
}

export function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data;

    // 1. Backend returned structured detail from FastAPI
    if (data?.detail) {
      if (typeof data.detail === 'string') return data.detail;
      if (typeof data.detail === 'object' && data.detail !== null) {
        if ('message' in data.detail && typeof (data.detail as any).message === 'string') {
          return (data.detail as any).message;
        }
      }
      if (Array.isArray(data.detail)) {
        return data.detail.map((d: any) => d.msg || (typeof d === 'string' ? d : JSON.stringify(d))).join(', ');
      }
    }
    if (data?.message && typeof data.message === 'string') {
      return data.message;
    }

    // 2. Detect 404 from static host (e.g. Vercel) when API is missing/unreachable
    if (error.response?.status === 404) {
      const isHtmlResponse = typeof data === 'string' && (data.includes('<!DOCTYPE html>') || data.includes('<html'));
      const isVercelError =
        error.response?.headers?.['x-vercel-error'] === 'NOT_FOUND' ||
        (typeof data === 'string' && data.includes('NOT_FOUND'));

      if (isVercelError || isHtmlResponse || !rawApiUrl) {
        return 'Backend API endpoint not found (HTTP 404). Please ensure your FastAPI backend is running and VITE_API_URL is configured in your Vercel project environment variables.';
      }
      return 'The requested API endpoint was not found on the backend (HTTP 404).';
    }

    // 3. Network connection errors / CORS blocks
    if (error.code === 'ERR_NETWORK') {
      return `Cannot connect to backend server (${BASE_URL}). Please verify that the backend is running and CORS allows ${typeof window !== 'undefined' ? window.location.origin : 'this origin'}.`;
    }

    // 4. HTTP status message fallback
    if (error.response?.statusText && error.response.statusText !== 'OK') {
      return `Request failed with status ${error.response.status}: ${error.response.statusText}`;
    }

    return error.message || 'An unexpected error occurred.';
  }
  if (error instanceof Error) return error.message;
  return 'An unexpected error occurred.';
}

export default api;
