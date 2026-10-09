import type {
  CompilationSession,
  CompilationSessionSummary,
  CompilationFieldInput,
  RetrievalInput,
  RetrievalSettings,
  VectorIndexResult,
  AiLoginFlow,
  AiProfile,
  AiProfileInput,
  AiSettings,
  ProjectAiSelection,
  ConversationDetail,
  CompilationDownload,
  DocumentReview,
  GroundedAnswer,
  GlobalKnowledgeDocument,
  GlobalKnowledgeDocumentContent,
  GlobalKnowledgeOverview,
  ProjectDetail,
  ProjectFile,
  ProjectFileContent,
  ProjectSummary,
} from './types'

const API_BASE = import.meta.env.VITE_API_URL ?? '/api'

function errorDetailMessage(detail: unknown): string | null {
  if (typeof detail === 'string') return detail.trim() || null

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === 'string') return item.trim()
        if (!item || typeof item !== 'object') return ''

        const entry = item as Record<string, unknown>
        const message = typeof entry.msg === 'string'
          ? entry.msg
          : typeof entry.message === 'string'
            ? entry.message
            : ''
        const location = Array.isArray(entry.loc)
          ? entry.loc.filter((part) => part !== 'body').join('.')
          : ''
        return location && message ? `${location}: ${message}` : message
      })
      .filter(Boolean)
    return messages.length > 0 ? messages.join('; ') : null
  }

  if (detail && typeof detail === 'object') {
    const entry = detail as Record<string, unknown>
    if (Array.isArray(entry.errors)) return errorDetailMessage(entry.errors)
    for (const key of ['message', 'msg', 'error']) {
      if (typeof entry[key] === 'string' && entry[key].trim()) return entry[key].trim()
    }
  }

  return null
}

async function requestResponse(path: string, init?: RequestInit): Promise<Response> {
  const headers = new Headers(init?.headers)
  if (init?.body && !(init.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  })

  if (!response.ok) {
    const payload: unknown = await response.json().catch(() => null)
    const detail = payload && typeof payload === 'object' && 'detail' in payload
      ? (payload as { detail: unknown }).detail
      : null
    throw new Error(
      errorDetailMessage(detail) ?? `Richiesta non riuscita (${response.status})`,
    )
  }

  return response
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await requestResponse(path, init)
  if (response.status === 204) return undefined as T

  return response.json() as Promise<T>
}

export const api = {
  retrievalSettings: (signal?: AbortSignal) =>
    request<RetrievalSettings>('/settings/retrieval', { signal }),
  saveRetrievalSettings: (payload: RetrievalInput) =>
    request<RetrievalSettings>('/settings/retrieval', {
      method: 'PUT', body: JSON.stringify(payload),
    }),
  checkRetrievalConnection: (payload: RetrievalInput) =>
    request<{ message: string; dimensions: number }>('/settings/retrieval/check', {
      method: 'POST', body: JSON.stringify(payload),
    }),
  updateVectorIndex: () =>
    request<VectorIndexResult>('/settings/retrieval/index', { method: 'POST' }),
  aiSettings: (signal?: AbortSignal) => request<AiSettings>('/settings/ai', { signal }),
  beginOpenRouterLogin: () => request<AiLoginFlow>('/settings/ai/openrouter/login', { method: 'POST' }),
  completeOpenRouterLogin: (connection_token: string, code: string) =>
    request<{ message: string }>('/settings/ai/openrouter/login/complete', {
      method: 'POST', body: JSON.stringify({ connection_token, code }),
    }),
  saveAiProfile: (payload: AiProfileInput, id?: string) =>
    request<AiProfile>(`/settings/ai/profiles${id ? `/${encodeURIComponent(id)}` : ''}`, {
      method: id ? 'PUT' : 'POST', body: JSON.stringify(payload),
    }),
  deleteAiProfile: (id: string) =>
    request<void>(`/settings/ai/profiles/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  setDefaultAiProfile: (profileId: string | null) =>
    request<AiSettings>('/settings/ai/default', {
      method: 'PUT', body: JSON.stringify({ profile_id: profileId }),
    }),
  checkAiConnection: (payload: AiProfileInput & { profile_id?: string }) =>
    request<{ models: string[]; message: string }>('/settings/ai/check', {
      method: 'POST', body: JSON.stringify(payload),
    }),
  projectAiModel: (projectId: string, signal?: AbortSignal) =>
    request<ProjectAiSelection>(`/projects/${projectId}/ai-model`, { signal }),
  setProjectAiModel: (projectId: string, profileId: string | null, thinking?: boolean) =>
    request<ProjectAiSelection>(`/projects/${projectId}/ai-model`, {
      method: 'PUT',
      body: JSON.stringify({
        profile_id: profileId,
        ...(thinking === undefined ? {} : { thinking }),
      }),
    }),
  projects: (signal?: AbortSignal) =>
    request<ProjectSummary[]>('/projects', { signal }),
  project: (projectId: string, signal?: AbortSignal) =>
    request<ProjectDetail>(`/projects/${projectId}`, { signal }),
  createProject: (payload: { title: string; description: string }) =>
    request<ProjectDetail>('/projects', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  updateProject: (projectId: string, payload: { title: string }) =>
    request<ProjectDetail>(`/projects/${projectId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
  deleteProject: (projectId: string) =>
    request<void>(`/projects/${projectId}`, { method: 'DELETE' }),
  uploadProjectFile: (projectId: string, file: File) => {
    const body = new FormData()
    body.append('file', file)
    return request<ProjectFile>(`/projects/${projectId}/files`, {
      method: 'POST',
      body,
    })
  },
  projectFileContent: (projectId: string, fileId: number) =>
    request<ProjectFileContent>(`/projects/${projectId}/files/${fileId}/content`),
  deleteProjectFile: (projectId: string, fileId: number) =>
    request<void>(`/projects/${projectId}/files/${fileId}`, { method: 'DELETE' }),
  updateProjectFileContent: (projectId: string, fileId: number, content: string) =>
    request<ProjectFileContent>(`/projects/${projectId}/files/${fileId}/content`, {
      method: 'PUT',
      body: JSON.stringify({ content }),
    }),
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
  globalKnowledgeFileContent: (documentId: number) =>
    request<GlobalKnowledgeDocumentContent>(`/global-knowledge/files/${documentId}/content`),
  updateGlobalKnowledgeFileContent: (documentId: number, content: string) =>
    request<GlobalKnowledgeDocumentContent>(`/global-knowledge/files/${documentId}/content`, {
      method: 'PUT',
      body: JSON.stringify({ content }),
    }),
  uploadProjectForm: (projectId: string, file: File, signal?: AbortSignal) => {
    const body = new FormData()
    body.append('file', file)
    return request<ProjectFile>(`/projects/${projectId}/forms`, { method: 'POST', body, signal })
  },
  downloadProjectForm: async (projectId: string, formId: number, signal?: AbortSignal) => {
    const response = await requestResponse(`/projects/${projectId}/forms/${formId}/download`, { signal })
    return response.blob()
  },
  deleteProjectForm: (projectId: string, formId: number, signal?: AbortSignal) =>
    request<void>(`/projects/${projectId}/forms/${formId}`, { method: 'DELETE', signal }),
  compilationSessions: (projectId: string, conversationId: string, signal?: AbortSignal) =>
    request<CompilationSessionSummary[]>(`/projects/${projectId}/compilation-sessions?${new URLSearchParams({ conversation_id: conversationId })}`, { signal }),
  compilationSession: (projectId: string, sessionId: string, signal?: AbortSignal) =>
    request<CompilationSession>(`/projects/${projectId}/compilation-sessions/${encodeURIComponent(sessionId)}`, { signal }),
  startCompilationSession: (projectId: string, formId: number, conversationId: string | null, signal?: AbortSignal) =>
    request<CompilationSession>(`/projects/${projectId}/compilation-sessions`, {
      method: 'POST', signal,
      body: JSON.stringify({ form_id: formId, conversation_id: conversationId, start_in_chat: true }),
    }),
  resolveCompilationSession: (projectId: string, sessionId: string, version: number, fieldIds?: string[], signal?: AbortSignal, automatic = false) =>
    request<CompilationSession>(`/projects/${projectId}/compilation-sessions/${encodeURIComponent(sessionId)}/resolve`, {
      method: 'POST', signal, body: JSON.stringify({ version, ...(fieldIds ? { field_ids: fieldIds } : {}), ...(automatic ? { automatic: true } : {}) }),
    }),
  updateCompilationFields: (projectId: string, sessionId: string, version: number, fields: CompilationFieldInput[], signal?: AbortSignal) =>
    request<CompilationSession>(`/projects/${projectId}/compilation-sessions/${encodeURIComponent(sessionId)}/fields`, {
      method: 'PATCH', signal, body: JSON.stringify({ version, fields }),
    }),
  finalizeCompilationSession: (projectId: string, sessionId: string, version: number, allowUnresolved: boolean, signal?: AbortSignal) =>
    request<CompilationSession>(`/projects/${projectId}/compilation-sessions/${encodeURIComponent(sessionId)}/finalize`, {
      method: 'POST', signal, body: JSON.stringify({ version, allow_unresolved: allowUnresolved }),
    }),
  downloadCompilation: async (projectId: string, runId: string, kind: CompilationDownload, signal?: AbortSignal) => {
    const response = await requestResponse(
      `/projects/${projectId}/document-compilations/${encodeURIComponent(runId)}/download/${kind}`,
      { signal },
    )
    return response.blob()
  },
  conversation: (projectId: string, conversationId: string, signal?: AbortSignal) =>
    request<ConversationDetail>(
      `/projects/${projectId}/conversations/${conversationId}`,
      { signal },
    ),
  projectAnswer: (projectId: string, question: string, conversationId?: string | null, signal?: AbortSignal, formId?: number | null, compilation?: { session_id: string; version: number }) =>
    request<GroundedAnswer>(`/projects/${projectId}/answer`, {
      method: 'POST',
      body: JSON.stringify({ question, conversation_id: conversationId ?? null,
        ...(formId != null ? { form_id: formId } : {}),
        ...(compilation ? { compilation_session_id: compilation.session_id, compilation_version: compilation.version } : {}) }),
      signal,
    }),
  documentReview: (projectId: string, signal?: AbortSignal) =>
    request<DocumentReview>(`/projects/${projectId}/document-review`, { signal }),
}
