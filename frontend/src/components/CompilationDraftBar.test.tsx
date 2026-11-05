import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import { CompilationDraftBar } from './CompilationDraftBar'
import { CompilationReply } from './CompilationReply'
import type { CompilationSession } from '../types'

vi.mock('../api', () => ({ api: { downloadCompilation: vi.fn() } }))
afterEach(cleanup)

function session(overrides: Partial<CompilationSession> = {}) {
  return {
    id: 's1', project_id: 'alpha', engine: 'global', status: 'WAITING_FOR_USER', version: 9,
    template_name: 'modulo.docx', open_issues: [], fields: [],
    summary: { pending: 1 }, chat: { paused: false, question: null },
    global_compilation: { phase: 'REVIEW', paused: false, segments: [],
      dialogue: { phase: 'READY', message: 'Messaggio del narratore.', question: null } },
    last_generation: { id: 'run-2', project_id: 'alpha', template_name: 'modulo.docx',
      created_at: '2026-11-05T15:17:00+00:00', status: 'needs_review', session_version: 8,
      changes_since_export: false, downloads: { docx: '/f', report: '/r', template: '/o' } },
    ...overrides,
  } as unknown as CompilationSession
}

describe('CompilationDraftBar', () => {
  beforeEach(() => vi.mocked(api.downloadCompilation).mockReset())

  it('shows the draft once and asks for nothing when nothing changed', () => {
    render(<CompilationDraftBar session={session()} locked={false} onRequestDraft={() => {}} />)
    expect(screen.getAllByRole('button', { name: 'Scarica DOCX' })).toHaveLength(1)
    expect(screen.queryByText(/modifiche non ancora/)).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Prepara nuova bozza' })).not.toBeInTheDocument()
  })

  it('says the file is behind and only prepares a request, it never exports by itself', () => {
    const onRequest = vi.fn()
    const base = session()
    render(<CompilationDraftBar session={session({ last_generation: {
      ...base.last_generation!, changes_since_export: true } })} locked={false} onRequestDraft={onRequest} />)
    expect(screen.getByText(/modifiche non ancora in questo file/)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Prepara nuova bozza' }))
    expect(onRequest).toHaveBeenCalledTimes(1)
    expect(api.downloadCompilation).not.toHaveBeenCalled()
  })

  it('keeps earlier drafts downloadable by their own id', async () => {
    vi.mocked(api.downloadCompilation).mockResolvedValue(new Blob(['x']))
    globalThis.URL.createObjectURL = vi.fn(() => 'blob:x')
    globalThis.URL.revokeObjectURL = vi.fn()
    render(<CompilationDraftBar session={session({ draft_history: [
      { id: 'run-1', created_at: '2026-11-05T14:00:00+00:00', session_version: 4 }] })}
      locked={false} onRequestDraft={() => {}} />)
    fireEvent.click(screen.getByRole('button', { name: /Scarica la bozza del/ }))
    await waitFor(() => expect(api.downloadCompilation).toHaveBeenCalledWith(
      'alpha', 'run-1', 'docx', expect.anything()))
  })

  it('is absent without a draft and for the previous engine', () => {
    const { container, rerender } = render(<CompilationDraftBar session={session({ last_generation: null })}
      locked={false} onRequestDraft={() => {}} />)
    expect(container).toBeEmptyDOMElement()
    rerender(<CompilationDraftBar session={session({ engine: 'legacy' } as Partial<CompilationSession>)}
      locked={false} onRequestDraft={() => {}} />)
    expect(container).toBeEmptyDOMElement()
  })
})

describe('CompilationReply with a global draft', () => {
  function reply(next: CompilationSession, action = 'updated') {
    return render(<CompilationReply session={next} pending={false} processing={false} locked={false}
      error={null} onRetry={() => {}} response={{ answer: 'x', compilation: { session_id: 's1', action } } as never} />)
  }

  it.each(['updated', 'paused'])('a %s reply does not republish the block', (action) => {
    reply(session(), action)
    expect(screen.queryByRole('button', { name: 'Scarica DOCX' })).not.toBeInTheDocument()
    expect(screen.queryByText(/bozza incompleta/)).not.toBeInTheDocument()
    expect(screen.queryByText(/precede le ultime modifiche/)).not.toBeInTheDocument()
  })
})
