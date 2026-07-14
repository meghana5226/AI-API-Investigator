export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  dark_mode: boolean;
  created_at: string;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  source_type: string;
  source_filename: string;
  status: "pending" | "processing" | "ready" | "failed";
  base_url: string | null;
  auth_type: string | null;
  ai_summary: string | null;
  risk_report: RiskReport | null;
  endpoint_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectListItem {
  id: string;
  name: string;
  source_type: string;
  status: string;
  endpoint_count: number;
  created_at: string;
}

export interface RiskIssue {
  severity: "high" | "medium" | "low";
  endpoint: string;
  issue: string;
}

export interface RiskReport {
  total_issues: number;
  high: number;
  medium: number;
  low: number;
  issues: RiskIssue[];
}

export interface Endpoint {
  id: string;
  project_id: string;
  method: string;
  path: string;
  summary: string | null;
  description: string | null;
  parameters: unknown;
  request_body: unknown;
  responses: unknown;
  tags: string[] | null;
  requires_auth: string | null;
  ai_explanation: string | null;
  sample_curl: string | null;
  sample_python: string | null;
  sample_javascript: string | null;
}

export interface EndpointListItem {
  id: string;
  method: string;
  path: string;
  summary: string | null;
  tags: string[] | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ChatSession {
  id: string;
  project_id: string;
  title: string;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ChatSessionDetail extends ChatSession {
  messages: ChatMessage[];
}

export interface HistoryEntry {
  id: string;
  project_id: string | null;
  action: string;
  description: string;
  extra_data: unknown;
  created_at: string;
}
