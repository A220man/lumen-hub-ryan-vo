/** SMS OTP template management service. */

import type {
  SMSTemplate,
  SMSTemplateCreate,
  SMSTemplateUpdate,
  SMSTemplateValidation,
  SMSTemplatePreview,
  SMSTemplatePreviewRequest,
} from "../types";

// Re-export types for convenience
export type {
  SMSTemplate,
  SMSTemplateCreate,
  SMSTemplateUpdate,
  SMSTemplateValidation,
  SMSTemplatePreview,
  SMSTemplatePreviewRequest,
};

const API_BASE = "/api/v1/sms-templates";

async function getAuthHeaders(): Promise<HeadersInit> {
  const token = localStorage.getItem("lumen_hub_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export async function listTemplates(): Promise<SMSTemplate[]> {
  const response = await fetch(API_BASE, {
    method: "GET",
    headers: await getAuthHeaders(),
  });
  return handleResponse<SMSTemplate[]>(response);
}

export async function createTemplate(data: SMSTemplateCreate): Promise<SMSTemplate> {
  const response = await fetch(API_BASE, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<SMSTemplate>(response);
}

export async function getTemplate(name: string): Promise<SMSTemplate> {
  const response = await fetch(`${API_BASE}/${encodeURIComponent(name)}`, {
    method: "GET",
    headers: await getAuthHeaders(),
  });
  return handleResponse<SMSTemplate>(response);
}

export async function updateTemplate(name: string, data: SMSTemplateUpdate): Promise<SMSTemplate> {
  const response = await fetch(`${API_BASE}/${encodeURIComponent(name)}`, {
    method: "PUT",
    headers: await getAuthHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<SMSTemplate>(response);
}

export async function deleteTemplate(name: string): Promise<void> {
  const response = await fetch(`${API_BASE}/${encodeURIComponent(name)}`, {
    method: "DELETE",
    headers: await getAuthHeaders(),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
}

export async function validateTemplate(data: SMSTemplateCreate): Promise<SMSTemplateValidation> {
  const response = await fetch(`${API_BASE}/validate`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<SMSTemplateValidation>(response);
}

export async function previewTemplate(data: SMSTemplatePreviewRequest): Promise<SMSTemplatePreview> {
  const response = await fetch(`${API_BASE}/preview`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse<SMSTemplatePreview>(response);
}
