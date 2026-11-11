import type { DocumentReference } from './types'

export interface ChatSubmission {
  request_id: string
  conversation_id: string | null
  document_id?: number
  compilation?: { session_id: string; version: number }
}

export interface RecoverableMessage {
  text: string
  document_reference: DocumentReference | null
  // A copy kept when the message was sent (failure or interrupted send). A draft only typed
  // is false; copies saved before this flag existed count as sent, the prudent reading.
  submitted?: boolean
  submission?: ChatSubmission
}

function key(projectId: string, conversationId?: string | null) {
  return `mapi:chat-draft:${encodeURIComponent(projectId)}:${encodeURIComponent(conversationId ?? 'new')}`
}

export function readChatDraft(projectId: string, conversationId?: string | null): {
  message: RecoverableMessage | null; unavailable: boolean
} {
  try {
    const raw = sessionStorage.getItem(key(projectId, conversationId))
    if (!raw) return { message: null, unavailable: false }
    const value = JSON.parse(raw)
    if (typeof value?.text !== 'string' || !['boolean', 'undefined'].includes(typeof value.submitted)) {
      return { message: null, unavailable: true }
    }
    const ref = value.document_reference
    if (ref !== null && (!ref || !Number.isInteger(ref.document_id)
      || typeof ref.name !== 'string' || !['source', 'form'].includes(ref.role))) {
      return { message: null, unavailable: true }
    }
    const s = value.submission
    if (s && (typeof s.request_id !== 'string' || !s.request_id || s.request_id.length > 100
      || !(s.conversation_id === null || typeof s.conversation_id === 'string')
      || (s.document_id !== undefined && (!Number.isInteger(s.document_id) || s.document_id < 1))
      || (s.compilation && (typeof s.compilation.session_id !== 'string'
        || !Number.isInteger(s.compilation.version) || s.compilation.version < 1)))) {
      return { message: null, unavailable: true }
    }
    return { message: value, unavailable: false }
  } catch {
    return { message: null, unavailable: true }
  }
}

export function sameMessage(message: RecoverableMessage | null, text: string,
  reference: DocumentReference | null) {
  return message?.text === text && message.document_reference?.document_id === reference?.document_id
    && message.document_reference?.role === reference?.role
}

export function saveChatDraft(projectId: string, conversationId: string | null | undefined,
  message: RecoverableMessage | null): boolean {
  try {
    if (message?.text) sessionStorage.setItem(key(projectId, conversationId), JSON.stringify(message))
    else sessionStorage.removeItem(key(projectId, conversationId))
    return true
  } catch {
    return false
  }
}
