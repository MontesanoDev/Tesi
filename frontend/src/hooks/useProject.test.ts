import { act, cleanup, renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { ProjectDetail } from '../types'
import { useProject } from './useProject'

vi.mock('../api', () => ({
  api: {
    project: vi.fn(),
  },
}))

interface PendingRequest {
  resolve: (project: ProjectDetail) => void
}

function projectDetail(id: string): ProjectDetail {
  return {
    id,
    title: `Progetto ${id}`,
    description: 'Descrizione',
    status: 'In analisi',
    status_tone: 'info',
    updated_label: 'Aggiornato ora',
    source_count: 0,
    model_count: 0,
    instructions: '',
    call_fact_count: 0,
    missing_fact_count: 0,
    files: [],
    knowledge_sources: [],
    conversations: [],
  }
}

describe('useProject', () => {
  const requests = new Map<string, PendingRequest>()

  afterEach(cleanup)

  beforeEach(() => {
    requests.clear()
    vi.mocked(api.project).mockReset()
    vi.mocked(api.project).mockImplementation((projectId) => (
      new Promise<ProjectDetail>((resolve) => {
        requests.set(projectId, { resolve })
      })
    ))
  })

  it('keeps loading when a stale project request completes during navigation', async () => {
    const { result, rerender } = renderHook(
      ({ projectId }) => useProject(projectId),
      { initialProps: { projectId: 'primo' } },
    )
    await waitFor(() => expect(requests.has('primo')).toBe(true))

    rerender({ projectId: 'secondo' })
    await waitFor(() => expect(requests.has('secondo')).toBe(true))

    await act(async () => requests.get('primo')?.resolve(projectDetail('primo')))
    expect(result.current.loading).toBe(true)
    expect(result.current.project).toBeNull()
    expect(result.current.error).toBeNull()

    await act(async () => requests.get('secondo')?.resolve(projectDetail('secondo')))
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.project?.id).toBe('secondo')
  })
})
