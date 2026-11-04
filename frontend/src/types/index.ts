/** Frontend type definitions. */

export interface HealthResponse {
  status: "healthy" | "unhealthy";
  service: string;
  version: string;
  environment: string;
}

export interface ReadinessResponse {
  status: "ready" | "not_ready";
  checks: Record<string, "pending" | "pass" | "fail">;
}

export interface LivenessResponse {
  status: "alive";
}

export interface User {
  id: string;
  email: string;
  name?: string;
  roles: string[];
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface SMSTemplate {
  name: string;
  content: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface SMSTemplateCreate {
  name: string;
  content: string;
  description?: string;
}

export interface SMSTemplateUpdate {
  content?: string;
  description?: string;
}

export interface SMSTemplateValidation {
  valid: boolean;
  errors: string[];
  warnings: string[];
  is_webotp_compatible: boolean;
}

export interface SMSTemplatePreview {
  rendered: string;
  is_webotp_compatible: boolean;
  character_count: number;
  segment_count: number;
}

export interface SMSTemplatePreviewRequest {
  content: string;
  variables: Record<string, string>;
}