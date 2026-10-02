import { act, cleanup, render, screen } from '@testing-library/react'
import { createMemoryRouter, RouterProvider } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { DocumentReview, ProjectDetail } from '../types'
import { DocumentReviewPage } from './DocumentReviewPage'

vi.mock('../api', () => ({
  api: { project: vi.fn(), documentReview: vi.fn() },
}))

function projectDetail(id: string): ProjectDetail {
  return {
    id, title: `Progetto ${id}`, description: '', status: 'In analisi',
    status_tone: 'info', updated_label: '', source_count: 0, model_count: 0,
    instructions: '', call_fact_count: 0, missing_fact_count: 0,
    files: [], knowledge_sources: [], conversations: [],
  }
}

function reviewDetail(id: string): DocumentReview {
  return {
    title: `Documento ${id}`, subtitle: '', completed_fields: 0, total_fields: 0, fields: [],
  }
}

function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (reason: Error) => void
  const promise = new Promise<T>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise
    reject = rejectPromise
  })
  return { promise, resolve, reject }
}

function renderReview() {
  const router = createMemoryRouter(
    [{ path: '/projects/:projectId/document-review', element: <DocumentReviewPage /> }],
    { initialEntries: ['/projects/primo/document-review'] },
  )
  render(<RouterProvider router={router} />)
  return router
}

describe('DocumentReviewPage', () => {
  afterEach(cleanup)

  beforeEach(() => {
    vi.mocked(api.project).mockReset()
    vi.mocked(api.project).mockImplementation(async (id) => projectDetail(id))
    vi.mocked(api.documentReview).mockReset()
    vi.mocked(api.documentReview).mockImplementation(async (id) => reviewDetail(id))
  })

  it('shows a review request error instead of loading indefinitely', async () => {
    vi.mocked(api.documentReview).mockRejectedValue(new Error('Revisione non disponibile'))
    renderReview()

    expect(await screen.findByRole('alert')).toHaveTextContent('Revisione non disponibile')
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })

  it('shows a project error even while the review is still pending', async () => {
    vi.mocked(api.project).mockRejectedValue(new Error('Progetto non trovato'))
    vi.mocked(api.documentReview).mockReturnValue(deferred<DocumentReview>().promise)
    renderReview()

    expect(await screen.findByRole('alert')).toHaveTextContent('Progetto non trovato')
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })

  it('renders zero progress for an empty review', async () => {
    renderReview()

    expect(await screen.findByText('0% completato')).toBeVisible()
    expect(screen.queryByText(/NaN/)).not.toBeInTheDocument()
    expect(screen.getByText('Demo')).toBeVisible()
    expect(screen.getByRole('link', { name: 'Apri moduli e bozze' })).toHaveAttribute('href', '/projects/primo?documents=docx')
    expect(screen.queryByRole('button', { name: 'Salva' })).not.toBeInTheDocument()
    expect(screen.queryByText('Giulia Bianchi')).not.toBeInTheDocument()
  })

  it('clears the previous review while loading another project', async () => {
    const next = deferred<DocumentReview>()
    vi.mocked(api.documentReview)
      .mockResolvedValueOnce(reviewDetail('primo'))
      .mockReturnValueOnce(next.promise)
    const router = renderReview()
    await screen.findByRole('heading', { name: 'Documento primo' })

    await act(async () => { await router.navigate('/projects/secondo/document-review') })
    expect(screen.queryByRole('heading', { name: 'Documento primo' })).not.toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveTextContent('Caricamento')

    await act(async () => next.resolve(reviewDetail('secondo')))
    expect(await screen.findByRole('heading', { name: 'Documento secondo' })).toBeVisible()
  })

  it('clears a previous error when navigating to another project', async () => {
    vi.mocked(api.documentReview).mockRejectedValueOnce(new Error('Errore primo progetto'))
    const router = renderReview()
    await screen.findByRole('alert')

    await act(async () => { await router.navigate('/projects/secondo/document-review') })
    expect(await screen.findByRole('heading', { name: 'Documento secondo' })).toBeVisible()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it.each(['success', 'failure'] as const)(
    'ignores a late %s from the previous project',
    async (outcome) => {
      const stale = deferred<DocumentReview>()
      vi.mocked(api.documentReview).mockReturnValueOnce(stale.promise)
      const router = renderReview()
      const signal = vi.mocked(api.documentReview).mock.calls[0][1]

      await act(async () => { await router.navigate('/projects/secondo/document-review') })
      await screen.findByRole('heading', { name: 'Documento secondo' })
      expect(signal?.aborted).toBe(true)

      await act(async () => {
        if (outcome === 'success') stale.resolve(reviewDetail('primo'))
        else stale.reject(new Error('Errore primo progetto'))
      })
      expect(screen.getByRole('heading', { name: 'Documento secondo' })).toBeVisible()
      expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    },
  )
})
