import type { DocumentReview, ProjectDetail, ProjectSummary } from './types'

const API_BASE = import.meta.env.VITE_API_URL ?? '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new Error(payload?.detail ?? `Richiesta non riuscita (${response.status})`)
  }

  return response.json() as Promise<T>
}

export const api = {
  projects: (signal?: AbortSignal) =>
    request<ProjectSummary[]>('/projects', { signal }),
  project: (projectId: string, signal?: AbortSignal) =>
    request<ProjectDetail>(`/projects/${projectId}`, { signal }),
  createProject: (payload: { title: string; description: string }) =>
    request<ProjectDetail>('/projects', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  documentReview: (projectId: string, signal?: AbortSignal) =>
    request<DocumentReview>(`/projects/${projectId}/document-review`, { signal }),
}
