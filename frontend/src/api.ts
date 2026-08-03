import type {
  ConversationDetail,
  DocumentReview,
  EvidenceSearch,
  GroundedAnswer,
  KnowledgeArtifactDetail,
  KnowledgeArtifactSummary,
  ProjectDetail,
  ProjectFile,
  ProjectSummary,
} from './types'

const API_BASE = import.meta.env.VITE_API_URL ?? '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers)
  if (init?.body && !(init.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
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
  uploadProjectFile: (projectId: string, file: File) => {
    const body = new FormData()
    body.append('file', file)
    return request<ProjectFile>(`/projects/${projectId}/files`, {
      method: 'POST',
      body,
    })
  },
  projectArtifacts: (projectId: string, signal?: AbortSignal) =>
    request<KnowledgeArtifactSummary[]>(`/projects/${projectId}/artifacts`, { signal }),
  projectArtifact: (projectId: string, artifactId: string, signal?: AbortSignal) =>
    request<KnowledgeArtifactDetail>(
      `/projects/${projectId}/artifacts/${encodeURIComponent(artifactId)}`,
      { signal },
    ),
  updateProjectArtifact: (projectId: string, artifactId: string, content: string) =>
    request<KnowledgeArtifactDetail>(
      `/projects/${projectId}/artifacts/${encodeURIComponent(artifactId)}`,
      {
        method: 'PUT',
        body: JSON.stringify({ content }),
      },
    ),
  projectEvidence: (projectId: string, query: string, signal?: AbortSignal) => {
    const params = new URLSearchParams({ q: query })
    return request<EvidenceSearch>(`/projects/${projectId}/evidence?${params}`, {
      signal,
    })
  },
  conversation: (projectId: string, conversationId: string, signal?: AbortSignal) =>
    request<ConversationDetail>(
      `/projects/${projectId}/conversations/${conversationId}`,
      { signal },
    ),
  projectAnswer: (projectId: string, question: string, conversationId?: string | null) =>
    request<GroundedAnswer>(`/projects/${projectId}/answer`, {
      method: 'POST',
      body: JSON.stringify({ question, conversation_id: conversationId ?? null }),
    }),
  documentReview: (projectId: string, signal?: AbortSignal) =>
    request<DocumentReview>(`/projects/${projectId}/document-review`, { signal }),
}
