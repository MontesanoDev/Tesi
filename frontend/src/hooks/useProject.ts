import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import type { ProjectDetail } from '../types'

interface ProjectState {
  requestedId?: string
  project: ProjectDetail | null
  error: string | null
  loading: boolean
}

export function useProject(projectId?: string) {
  const [state, setState] = useState<ProjectState>(() => ({
    requestedId: projectId,
    project: null,
    error: projectId ? null : 'Progetto non specificato',
    loading: Boolean(projectId),
  }))

  useEffect(() => {
    if (!projectId) {
      setState({
        requestedId: projectId,
        project: null,
        error: 'Progetto non specificato',
        loading: false,
      })
      return
    }

    const controller = new AbortController()
    setState({ requestedId: projectId, project: null, error: null, loading: true })
    api
      .project(projectId, controller.signal)
      .then((result) => {
        if (controller.signal.aborted) return
        setState({ requestedId: projectId, project: result, error: null, loading: false })
      })
      .catch((reason: Error) => {
        if (controller.signal.aborted || reason.name === 'AbortError') return
        setState({
          requestedId: projectId,
          project: null,
          error: reason.message,
          loading: false,
        })
      })

    return () => controller.abort()
  }, [projectId])

  const refresh = useCallback(async () => {
    if (!projectId) return
    try {
      const result = await api.project(projectId)
      setState((current) => (
        current.requestedId === projectId
          ? { ...current, project: result, error: null }
          : current
      ))
    } catch (reason) {
      setState((current) => (
        current.requestedId === projectId
          ? {
              ...current,
              error: reason instanceof Error ? reason.message : 'Aggiornamento non riuscito',
            }
          : current
      ))
      throw reason
    }
  }, [projectId])

  const stateMatchesRoute = state.requestedId === projectId
  return {
    project: stateMatchesRoute ? state.project : null,
    error: stateMatchesRoute ? state.error : null,
    loading: !stateMatchesRoute || state.loading,
    refresh,
  }
}
