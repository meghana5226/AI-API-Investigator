import { apiClient } from "./client";
import { Endpoint, EndpointListItem, PaginatedResponse, Project, ProjectListItem } from "./types";

export const projectsApi = {
  list: (params: { page?: number; page_size?: number; search?: string } = {}) =>
    apiClient.get<PaginatedResponse<ProjectListItem>>("/projects", { params }),

  get: (id: string) => apiClient.get<Project>(`/projects/${id}`),

  upload: (file: File, onProgress?: (pct: number) => void) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post<Project>("/projects/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (evt) => {
        if (onProgress && evt.total) onProgress(Math.round((evt.loaded * 100) / evt.total));
      },
    });
  },

  update: (id: string, payload: { name?: string; description?: string }) =>
    apiClient.patch<Project>(`/projects/${id}`, payload),

  delete: (id: string) => apiClient.delete(`/projects/${id}`),

  analyze: (id: string) => apiClient.post<Project>(`/projects/${id}/analyze`),

  listEndpoints: (id: string, params: { page?: number; page_size?: number; search?: string; method?: string } = {}) =>
    apiClient.get<PaginatedResponse<EndpointListItem>>(`/projects/${id}/endpoints`, { params }),

  getEndpoint: (projectId: string, endpointId: string) =>
    apiClient.get<Endpoint>(`/projects/${projectId}/endpoints/${endpointId}`),

  explainEndpoint: (projectId: string, endpointId: string) =>
    apiClient.post<Endpoint>(`/projects/${projectId}/endpoints/${endpointId}/explain`),

  compare: (projectIdA: string, projectIdB: string) =>
    apiClient.post("/projects/compare", { project_id_a: projectIdA, project_id_b: projectIdB }),

  search: (projectId: string, q: string, topK = 5) =>
    apiClient.get(`/search/${projectId}`, { params: { q, top_k: topK } }),

  exportReport: (id: string, format: "json" | "markdown") =>
    apiClient.get(`/export/${id}`, { params: { format }, responseType: "blob" }),
};
