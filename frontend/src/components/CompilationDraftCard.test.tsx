import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import { draftsOfConversation } from '../compilationDrafts'
import { CompilationDraftCard } from './CompilationDraftCard'
import type { CompilationChatAction, CompilationSession } from '../types'

vi.mock('../api', () => ({ api: { downloadCompilation: vi.fn() } }))
afterEach(cleanup)

const FIRST = { id: 'run-1', created_at: '2026-11-05T15:00:00+00:00', session_version: 4 }

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
    draft_history: [FIRST],
    ...overrides,
  } as unknown as CompilationSession
}

function turn(id: string, action?: CompilationChatAction['action'], generation_id?: string) {
  return { id, result: action ? { compilation: { session_id: 's1', action, generation_id } } : {} }
}

describe('draftsOfConversation', () => {
  it('lega ogni bozza al messaggio che l’ha prodotta; i messaggi ordinari non ne ricevono', () => {
    const turns = [turn('1', 'updated'), turn('2', 'generated', 'run-1'), turn('3'), turn('4', 'generated', 'run-2'), turn('5')]
    const { byTurn, unclaimed } = draftsOfConversation(session(), turns)
    expect(byTurn.get('2')?.id).toBe('run-1')
    expect(byTurn.get('2')?.number).toBe(1)
    expect(byTurn.get('4')?.id).toBe('run-2')
    expect(byTurn.get('4')?.number).toBe(2)
    expect([...byTurn.keys()]).toEqual(['2', '4'])
    expect(unclaimed).toEqual([])
  })

  it('un messaggio salvato prima del collegamento riceve la bozza nello stesso ordine', () => {
    const { byTurn } = draftsOfConversation(session(), [turn('2', 'generated'), turn('4', 'generated')])
    expect(byTurn.get('2')?.id).toBe('run-1')
    expect(byTurn.get('4')?.id).toBe('run-2')
  })

  it('una bozza senza messaggio compare una sola volta, e nessuna per altri motori o sessioni', () => {
    const { byTurn, unclaimed } = draftsOfConversation(session(), [turn('2', 'generated', 'run-2')])
    expect(byTurn.get('2')?.id).toBe('run-2')
    expect(unclaimed.map((draft) => draft.id)).toEqual(['run-1'])
    expect(draftsOfConversation(session({ engine: 'legacy' } as Partial<CompilationSession>), [turn('2', 'generated', 'run-2')]).byTurn.size).toBe(0)
    expect(draftsOfConversation(null, [turn('2', 'generated', 'run-2')]).byTurn.size).toBe(0)
  })
})

describe('CompilationDraftCard', () => {
  const draft = { id: 'run-2', created_at: '2026-11-05T15:17:00+00:00', number: 2 }

  it('scarica proprio la bozza della scheda e non genera nulla', async () => {
    vi.mocked(api.downloadCompilation).mockResolvedValue(new Blob(['x']))
    URL.createObjectURL = vi.fn(() => 'blob:x')
    URL.revokeObjectURL = vi.fn()
    render(<CompilationDraftCard session={session()} locked={false} onRequestDraft={vi.fn()}
      draft={{ id: 'run-1', created_at: FIRST.created_at, number: 1 }} />)
    expect(screen.getByRole('region', { name: 'Bozza 1 esportata' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Scarica DOCX' }))
    await waitFor(() => expect(api.downloadCompilation).toHaveBeenCalledWith('alpha', 'run-1', 'docx', expect.anything()))
  })

  it('solo l’ultima bozza avvisa delle modifiche non esportate; il pulsante non esporta', () => {
    const request = vi.fn()
    const changed = session({ last_generation: { ...session().last_generation!, changes_since_export: true } })
    render(<CompilationDraftCard session={changed} draft={draft} locked={false} onRequestDraft={request} />)
    expect(screen.getByText(/modifiche non ancora in questo file/)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Prepara nuova bozza' }))
    expect(request).toHaveBeenCalledOnce()
    cleanup()
    render(<CompilationDraftCard session={changed} locked={false} onRequestDraft={request}
      draft={{ id: 'run-1', created_at: FIRST.created_at, number: 1 }} />)
    expect(screen.queryByText(/modifiche non ancora in questo file/)).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Prepara nuova bozza' })).not.toBeInTheDocument()
  })

  it('senza modifiche resta discreta', () => {
    render(<CompilationDraftCard session={session()} draft={draft} locked={false} onRequestDraft={vi.fn()} />)
    expect(screen.getByText(/va verificato prima dell’uso/)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Prepara nuova bozza' })).not.toBeInTheDocument()
  })
})
