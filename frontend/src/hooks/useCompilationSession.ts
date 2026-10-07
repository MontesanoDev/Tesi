import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../api'
import type { CompilationFieldInput, CompilationSession } from '../types'

interface State {
  key: string
  session: CompilationSession | null
  loading: boolean
  busy: boolean
  error: string | null
}

// Backend owns progress and provenance. React holds only the displayed snapshot.
export function useCompilationSession(projectId?: string, conversationId?: string, formId?: number, suspended = false) {
  const key = JSON.stringify([projectId, conversationId, formId])
  const activeKey = useRef(key)
  activeKey.current = key
  const operation = useRef<AbortController | null>(null)
  const [state, setState] = useState<State>({ key, session: null, loading: false, busy: false, error: null })
  const [reload, setReload] = useState(0)
  const current = state.key === key ? state : { key, session: null, loading: Boolean(conversationId), busy: false, error: null }

  useEffect(() => {
    const controller = new AbortController()
    setState({ key, session: null, loading: Boolean(conversationId), busy: false, error: null })
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
          if (!controller.signal.aborted && activeKey.current === key) setState({ key, session: null,
            loading: false, busy: false, error: reason instanceof Error ? reason.message : 'Sessione non disponibile' })
        })
    }
    return () => {
      controller.abort()
      operation.current?.abort()
      operation.current = null
    }
  }, [key, projectId, conversationId, formId, reload])

  useEffect(() => {
    if (!projectId || current.session?.status !== 'ANALYZING' || current.session.chat?.paused || current.busy) return
    const controller = new AbortController()
    const sessionId = current.session.id
    // Read-only polling recovers progress after a refresh; never starts another AI step.
    const timer = window.setTimeout(() => {
      api.compilationSession(projectId, sessionId, controller.signal).then((session) => {
        if (!controller.signal.aborted && activeKey.current === key) setState((s) => ({ ...s, session }))
      }).catch(() => {
        if (!controller.signal.aborted && activeKey.current === key) setState((s) => ({
          ...s, error: 'Impossibile aggiornare la compilazione. Riprova dal controllo dei dettagli.',
        }))
      })
    }, 3000)
    return () => { clearTimeout(timer); controller.abort() }
  }, [projectId, key, current.session, current.busy])

  const run = useCallback(async (action: (signal: AbortSignal) => Promise<CompilationSession>) => {
    if (!projectId || operation.current || current.loading) return null
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
      // Errors and 409s can advance backend versions. Reload, never resubmit a mutation.
      const session = current.session
        ? await api.compilationSession(projectId, current.session.id, controller.signal).catch(() => null)
        : null
      if (!controller.signal.aborted && activeKey.current === key) setState((s) => ({ ...s,
        ...(session ? { session } : {}), busy: false,
        error: reason instanceof Error ? reason.message : 'Operazione non riuscita',
      }))
      return null
    } finally {
      if (operation.current === controller) operation.current = null
    }
  }, [projectId, current.loading, current.session, key])

  useEffect(() => {
    const session = current.session
    if (!projectId || !session?.chat?.auto_continue || session.conversation_id !== conversationId
      || current.busy || current.loading
      || current.error || suspended || operation.current) return
    // One step per snapshot; the persisted backend budget authorizes every next step.
    // Refresh cannot reset the budget, and waiting/errors never trigger another mutation.
    void run((signal) => api.resolveCompilationSession(projectId, session.id, session.version,
      undefined, signal, true))
  }, [projectId, conversationId, current.session, current.busy, current.loading, current.error, suspended, run])

  return {
    ...current,
    refresh: () => setReload((value) => value + 1),
    start: (id: number) => run((signal) => api.startCompilationSession(projectId!, id, conversationId ?? null, signal)),
    resolve: (fieldIds?: string[]) => current.session
      ? run((signal) => api.resolveCompilationSession(projectId!, current.session!.id, current.session!.version, fieldIds, signal)) : Promise.resolve(null),
    update: (field: CompilationFieldInput) => current.session
      ? run((signal) => api.updateCompilationFields(projectId!, current.session!.id, current.session!.version, [field], signal)) : Promise.resolve(null),
    finalize: (allowUnresolved = false) => current.session
      ? run((signal) => api.finalizeCompilationSession(projectId!, current.session!.id, current.session!.version, allowUnresolved, signal)) : Promise.resolve(null),
  }
}
