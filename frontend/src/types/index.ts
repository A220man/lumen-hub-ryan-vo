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