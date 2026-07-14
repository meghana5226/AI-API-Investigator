import { apiClient } from "./client";
import { HistoryEntry, PaginatedResponse } from "./types";

export const historyApi = {
  list: (params: { page?: number; page_size?: number; search?: string } = {}) =>
    apiClient.get<PaginatedResponse<HistoryEntry>>("/history", { params }),
};
