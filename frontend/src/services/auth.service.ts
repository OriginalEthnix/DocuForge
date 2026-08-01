import api, { setTokens, clearTokens, getErrorMessage } from './api';
import { User, AuthTokens } from '@/types';

export const authService = {
  async register(data: {
    email: string;
    full_name: string;
    password: string;
    organization?: string;
  }): Promise<AuthTokens> {
    const res = await api.post<AuthTokens>('/auth/register', data);
    const tokens = res.data;
    setTokens(tokens.access_token, tokens.refresh_token);
    localStorage.setItem('user', JSON.stringify(tokens.user));
    return tokens;
  },

  async login(email: string, password: string): Promise<AuthTokens> {
    const res = await api.post<AuthTokens>('/auth/login', { email, password });
    const tokens = res.data;
    setTokens(tokens.access_token, tokens.refresh_token);
    localStorage.setItem('user', JSON.stringify(tokens.user));
    return tokens;
  },

  async getMe(): Promise<User> {
    const res = await api.get<User>('/auth/me');
    localStorage.setItem('user', JSON.stringify(res.data));
    return res.data;
  },

  logout() {
    clearTokens();
  },

  getStoredUser(): User | null {
    const stored = localStorage.getItem('user');
    if (!stored) return null;
    try {
      return JSON.parse(stored) as User;
    } catch {
      return null;
    }
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },
};
