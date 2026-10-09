import { useCallback, useEffect, useRef, useState, type RefObject } from 'react'
import { api } from '../api'
import type { CompilationFieldInput, CompilationSession } from '../types'

interface State {
  key: string
  session: CompilationSession | null
  loading: boolean
  busy: boolean
  error: string | null
}

function hasActiveLease(session: CompilationSession | null) {
  return session?.status === 'ANALYZING' && Boolean(session.lease_until
    && Date.parse(session.lease_until) > Date.now())
}

// Backend owns progress and provenance. React holds only the displayed snapshot.
export function useCompilationSession(projectId?: string, conversationId?: string, formId?: number,
  suspended = false, chatRequest?: RefObject<AbortController | null>) {
  const key = JSON.stringify([projectId, conversationId, formId])
  const activeKey = useRef(key)
  activeKey.current = key
  const operation = useRef<AbortController | null>(null)
  const [state, setState] = useState<State>({ key, session: null, loading: Boolean(conversationId), busy: false, error: null })
  const [reload, setReload] = useState(0)
  const [poll, setPoll] = useState(0)
  const current = state.key === key ? state : { key, session: null, loading: Boolean(conversationId), busy: false, error: null }
  const processing = current.busy || hasActiveLease(current.session) || Boolean(
    current.session?.chat?.auto_continue && !current.session.chat.paused
    && !current.error && !current.loading && !suspended)

  useEffect(() => {
    const controller = new AbortController()
    // A read refresh keeps the displayed session and any drafts in its details.
    setState((s) => ({ key, session: s.key === key ? s.session : null,
      loading: Boolean(conversationId), busy: false, error: null }))
    if (projectId && conversationId) {
      api.compilationSessions(projectId, conversationId, controller.signal)
        .then(async (summaries) => {
          const match = summaries.find((item) => item.project_id === projectId
            && item.conversation_id === conversationId
            && (formId == null || item.original_file_id === formId))
          const session = match ? await api.compilationSession(projectId, match.id, controller.signal) : null
          if (!controller.signal.aborted && activeKey.current === key) {
            setState({ key, session, loading: false, busy: false, error: null })
          }
        })
        .catch((reason) => {
          if (!controller.signal.aborted) console.warn('Caricamento CompilationSession', reason)
          if (!controller.signal.aborted && activeKey.current === key) setState((s) => ({ ...s,
            loading: false, busy: false, error: 'Non riesco a caricare la compilazione. Riprova.' }))
        })
    }
    return () => {
      controller.abort()
      operation.current?.abort()
      operation.current = null
    }
  }, [key, projectId, conversationId, formId, reload])

  useEffect(() => {
    if (!projectId || current.session?.status !== 'ANALYZING' || current.session.chat?.paused || current.busy || current.loading) return
    const controller = new AbortController()
    const sessionId = current.session.id
    // Read-only polling recovers progress after a refresh; never starts another AI step.
    const timer = window.setTimeout(() => {
      api.compilationSession(projectId, sessionId, controller.signal).then((session) => {
        if (!controller.signal.aborted && activeKey.current === key) {
          setState((s) => ({ ...s, session, error: null }))
          setPoll((value) => value + 1)
        }
      }).catch(() => {
        if (!controller.signal.aborted && activeKey.current === key) {
          setState((s) => ({ ...s, error: 'Impossibile aggiornare la compilazione. I dati sono conservati.' }))
          setPoll((value) => value + 1)
        }
      })
    }, 3000)
    return () => { clearTimeout(timer); controller.abort() }
  }, [projectId, key, current.session, current.busy, current.loading, poll])

  const run = useCallback(async (action: (signal: AbortSignal) => Promise<CompilationSession>) => {
    if (!projectId || operation.current || chatRequest?.current || current.loading
      || suspended || hasActiveLease(current.session)) return null
    const controller = new AbortController()
    operation.current = controller
    setState((s) => ({ ...s, key, busy: true, error: null }))
    try {
      const session = await action(controller.signal)
      if (controller.signal.aborted || activeKey.current !== key) return null
      setState({ key, session, busy: false, loading: false, error: null })
      return session
    } catch (reason) {
      if (controller.signal.aborted || activeKey.current !== key) return null
      console.warn('Operazione CompilationSession', reason)
      // Errors and 409s can advance backend versions. Reload, never resubmit a mutation.
      const session = current.session
        ? await api.compilationSession(projectId, current.session.id, controller.signal).catch(() => null)
        : null
      if (!controller.signal.aborted && activeKey.current === key) setState((s) => ({ ...s,
        ...(session ? { session } : {}), busy: false,
        error: 'Ho conservato i dati già verificati. Non ho completato questa operazione. Puoi aggiornare lo stato e riprovare.',
      }))
      return null
    } finally {
      if (operation.current === controller) operation.current = null
    }
  }, [projectId, current.loading, current.session, key, suspended, chatRequest])

  useEffect(() => {
    const session = current.session
    if (!projectId || !session?.chat?.auto_continue || session.chat.paused || session.conversation_id !== conversationId
      || current.busy || current.loading
      || current.error || suspended || operation.current) return
    // One step per snapshot; the persisted backend budget authorizes every next step.
    // Refresh cannot reset the budget, and waiting/errors never trigger another mutation.
    void run((signal) => api.resolveCompilationSession(projectId, session.id, session.version,
      undefined, signal, true))
  }, [projectId, conversationId, current.session, current.busy, current.loading, current.error, suspended, run])

  return {
    ...current,
    processing,
    // The ref also closes the gap before React renders a newly started operation.
    isProcessing: () => processing || Boolean(operation.current),
    refresh: () => { if (!operation.current) setReload((value) => value + 1) },
    start: (id: number) => run((signal) => api.startCompilationSession(projectId!, id, conversationId ?? null, signal)),
    resolve: (fieldIds?: string[]) => current.session
      ? run((signal) => api.resolveCompilationSession(projectId!, current.session!.id, current.session!.version, fieldIds, signal)) : Promise.resolve(null),
    update: (field: CompilationFieldInput) => current.session
      ? run((signal) => api.updateCompilationFields(projectId!, current.session!.id, current.session!.version, [field], signal)) : Promise.resolve(null),
    finalize: (allowUnresolved = false) => current.session
      ? run((signal) => api.finalizeCompilationSession(projectId!, current.session!.id, current.session!.version, allowUnresolved, signal)) : Promise.resolve(null),
  }
}
