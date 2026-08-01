import api from './api';
import { Project, ProjectCreate, DashboardStats } from '@/types';

export const projectService = {
  async list(page = 1, pageSize = 20, status?: string): Promise<{ projects: Project[]; total: number }> {
    const params: any = { page, page_size: pageSize };
    if (status) params.status = status;
    const res = await api.get('/projects', { params });
    return res.data;
  },

  async get(id: number): Promise<Project> {
    const res = await api.get(`/projects/${id}`);
    return res.data;
  },

  async create(data: ProjectCreate): Promise<Project> {
    const res = await api.post('/projects', data);
    return res.data;
  },

  async update(id: number, data: Partial<ProjectCreate>): Promise<Project> {
    const res = await api.put(`/projects/${id}`, data);
    return res.data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/projects/${id}`);
  },

  async getDashboardStats(): Promise<DashboardStats> {
    const res = await api.get('/dashboard/stats');
    return res.data;
  },
};
