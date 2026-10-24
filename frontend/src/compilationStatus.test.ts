import { describe, expect, it } from 'vitest'
import { compilationActivity, compilationState } from './compilationStatus'
import type { CompilationSession } from './types'

function session(patch: Record<string, unknown> = {}, data: Record<string, unknown> = {}): CompilationSession {
  return {
    engine: 'global', id: 's', project_id: 'p', conversation_id: 'c', form_id: 1, original_file_id: 1,
    template_name: 'modulo.docx', status: 'WAITING_FOR_USER', version: 3, created_at: '', updated_at: '',
    lease_until: null, last_error: null, last_generation: null,
    summary: { total: 10, pending: 4, resolved: 0, missing: 0, ambiguous: 0, conflicting: 0, not_applicable: 0, user_provided: 0 },
    chat: { enabled: true, auto_continue: false, paused: false, question: null, analyzed: 0, verified: 0,
      user_provided: 0, remaining_questions: 0, steps_used: 0, max_steps: 0 },
    fields: [], open_issues: [],
    global_compilation: { phase: 'REVIEW', dialogue: { phase: 'READY' }, attempts: 1, candidate_count: 10,
      proposal_count: 3, omitted: 0, rejected: 0, report_url: null, fields: [], conditions: [], ...data },
    ...patch,
  } as unknown as CompilationSession
}

describe('Compilazione DOCX: stati reali', () => {
  it('names the running step without percentages', () => {
    expect(compilationActivity(null)).toBe('Avvio della Compilazione DOCX…')
    expect(compilationActivity(session({ status: 'ANALYZING' }, { phase: 'ANALYZING' })))
      .toBe('Analisi del documento e compilazione delle sezioni…')
    expect(compilationActivity(session())).toBe('Verifica dei dati…')
    const generate = session({ chat: { ...session().chat, question: { kind: 'generate', field_ids: [], message: 'Genero?' } } })
    expect(compilationActivity(generate)).toBe('Preparazione del DOCX…')
    expect(compilationActivity(session({ engine: 'legacy' }))).toBe('Sto lavorando…')
  })

  it('distinguishes waiting for clarifications from a completed check', () => {
    const asking = session({ chat: { ...session().chat, question: { kind: 'clarifications', field_ids: [], message: '?' } } })
    expect(compilationState(asking)?.label).toBe('Compilazione DOCX · attesa di chiarimenti')
    expect(compilationState(session())?.label).toBe('Compilazione DOCX · verifica dei dati completata')
  })

  it('never presents a draft with an unanalyzed section as complete', () => {
    const generation = { id: 'g', session_version: 3 }
    const failed = session({ last_generation: generation, summary: { ...session().summary, pending: 0 } },
      { segments: [{ index: 1, status: 'analyzed' }, { index: 2, status: 'failed', error: 'JSON' }] })
    const state = compilationState(failed)!
    expect(state.label).toBe('Compilazione DOCX · bozza incompleta')
    expect(state.notes[0]).toContain('Una parte del documento non è stata analizzata')
    expect(state.notes).toContain('Il DOCX è una bozza: va verificato prima dell’uso.')
    const complete = session({ last_generation: generation, summary: { ...session().summary, pending: 0 } },
      { segments: [{ index: 1, status: 'analyzed' }] })
    expect(compilationState(complete)?.label).toBe('Compilazione DOCX · bozza completata')
  })

  it('explains when an interrupted compilation can be resumed', () => {
    const lease = new Date(Date.now() + 20 * 60 * 1000).toISOString()
    const state = compilationState(session({ status: 'ANALYZING', lease_until: lease }, { phase: 'ANALYZING' }))!
    expect(state.label).toBe('Compilazione DOCX · compilazione in corso')
    expect(state.notes[0]).toMatch(/potrai riprendere la compilazione dalle \d{2}:\d{2}/)
    expect(compilationState(session({ status: 'FAILED', last_error: 'x' }))?.label)
      .toBe('Compilazione DOCX · compilazione interrotta')
  })

  it('shows no technical revision or experimental label', () => {
    const texts = [compilationActivity(session()), compilationState(session())?.label ?? '']
    for (const text of texts) expect(text).not.toMatch(/P3|rev ?3|beta|sperimental|monolitic/i)
  })
})
