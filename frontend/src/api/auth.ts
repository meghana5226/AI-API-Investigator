import { apiClient } from "./client";
import { User } from "./types";

export interface RegisterPayload {
  email: string;
  full_name: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export const authApi = {
  register: (payload: RegisterPayload) => apiClient.post<User>("/auth/register", payload),

  login: (payload: LoginPayload) => {
    const form = new URLSearchParams();
    form.append("username", payload.email);
    form.append("password", payload.password);
    return apiClient.post<TokenResponse>("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },

  me: () => apiClient.get<User>("/users/me"),

  updateMe: (payload: { full_name?: string; dark_mode?: boolean }) =>
    apiClient.patch<User>("/users/me", payload),

  changePassword: (payload: { current_password: string; new_password: string }) =>
    apiClient.post("/users/me/change-password", payload),
};
