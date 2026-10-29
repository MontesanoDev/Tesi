import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { CompilationSession, GroundedAnswer } from '../types'
import { CompilationReply } from './CompilationReply'

vi.mock('../api', () => ({ api: { downloadCompilation: vi.fn() } }))

const FULL = [
  '☐ Libero professionista singolo',
  '☐ Legale rappresentante di società di professionisti (art. 66, comma 1, lett. b) avente la seguente',
]

function session(dialogue: Record<string, unknown>, patch: Record<string, unknown> = {}) {
  return {
    engine: 'global', id: 's', project_id: 'p', conversation_id: 'c', form_id: 1, original_file_id: 1,
    template_name: 'modulo.docx', status: 'WAITING_FOR_USER', version: 3, created_at: '', updated_at: '',
    lease_until: null, last_error: null, last_generation: null,
    summary: { total: 1, pending: 1, resolved: 0, missing: 0, ambiguous: 0, conflicting: 0, not_applicable: 0, user_provided: 0 },
    chat: { enabled: true, auto_continue: false, paused: false, question: null, analyzed: 0, verified: 0,
      user_provided: 0, remaining_questions: 1, steps_used: 0, max_steps: 0 },
    fields: [], open_issues: [],
    global_compilation: { phase: 'REVIEW', dialogue: { phase: 'READY', ...dialogue }, attempts: 1,
      candidate_count: 1, proposal_count: 0, omitted: 0, rejected: 0, report_url: null, fields: [], conditions: [] },
    ...patch,
  } as unknown as CompilationSession
}

function reply(value: CompilationSession, response: GroundedAnswer | null = null, processing = false) {
  return render(<CompilationReply session={value} response={response} pending={false}
    processing={processing} locked={false} error={null} onRetry={() => {}} />)
}

describe('Testo completo del modulo separato dalla domanda', () => {
  afterEach(cleanup)
  const message = 'Quale qualità scegli?\n1. Libero professionista singolo\n2. Legale rappresentante di società di professionisti'
  const slots = [{ slot: 1, label: 'IN QUALITÀ DI', details: FULL }, { slot: 2, label: 'Luogo e data' }]

  it('shows the short question and keeps the full FORM text collapsed', () => {
    const { container } = reply(session({ message, question: { slots } }))
    expect(screen.getByText(/Quale qualità scegli\?/)).toBeInTheDocument()
    const details = container.querySelectorAll('details')
    expect(details).toHaveLength(1)
    expect(details[0]).not.toHaveAttribute('open')
    expect(screen.getByText('Testo completo del modulo: IN QUALITÀ DI')).toBeInTheDocument()
    expect(details[0]).toHaveTextContent('(art. 66, comma 1, lett. b)')
  })

  it.each([
    ['in elaborazione', session({ message, question: { slots } }), true],
    ['in revisione', session({ phase: 'PENDING', message, question: { slots } }), false],
    ['in pausa', session({ message, question: { slots } }, { chat: { paused: true } }), false],
  ])('never shows details beside another state: %s', (_, value, processing) => {
    const { container } = reply(value, null, processing)
    expect(container.querySelector('details')).toBeNull()
  })

  it('does not attach details to a clarification of the planner', () => {
    const clarify = { answer: 'Puoi precisare?', compilation: { session_id: 's', action: 'clarify' } } as unknown as GroundedAnswer
    const { container } = reply(session({ message, question: { slots } }), clarify)
    expect(container.querySelector('details')).toBeNull()
  })
})
