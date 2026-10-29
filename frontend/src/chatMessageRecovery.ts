import type { DocumentReference } from './types'

export interface RecoverableMessage {
  text: string
  document_reference: DocumentReference | null
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
    if (typeof value?.text !== 'string') return { message: null, unavailable: true }
    const ref = value.document_reference
    if (ref !== null && (!ref || !Number.isInteger(ref.document_id)
      || typeof ref.name !== 'string' || !['source', 'form'].includes(ref.role))) {
      return { message: null, unavailable: true }
    }
    return { message: value, unavailable: false }
  } catch {
    return { message: null, unavailable: true }
  }
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
