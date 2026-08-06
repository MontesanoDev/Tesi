import type {
  CallFactsExtractionResult,
  CallFactsReview,
  CallFactRevision,
  ConversationDetail,
  DocumentReview,
  DraftGenerationResult,
  EvidenceSearch,
  GroundedAnswer,
  GlobalKnowledgeDocument,
  GlobalKnowledgeOverview,
  KnowledgeArtifactDetail,
  KnowledgeArtifactSummary,
  ProjectDetail,
  ProjectFile,
  ProjectGlobalKnowledgeDocument,
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

  if (response.status === 204) return undefined as T

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
  globalKnowledge: (signal?: AbortSignal) =>
    request<GlobalKnowledgeOverview>('/global-knowledge', { signal }),
  uploadGlobalKnowledgeFile: (file: File, category: 'general' | 'company') => {
    const body = new FormData()
    body.append('file', file)
    body.append('category', category)
    return request<GlobalKnowledgeDocument>('/global-knowledge/files', {
      method: 'POST',
      body,
    })
  },
  deleteGlobalKnowledgeFile: (documentId: number) =>
    request<void>(`/global-knowledge/files/${documentId}`, { method: 'DELETE' }),
  companyFacts: (signal?: AbortSignal) =>
    request<KnowledgeArtifactDetail>('/global-knowledge/company-facts', { signal }),
  updateCompanyFacts: (content: string) =>
    request<KnowledgeArtifactDetail>('/global-knowledge/company-facts', {
      method: 'PUT',
      body: JSON.stringify({ content }),
    }),
  projectGlobalKnowledge: (projectId: string, signal?: AbortSignal) =>
    request<ProjectGlobalKnowledgeDocument[]>(
      `/projects/${projectId}/global-knowledge`,
      { signal },
    ),
  updateProjectGlobalKnowledge: (projectId: string, documentId: number, linked: boolean) =>
    request<ProjectGlobalKnowledgeDocument>(
      `/projects/${projectId}/global-knowledge/${documentId}`,
      { method: 'PUT', body: JSON.stringify({ linked }) },
    ),
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
  extractCallFacts: (projectId: string) =>
    request<CallFactsExtractionResult>(`/projects/${projectId}/call-facts/extract`, {
      method: 'POST',
    }),
  callFactsReview: (projectId: string, signal?: AbortSignal) =>
    request<CallFactsReview>(`/projects/${projectId}/call-facts`, { signal }),
  reviseCallFact: (projectId: string, factId: string, payload: CallFactRevision) =>
    request<CallFactsReview>(
      `/projects/${projectId}/call-facts/${encodeURIComponent(factId)}`,
      {
        method: 'PATCH',
        body: JSON.stringify(payload),
      },
    ),
  generateDraft: (projectId: string) =>
    request<DraftGenerationResult>(`/projects/${projectId}/draft/generate`, {
      method: 'POST',
    }),
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
