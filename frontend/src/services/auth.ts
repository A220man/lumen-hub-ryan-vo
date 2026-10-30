/** Authentication service for Keycloak/OIDC integration. */

import type { User } from "../types";

const AUTH_STORAGE_KEY = "lumen_hub_auth";
const TOKEN_STORAGE_KEY = "lumen_hub_token";

interface AuthConfig {
  keycloak_url: string;
  realm: string;
  client_id: string;
  redirect_uri: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

function getAuthConfig(): Promise<AuthConfig> {
  return fetch("/api/v1/auth/config").then((res) => res.json());
}

function getKeycloakUrls(config: AuthConfig) {
  const baseUrl = `${config.keycloak_url}/realms/${config.realm}/protocol/openid-connect`;
  return {
    auth: `${baseUrl}/auth`,
    token: `${baseUrl}/token`,
    logout: `${baseUrl}/logout`,
    userinfo: `${baseUrl}/userinfo`,
  };
}

export async function initiateLogin(): Promise<void> {
  const config = await getAuthConfig();
  const urls = getKeycloakUrls(config);
  const authUrl = new URL(urls.auth);
  authUrl.searchParams.set("client_id", config.client_id);
  authUrl.searchParams.set("redirect_uri", config.redirect_uri);
  authUrl.searchParams.set("response_type", "code");
  authUrl.searchParams.set("scope", "openid profile email");
  window.location.href = authUrl.toString();
}

export async function exchangeCodeForToken(code: string): Promise<TokenResponse> {
  const config = await getAuthConfig();
  const urls = getKeycloakUrls(config);

  const params = new URLSearchParams({
    grant_type: "authorization_code",
    code,
    redirect_uri: config.redirect_uri,
    client_id: config.client_id,
  });

  const response = await fetch("/api/v1/auth/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: params.toString(),
  });

  if (!response.ok) {
    throw new Error("Failed to exchange code for token");
  }

  return response.json();
}

export async function fetchUserInfo(accessToken: string): Promise<User> {
  const config = await getAuthConfig();
  const urls = getKeycloakUrls(config);

  const response = await fetch(urls.userinfo, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch user info");
  }

  const data = await response.json();
  return {
    id: data.sub,
    email: data.email || data.preferred_username,
    name: data.name,
    roles: data.realm_access?.roles || [],
  };
}

export function saveAuth(token: string, user: User): void {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(user));
}

export function loadAuth(): { token: string | null; user: User | null } {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  const userStr = localStorage.getItem(AUTH_STORAGE_KEY);
  const user = userStr ? JSON.parse(userStr) : null;
  return { token, user };
}

export function clearAuth(): void {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  localStorage.removeItem(AUTH_STORAGE_KEY);
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export async function logout(): Promise<void> {
  const config = await getAuthConfig();
  const urls = getKeycloakUrls(config);
  const token = getToken();

  // Call Keycloak logout endpoint
  if (token) {
    try {
      await fetch("/api/v1/auth/logout", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch {
      // Ignore logout errors
    }
  }

  clearAuth();

  // Redirect to Keycloak logout
  const logoutUrl = new URL(urls.logout);
  logoutUrl.searchParams.set("client_id", config.client_id);
  logoutUrl.searchParams.set("post_logout_redirect_uri", window.location.origin);
  window.location.href = logoutUrl.toString();
}
