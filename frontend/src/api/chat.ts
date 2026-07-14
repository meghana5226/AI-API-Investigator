import { apiClient, tokenStorage, API_BASE_URL } from "./client";
import { ChatSession, ChatSessionDetail } from "./types";

export const chatApi = {
  listSessions: () => apiClient.get<ChatSession[]>("/chat/sessions"),

  createSession: (projectId: string, title?: string) =>
    apiClient.post<ChatSession>("/chat/sessions", { project_id: projectId, title }),

  getSession: (id: string) => apiClient.get<ChatSessionDetail>(`/chat/sessions/${id}`),

  deleteSession: (id: string) => apiClient.delete(`/chat/sessions/${id}`),

  sendMessage: (sessionId: string, message: string) =>
    apiClient.post<ChatSessionDetail>(`/chat/sessions/${sessionId}/messages`, { message }),

  /** Streams the assistant's reply token-by-token via fetch + ReadableStream
   * (native EventSource can't send auth headers, so we use fetch directly). */
  streamMessage: async (
    sessionId: string,
    message: string,
    onToken: (token: string) => void
  ): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${tokenStorage.getAccess()}`,
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok || !response.body) {
      throw new Error("Failed to reach the AI chat service");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    // eslint-disable-next-line no-constant-condition
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      onToken(decoder.decode(value, { stream: true }));
    }
  },
};
