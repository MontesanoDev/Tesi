import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import type { ProjectDetail } from '../types'

export function useProject(projectId?: string) {
  const [project, setProject] = useState<ProjectDetail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!projectId) {
      setError('Progetto non specificato')
      setLoading(false)
      return
    }

    const controller = new AbortController()
    setLoading(true)
    api
      .project(projectId, controller.signal)
      .then((result) => {
        setProject(result)
        setError(null)
      })
      .catch((reason: Error) => {
        if (reason.name !== 'AbortError') setError(reason.message)
      })
      .finally(() => setLoading(false))

    return () => controller.abort()
  }, [projectId])

  const refresh = useCallback(async () => {
    if (!projectId) return
    try {
      const result = await api.project(projectId)
      setProject(result)
      setError(null)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Aggiornamento non riuscito')
      throw reason
    }
  }, [projectId])

  return { project, error, loading, refresh }
}
