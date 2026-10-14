import api from './api';

export const generationService = {
  // Requirements
  async generateRequirements(projectId: number) {
    const res = await api.post(`/projects/${projectId}/requirements/generate`);
    return res.data;
  },
  async getRequirements(projectId: number) {
    const res = await api.get(`/projects/${projectId}/requirements`);
    return res.data;
  },

  // User Stories
  async generateUserStories(projectId: number) {
    const res = await api.post(`/projects/${projectId}/user-stories/generate`);
    return res.data;
  },
  async getUserStories(projectId: number) {
    const res = await api.get(`/projects/${projectId}/user-stories`);
    return res.data;
  },

  // SRS
  async generateSRS(projectId: number) {
    const res = await api.post(`/projects/${projectId}/srs/generate`);
    return res.data;
  },
  async getSRS(projectId: number) {
    const res = await api.get(`/projects/${projectId}/srs`);
    return res.data;
  },

  // UML Diagrams
  async generateUML(projectId: number) {
    const res = await api.post(`/projects/${projectId}/diagrams/uml/generate`);
    return res.data;
  },
  async generateDFD(projectId: number) {
    const res = await api.post(`/projects/${projectId}/diagrams/dfd/generate`);
    return res.data;
  },
  async getDiagrams(projectId: number, category?: string) {
    const params = category ? { category } : {};
    const res = await api.get(`/projects/${projectId}/diagrams`, { params });
    return res.data;
  },

  // Database Design
  async generateDatabase(projectId: number) {
    const res = await api.post(`/projects/${projectId}/database/generate`);
    return res.data;
  },
  async getDatabase(projectId: number) {
    const res = await api.get(`/projects/${projectId}/database`);
    return res.data;
  },

  // Planning
  async generatePlanning(projectId: number) {
    const res = await api.post(`/projects/${projectId}/planning/generate`);
    return res.data;
  },
  async getPlanning(projectId: number) {
    const res = await api.get(`/projects/${projectId}/planning`);
    return res.data;
  },

  // Estimation
  async generateEstimation(projectId: number) {
    const res = await api.post(`/projects/${projectId}/estimation/generate`);
    return res.data;
  },
  async getEstimation(projectId: number) {
    const res = await api.get(`/projects/${projectId}/estimation`);
    return res.data;
  },

  // Risks
  async generateRisks(projectId: number) {
    const res = await api.post(`/projects/${projectId}/risks/generate`);
    return res.data;
  },
  async getRisks(projectId: number) {
    const res = await api.get(`/projects/${projectId}/risks`);
    return res.data;
  },

  // Test Cases
  async generateTestCases(projectId: number) {
    const res = await api.post(`/projects/${projectId}/tests/generate`);
    return res.data;
  },
  async getTestCases(projectId: number) {
    const res = await api.get(`/projects/${projectId}/tests`);
    return res.data;
  },

  // Traceability
  async generateTraceability(projectId: number) {
    const res = await api.post(`/projects/${projectId}/traceability/generate`);
    return res.data;
  },
  async getTraceability(projectId: number) {
    const res = await api.get(`/projects/${projectId}/traceability`);
    return res.data;
  },

  // Metrics
  async generateMetrics(projectId: number) {
    const res = await api.post(`/projects/${projectId}/metrics/generate`);
    return res.data;
  },
  async getMetrics(projectId: number) {
    const res = await api.get(`/projects/${projectId}/metrics`);
    return res.data;
  },

  // Maintenance
  async generateMaintenance(projectId: number) {
    const res = await api.post(`/projects/${projectId}/maintenance/generate`);
    return res.data;
  },
  async getMaintenance(projectId: number) {
    const res = await api.get(`/projects/${projectId}/maintenance`);
    return res.data;
  },

// PDF Export
  async exportPDF(projectId: number): Promise<{
    message: string;
    file_id: number;
    filename: string;
    download_url: string;
    expires_in_seconds: number;
  }> {
    const res = await api.get(`/projects/${projectId}/export/pdf`);
    return res.data;
  },

  // Upload a file to S3 through the authenticated backend
  async uploadFile(projectId: number, file: File): Promise<{
    id: number;
    filename: string;
    content_type: string;
    size_bytes: number;
    download_url: string;
    expires_in_seconds: number;
  }> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await api.post(
      `/projects/${projectId}/files`,
      formData,
      {
        headers: { 'Content-Type': undefined },
        timeout: 120000,
      }
    );

    return res.data;
  },

  // Get a fresh S3 download link for a previously uploaded file
  async getFileDownload(projectId: number, fileId: number): Promise<{
    id: number;
    filename: string;
    download_url: string;
    expires_in_seconds: number;
  }> {
    const res = await api.get(
      `/projects/${projectId}/files/${fileId}/download`
    );
    return res.data;
  },

  // Document Management & S3 Artifacts
  async listDocuments(projectId: number) {
    const res = await api.get(`/projects/${projectId}/documents`);
    return res.data;
  },
  async getDocument(projectId: number, documentId: string) {
    const res = await api.get(`/projects/${projectId}/documents/${documentId}`);
    return res.data;
  },
  async updateDocument(projectId: number, documentId: string, content: any) {
    const res = await api.put(`/projects/${projectId}/documents/${documentId}`, { content });
    return res.data;
  },
  async regenerateDocument(projectId: number, documentId: string) {
    const res = await api.post(`/projects/${projectId}/documents/${documentId}/regenerate`);
    return res.data;
  },
  async downloadDocument(projectId: number, documentId: string): Promise<{
    document_id: string;
    filename: string;
    download_url: string;
    expires_in_seconds: number;
  }> {
    const res = await api.get(`/projects/${projectId}/documents/${documentId}/download`);
    return res.data;
  },
};

export function downloadFileFromUrl(url: string, filename: string) {
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.rel = 'noopener noreferrer';
  document.body.appendChild(a);
  a.click();
  a.remove();
};

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
