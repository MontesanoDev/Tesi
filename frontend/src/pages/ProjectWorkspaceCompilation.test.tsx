import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { Link, MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { CompilationSession, CompilationSessionField, GroundedAnswer, ProjectDetail } from '../types'
import { ProjectWorkspacePage } from './ProjectWorkspacePage'

vi.mock('../api', () => ({ api: {
  project: vi.fn(), conversation: vi.fn(), projectAnswer: vi.fn(), compilationSessions: vi.fn(),
  compilationSession: vi.fn(), startCompilationSession: vi.fn(), resolveCompilationSession: vi.fn(),
  updateCompilationFields: vi.fn(), finalizeCompilationSession: vi.fn(), downloadCompilation: vi.fn(),
} }))
vi.mock('../components/ProjectKnowledgePanel', () => ({ ProjectKnowledgePanel: () => null }))
vi.mock('../components/ProjectModelSelector', () => ({ ProjectModelSelector: () => null }))

const form = { id: 10, name: 'domanda.docx', kind: 'form' as const, status: 'Caricato', metadata: '', page_count: 1, chunk_count: 1 }
const reference = { form_id: form.id, name: form.name }
function field(id: string, label: string, status: CompilationSessionField['status'] = 'PENDING'): CompilationSessionField {
  return { id, candidate_id: id, label, status, value: status === 'RESOLVED' ? 'Mapi S.r.l.' : null,
    provenance: status === 'RESOLVED' ? 'SOURCE' : null, reason: '', validation_errors: [],
    form_evidence: { role: 'form', source_name: form.name, candidate_id: id },
    source_evidence: status === 'RESOLVED' ? [{ role: 'source', source_name: 'visura.txt', chunk_id: 2,
      file_id: -1, chunk_index: 0, excerpt: 'Mapi S.r.l.', quote: 'Denominazione: Mapi S.r.l.',
      relevance: 1, project_id: null, category: 'company' }] : [], alternatives: [],
    requirement: status === 'PENDING' ? null : { name: label, person_role: '', form_quote: label },
  }
}
function session(fields = [field('t0:r0:c1', 'Denominazione'), field('t0:r1:c1', 'Data abilitazione')],
  status: CompilationSession['status'] = 'CREATED', version = 1): CompilationSession {
  const summary = { total: fields.length, pending: 0, resolved: 0, missing: 0, ambiguous: 0,
    conflicting: 0, not_applicable: 0, user_provided: 0 }
  for (const f of fields) summary[f.status.toLowerCase() as Exclude<keyof typeof summary, 'total'>] += 1
  return { id: 'session-1', project_id: 'alpha', conversation_id: 'chat-1', form_id: 10,
    original_file_id: 10, template_name: form.name, status, version, created_at: '', updated_at: '',
    lease_until: null, last_error: null, last_generation: null, summary, fields,
    open_issues: fields.filter((f) => ['PENDING', 'MISSING', 'AMBIGUOUS', 'CONFLICTING'].includes(f.status))
      .map((f) => ({ field_id: f.id, label: f.label, status: f.status, reason: f.reason, validation_errors: [] })),
  }
}
function conversational(s: CompilationSession, paused = false): CompilationSession {
  const asked = s.fields.find((f) => ['MISSING', 'AMBIGUOUS', 'CONFLICTING'].includes(f.status))
  return { ...s, chat: { enabled: true, auto_continue: s.status === 'CREATED' && !paused,
    paused, question: asked ? { kind: 'value', field_ids: [asked.id], message: `Mi manca ${asked.label}. Qual è?` }
      : s.status === 'READY' ? { kind: 'generate', field_ids: [], message: 'Vuoi che generi il DOCX?' } : null,
    analyzed: s.summary.total - s.summary.pending, verified: s.summary.resolved,
    user_provided: s.summary.user_provided, remaining_questions: s.open_issues.filter((f) => f.status !== 'PENDING').length,
    steps_used: paused ? 36 : 0, max_steps: 36 } }
}
const originalScrollTo = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'scrollTo')
let stored: CompilationSession | null
async function setup(path = '/projects/alpha') {
  const view = render(<MemoryRouter initialEntries={[path]}>
    <Link to="/projects/beta">Vai a Beta</Link>
    <Routes>
      <Route path="/projects/:projectId" element={<ProjectWorkspacePage />} />
      <Route path="/projects/:projectId/conversations/:conversationId" element={<ProjectWorkspacePage />} />
    </Routes>
  </MemoryRouter>)
  await screen.findByRole('heading', { name: 'alpha' })
  await waitFor(() => expect(screen.queryByText('Caricamento conversazione')).not.toBeInTheDocument())
  return view
}
function selectForm(name = form.name) {
  fireEvent.change(screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' }), { target: { value: '@' } })
  fireEvent.click(screen.getByRole('option', { name }))
}
async function start() {
  selectForm()
  const button = screen.getByRole('button', { name: 'Avvia compilazione' })
  await waitFor(() => expect(button).toBeEnabled())
  fireEvent.click(button)
  await screen.findByRole('region', { name: 'Compilazione domanda.docx' })
}
function submit(text: string) {
  fireEvent.change(screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' }), { target: { value: text } })
  fireEvent.click(screen.getByRole('button', { name: 'Invia' }))
}

describe('CompilationSession nella chat', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    Object.defineProperty(HTMLElement.prototype, 'scrollTo', { configurable: true, value: vi.fn() })
    stored = null
    vi.stubGlobal('requestAnimationFrame', () => 1)
    vi.stubGlobal('cancelAnimationFrame', vi.fn())
    vi.mocked(api.project).mockImplementation(async (id) => ({ id, title: id, description: 'Progetto',
      status: 'Bozza', status_tone: 'info', updated_label: '', source_count: 0, model_count: 0,
      instructions: '', call_fact_count: 0, missing_fact_count: 0, knowledge_sources: [], conversations: [],
      files: id === 'alpha' ? [form, { ...form, id: 11, name: 'istruzioni.txt' },
        { ...form, id: 12, name: 'fonte.txt', kind: 'source' }] : [{ ...form, id: 20, name: 'privato-beta.docx' }],
    } as ProjectDetail))
    vi.mocked(api.conversation).mockImplementation(async (project, id) => ({ id, project_id: project,
      title: 'Chat', metadata: '', target: 'chat', turns: [], form_reference: reference }))
    vi.mocked(api.compilationSessions).mockImplementation(async (project, conversation) =>
      stored && stored.project_id === project && stored.conversation_id === conversation ? [structuredClone(stored)] : [])
    vi.mocked(api.compilationSession).mockImplementation(async () => structuredClone(stored!))
    vi.mocked(api.startCompilationSession).mockImplementation(async () => {
      stored ??= session()
      return structuredClone(stored)
    })
    vi.mocked(api.resolveCompilationSession).mockImplementation(async () => {
      stored = session([field('t0:r0:c1', 'Denominazione', 'RESOLVED'),
        field('t0:r1:c1', 'Data abilitazione', 'MISSING')], 'WAITING_FOR_USER', 3)
      return structuredClone(stored)
    })
    vi.mocked(api.updateCompilationFields).mockImplementation(async (_p, _s, version, inputs) => {
      const fields = stored!.fields.map((f) => f.id === inputs[0].field_id
        ? { ...f, value: inputs[0].value!, provenance: 'USER' as const, status: 'USER_PROVIDED' as const } : f)
      stored = session(fields, 'READY', version + 1)
      return structuredClone(stored)
    })
    vi.mocked(api.finalizeCompilationSession).mockImplementation(async (_p, _s, version) => {
      stored = { ...stored!, status: 'GENERATED', version: version + 1, last_generation: {
        id: 'run-1', project_id: 'alpha', template_name: form.name, created_at: '', status: 'needs_review',
        session_version: version, downloads: { docx: '/file', report: '/report', template: '/original' },
      } }
      return structuredClone(stored)
    })
    vi.mocked(api.downloadCompilation).mockResolvedValue(new Blob(['docx']))
  })
  afterEach(() => {
    cleanup(); vi.useRealTimers(); vi.unstubAllGlobals(); vi.restoreAllMocks()
    if (originalScrollTo) Object.defineProperty(HTMLElement.prototype, 'scrollTo', originalScrollTo)
    else Reflect.deleteProperty(HTMLElement.prototype, 'scrollTo')
  })

  it('mostra solo i moduli del progetto e seleziona una mention strutturata anche da tastiera', async () => {
    await setup()
    const input = screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
    fireEvent.change(input, { target: { value: '@' } })
    expect(screen.getAllByRole('option')).toHaveLength(2)
    expect(screen.queryByRole('option', { name: 'fonte.txt' })).not.toBeInTheDocument()
    expect(screen.queryByRole('option', { name: 'privato-beta.docx' })).not.toBeInTheDocument()
    fireEvent.keyDown(input, { key: 'ArrowDown' })
    fireEvent.keyDown(input, { key: 'Enter' })
    expect(screen.getByText('@istruzioni.txt')).toBeInTheDocument()
    expect(input).toHaveValue('')
    expect(screen.queryByRole('button', { name: 'Avvia compilazione' })).not.toBeInTheDocument()
    expect(api.startCompilationSession).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Rimuovi riferimento al modulo' }))
    selectForm()
    expect(screen.getByText('@domanda.docx')).toBeInTheDocument()
  })

  it('una domanda con mention usa la chat normale, senza creare una sessione', async () => {
    vi.mocked(api.projectAnswer).mockResolvedValue({ conversation_id: 'chat-1', turn_id: 1,
      question: 'riassumilo', answer: 'Requisiti del modulo', citations: [], evidence: [],
      missing_information: [], generation_status: 'completed', model: 'test', total_tokens: 1,
      notice: null, form_reference: reference } as GroundedAnswer)
    await setup()
    selectForm()
    submit('riassumilo')
    await screen.findByText('Requisiti del modulo')
    expect(api.projectAnswer).toHaveBeenCalledWith('alpha', 'riassumilo', null, expect.any(AbortSignal), 10, undefined)
    expect(api.startCompilationSession).not.toHaveBeenCalled()
  })

  it('avvia, analizza, chiarisce un field USER, riprende e genera il download nella chat', async () => {
    const view = await setup()
    await start()
    expect(api.startCompilationSession).toHaveBeenCalledWith('alpha', 10, null, expect.any(AbortSignal))
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
    fireEvent.click(await screen.findByText('Dettagli compilazione'))
    fireEvent.click(await screen.findByRole('button', { name: 'Continua analisi' }))
    await screen.findByText('In attesa di informazioni')
    expect(api.resolveCompilationSession).toHaveBeenCalledWith('alpha', 'session-1', 1, undefined, expect.any(AbortSignal))
    expect(screen.getByText('Informazioni da chiarire (1)')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Genera DOCX' })).not.toBeInTheDocument()
    fireEvent.click(await screen.findByText('Informazioni da chiarire (1)'))
    fireEvent.click(screen.getByRole('button', { name: 'Chiarisci Data abilitazione' }))
    fireEvent.change(screen.getByRole('textbox', { name: 'Valore fornito dall’utente' }), { target: { value: '12/06/2010' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salva valore' }))
    await screen.findByText('Pronta per la generazione')
    expect(api.updateCompilationFields).toHaveBeenCalledWith('alpha', 'session-1', 3,
      [{ field_id: 't0:r1:c1', action: 'set', value: '12/06/2010' }], expect.any(AbortSignal))
    expect(stored!.fields[0].status).toBe('RESOLVED')
    // A fresh React tree recovers the backend state, including the mention and USER value.
    view.unmount()
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Pronta per la generazione')
    expect(screen.getByText('@domanda.docx')).toBeInTheDocument()
    fireEvent.click(screen.getByText('Dettagli compilazione'))
    fireEvent.click(await screen.findByText('Valori e sezioni già valutati (2)'))
    expect(screen.getByText('12/06/2010')).toBeInTheDocument()
    expect(screen.getByText('USER · Indicazione dell’utente, non verificata da una fonte.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Correggi Denominazione' }).parentElement).toHaveTextContent('Verificato da fonte')
    fireEvent.click(screen.getByRole('button', { name: 'Genera DOCX' }))
    await screen.findByRole('button', { name: 'Scarica DOCX' })
    expect(api.finalizeCompilationSession).toHaveBeenCalledWith('alpha', 'session-1', 4, false, expect.any(AbortSignal))
    vi.stubGlobal('URL', { createObjectURL: vi.fn(() => 'blob:docx'), revokeObjectURL: vi.fn() })
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
    fireEvent.click(screen.getByRole('button', { name: 'Scarica DOCX' }))
    await waitFor(() => expect(api.downloadCompilation).toHaveBeenCalledWith('alpha', 'run-1', 'docx', expect.any(AbortSignal)))
  })

  it('riprende una sessione esistente e mostra tutti i conteggi del backend', async () => {
    const statuses = ['PENDING', 'RESOLVED', 'MISSING', 'AMBIGUOUS', 'CONFLICTING', 'NOT_APPLICABLE', 'USER_PROVIDED'] as const
    stored = session(statuses.map((s, i) => field(`f${i}`, `Campo ${i}`, s)), 'WAITING_FOR_USER', 8)
    await setup('/projects/alpha/conversations/chat-1')
    const card = await screen.findByRole('region', { name: 'Compilazione domanda.docx' })
    fireEvent.click(screen.getByText('Dettagli compilazione'))
    await waitFor(() => expect(card.querySelectorAll('dd')).toHaveLength(8))
    const definitions = card.querySelectorAll('dd')
    expect(Array.from(definitions).map((d) => d.textContent)).toEqual(['7', '1', '1', '1', '1', '1', '1', '1'])
    fireEvent.click(screen.getByRole('button', { name: 'Riprendi compilazione' }))
    await waitFor(() => expect(api.startCompilationSession).toHaveBeenCalledWith('alpha', 10, 'chat-1', expect.any(AbortSignal)))
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
  })

  it('una sessione legacy non avanza senza avvio esplicito e la bozza incompleta resta nei dettagli', async () => {
    stored = session()
    vi.mocked(api.resolveCompilationSession).mockImplementation(async () => {
      stored = session([field('f1', 'Uno', 'RESOLVED'), field('f2', 'Due')], 'CREATED', 3)
      return stored
    })
    await setup('/projects/alpha/conversations/chat-1')
    fireEvent.click(await screen.findByText('Dettagli compilazione'))
    fireEvent.click(await screen.findByRole('button', { name: 'Continua analisi' }))
    await waitFor(() => expect(screen.getByRole('button', { name: 'Continua analisi' })).toBeEnabled())
    expect(api.resolveCompilationSession).toHaveBeenCalledTimes(1)
    expect(api.finalizeCompilationSession).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Genera bozza con campi irrisolti' }))
    await waitFor(() => expect(api.finalizeCompilationSession).toHaveBeenCalledWith('alpha', 'session-1', 3, true, expect.any(AbortSignal)))
  })

  it('ignora una creazione tardiva dopo il cambio di progetto', async () => {
    let complete!: (s: CompilationSession) => void
    vi.mocked(api.startCompilationSession).mockReturnValue(new Promise((resolve) => { complete = resolve }))
    await setup()
    selectForm()
    fireEvent.click(screen.getByRole('button', { name: 'Avvia compilazione' }))
    fireEvent.click(screen.getByRole('link', { name: 'Vai a Beta' }))
    await screen.findByRole('heading', { name: 'beta' })
    await act(async () => complete(session()))
    expect(screen.queryByRole('region', { name: 'Compilazione domanda.docx' })).not.toBeInTheDocument()
    expect(screen.queryByText('@domanda.docx')).not.toBeInTheDocument()
    fireEvent.change(screen.getByRole('textbox'), { target: { value: '@' } })
    expect(screen.getAllByRole('option')).toHaveLength(1)
    expect(screen.getByRole('option', { name: 'privato-beta.docx' })).toBeInTheDocument()
  })

  it('su conflitto di versione rilegge lo stato senza ripetere la mutazione', async () => {
    stored = session()
    vi.mocked(api.resolveCompilationSession).mockImplementation(async () => {
      stored = session([field('f1', 'A', 'RESOLVED')], 'READY', 5)
      throw new Error('Versione non aggiornata')
    })
    await setup('/projects/alpha/conversations/chat-1')
    fireEvent.click(await screen.findByText('Dettagli compilazione'))
    fireEvent.click(await screen.findByRole('button', { name: 'Continua analisi' }))
    await screen.findByText('Ho conservato i dati già verificati. Non ho completato questa operazione. Puoi aggiornare lo stato e riprovare.')
    expect(screen.queryByText('Versione non aggiornata')).not.toBeInTheDocument()
    expect(screen.getByText('Pronta per la generazione')).toBeInTheDocument()
    expect(api.resolveCompilationSession).toHaveBeenCalledTimes(1)
  })

  it('una sessione ANALYZING riaperta aggiorna solo lo stato, senza avviare nuovi step', async () => {
    stored = { ...session(), status: 'ANALYZING', lease_until: new Date(Date.now() + 240000).toISOString() }
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Analisi in corso')
    fireEvent.click(screen.getByText('Dettagli compilazione'))
    expect(await screen.findByRole('button', { name: 'Continua analisi' })).toBeDisabled()
    vi.useFakeTimers()
    // Install the read-only polling timer under the fake clock while still ANALYZING.
    await act(async () => fireEvent.click(screen.getByRole('button', { name: 'Aggiorna stato' })))
    expect(screen.getByText('Analisi in corso')).toBeInTheDocument()
    const readsBeforePoll = vi.mocked(api.compilationSession).mock.calls.length
    stored = session([field('f1', 'Denominazione', 'RESOLVED')], 'READY', 3)
    await act(async () => { await vi.advanceTimersByTimeAsync(3000) })
    expect(screen.getByText('Pronta per la generazione')).toBeInTheDocument()
    expect(api.compilationSession).toHaveBeenCalledTimes(readsBeforePoll + 1)
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
  })

  it('ignora anche un risultato di analisi tardivo dopo il cambio di progetto', async () => {
    stored = session()
    let complete!: (s: CompilationSession) => void
    vi.mocked(api.resolveCompilationSession).mockReturnValue(new Promise((resolve) => { complete = resolve }))
    await setup('/projects/alpha/conversations/chat-1')
    fireEvent.click(await screen.findByText('Dettagli compilazione'))
    fireEvent.click(await screen.findByRole('button', { name: 'Continua analisi' }))
    fireEvent.click(screen.getByRole('link', { name: 'Vai a Beta' }))
    await screen.findByRole('heading', { name: 'beta' })
    await act(async () => complete(session([field('f1', 'Dato privato', 'RESOLVED')], 'READY', 3)))
    expect(screen.queryByText('Dato privato')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Genera DOCX' })).not.toBeInTheDocument()
  })

  it('conserva il valore digitato se la validazione backend lo rifiuta', async () => {
    stored = session([field('f1', 'PEC', 'MISSING')], 'WAITING_FOR_USER', 3)
    vi.mocked(api.updateCompilationFields).mockRejectedValue(new Error('Email non valida'))
    await setup('/projects/alpha/conversations/chat-1')
    fireEvent.click(await screen.findByText('Dettagli compilazione'))
    fireEvent.click(await screen.findByText('Informazioni da chiarire (1)'))
    fireEvent.click(screen.getByRole('button', { name: 'Chiarisci PEC' }))
    fireEvent.change(screen.getByRole('textbox', { name: 'Valore fornito dall’utente' }), { target: { value: 'non-una-email' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salva valore' }))
    await screen.findByText('Ho conservato i dati già verificati. Non ho completato questa operazione. Puoi aggiornare lo stato e riprovare.')
    expect(screen.getByRole('textbox', { name: 'Valore fornito dall’utente' })).toHaveValue('non-una-email')
    expect(screen.getByText('In attesa di informazioni')).toBeInTheDocument()
    expect(api.updateCompilationFields).toHaveBeenCalledTimes(1)
  })

  it('conserva conteggi e bozza parziale dopo un errore senza esporre eccezioni tecniche', async () => {
    stored = conversational(session([field('f1', 'Denominazione', 'RESOLVED'), field('f2', 'Altro')], 'CREATED', 5), true)
    stored.last_error = 'Traceback: sqlite3.OperationalError: database is locked'
    stored.chat!.notice = 'Ho conservato i dati già verificati. Puoi continuare o esportare una bozza parziale.'
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText(stored.chat!.notice)
    expect(screen.queryByText(/Traceback|OperationalError|database is locked/)).not.toBeInTheDocument()
    expect(screen.getByText(/Ho verificato 1 informazione nelle fonti/)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Genera DOCX' })).not.toBeInTheDocument()
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
    fireEvent.click(screen.getByText('Dettagli compilazione'))
    fireEvent.click(await screen.findByRole('button', { name: 'Genera bozza con campi irrisolti' }))
    await waitFor(() => expect(api.finalizeCompilationSession).toHaveBeenCalledWith('alpha', 'session-1', 5, true, expect.any(AbortSignal)))
  })

  it('me lo compili avvia il workflow senza risposta RAG, avanza da solo e riceve la data in chat', async () => {
    vi.mocked(api.projectAnswer).mockImplementation(async (_p, question, _c, _signal, formId, context) => {
      const creating = !stored
      if (creating) stored = conversational(session())
      else {
        expect(context).toEqual({ session_id: stored!.id, version: stored!.version })
        const fields = stored!.fields.map((f) => f.status === 'MISSING'
          ? { ...f, status: 'USER_PROVIDED' as const, value: '12/06/2014', provenance: 'USER' as const } : f)
        stored = conversational(session(fields, 'READY', stored!.version + 1))
      }
      expect(formId).toBe(10)
      return { conversation_id: 'chat-1', turn_id: creating ? 1 : 2, question,
        answer: creating ? 'Certo. Analizzo il modulo e verifico le informazioni disponibili.' : 'Ho registrato la tua indicazione.',
        compilation: { session_id: 'session-1', action: creating ? 'start' : 'updated' },
        generation_status: 'direct', citations: [], evidence: [], missing_information: [],
        notice: null, model: 'simulato', total_tokens: 1, form_reference: reference }
    })
    vi.mocked(api.resolveCompilationSession).mockImplementation(async () => {
      stored = conversational(session([field('t0:r0:c1', 'Denominazione', 'RESOLVED'),
        field('t0:r1:c1', 'Data abilitazione', 'MISSING')], 'WAITING_FOR_USER', 3))
      return structuredClone(stored)
    })
    const view = await setup()
    selectForm()
    submit('me lo compili?')
    await screen.findByText('Mi manca Data abilitazione. Qual è?')
    expect(api.startCompilationSession).not.toHaveBeenCalled() // Routed by the answer backend.
    expect(api.resolveCompilationSession).toHaveBeenCalledWith('alpha', 'session-1', 1,
      undefined, expect.any(AbortSignal), true)
    expect(screen.queryByRole('button', { name: 'Continua analisi' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Chiarisci Data abilitazione' })).not.toBeInTheDocument()
    expect(api.finalizeCompilationSession).not.toHaveBeenCalled()
    submit('12 giugno 2014')
    await screen.findByText('Vuoi che generi il DOCX?')
    expect(stored!.fields[0].provenance).toBe('SOURCE')
    expect(stored!.fields[1].provenance).toBe('USER')
    expect(api.updateCompilationFields).not.toHaveBeenCalled() // Free reply uses the normal chat endpoint.
    view.unmount()
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Vuoi che generi il DOCX?')
    expect(api.finalizeCompilationSession).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Genera DOCX' }))
    await screen.findByRole('button', { name: 'Scarica DOCX' })
    expect(api.finalizeCompilationSession).toHaveBeenCalledWith('alpha', 'session-1', 4, false, expect.any(AbortSignal))
  })

  it('avanza più batch automaticamente, si ferma al budget persistito e non genera una bozza', async () => {
    stored = conversational(session())
    let step = 0
    vi.mocked(api.resolveCompilationSession).mockImplementation(async () => {
      step++
      stored = conversational(session(undefined, 'CREATED', 1 + step * 2), step === 3)
      return structuredClone(stored)
    })
    const view = await setup('/projects/alpha/conversations/chat-1')
    await screen.findByRole('button', { name: 'Prosegui compilazione' })
    expect(api.resolveCompilationSession).toHaveBeenCalledTimes(3)
    expect(screen.queryByRole('button', { name: 'Genera DOCX' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Genera bozza con campi irrisolti' })).not.toBeInTheDocument()
    expect(api.finalizeCompilationSession).not.toHaveBeenCalled()
    view.unmount()
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByRole('button', { name: 'Prosegui compilazione' })
    expect(api.resolveCompilationSession).toHaveBeenCalledTimes(3)
  })

  it('una risposta ambigua chiede chiarimento senza aggiornamenti e resta riprendibile', async () => {
    stored = conversational(session([field('f1', 'Sede', 'AMBIGUOUS')], 'WAITING_FOR_USER', 3))
    vi.mocked(api.projectAnswer).mockImplementation(async (_p, question) => {
      stored = { ...stored!, version: 4, chat: { ...stored!.chat!, question: {
        kind: 'value', field_ids: ['f1'], message: 'Non ho modificato i valori. Quale sede vuoi usare?',
      } } }
      return { conversation_id: 'chat-1', turn_id: 1, question, answer: 'Mi serve una scelta univoca.',
        compilation: { session_id: 'session-1', action: 'clarify' }, generation_status: 'direct',
        citations: [], evidence: [], missing_information: [], notice: null, model: null, total_tokens: null }
    })
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Mi manca Sede. Qual è?')
    const before = structuredClone(stored!.fields)
    submit('Una delle due sedi')
    await screen.findByText('Non ho modificato i valori. Quale sede vuoi usare?')
    expect(stored!.fields).toEqual(before)
    expect(api.updateCompilationFields).not.toHaveBeenCalled()
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
  })

  it.each(['salta', 'non lo so'])('%s passa alla prossima domanda senza inventare valori', async (text) => {
    stored = conversational(session([field('f1', 'Estremi procura', 'MISSING'),
      field('f2', 'Data abilitazione', 'MISSING')], 'WAITING_FOR_USER', 3))
    vi.mocked(api.projectAnswer).mockImplementation(async (_p, question, _c, _signal, _form, context) => {
      expect(context).toEqual({ session_id: 'session-1', version: 3 })
      stored = { ...stored!, version: 4, chat: { ...stored!.chat!, deferred: 1,
        question: { kind: 'value', field_ids: ['f2'], message: 'Qual è la data di abilitazione?' } } }
      return { conversation_id: 'chat-1', turn_id: 1, question, answer: 'La lascio aperta e continuo.',
        compilation: { session_id: 'session-1', action: 'deferred' }, generation_status: 'direct',
        citations: [], evidence: [], missing_information: [], notice: null, model: null, total_tokens: null }
    })
    const view = await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Mi manca Estremi procura. Qual è?')
    const before = structuredClone(stored!.fields)
    submit(text)
    await screen.findByText('Qual è la data di abilitazione?')
    expect(screen.queryByText('Mi manca Estremi procura. Qual è?')).not.toBeInTheDocument()
    expect(stored!.fields).toEqual(before)
    expect(api.updateCompilationFields).not.toHaveBeenCalled()
    view.unmount()
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Qual è la data di abilitazione?')
  })

  it('basta mette in pausa, nasconde la domanda anche dopo refresh e riprendi usa la stessa sessione', async () => {
    stored = conversational(session([field('f1', 'Estremi procura', 'MISSING')], 'WAITING_FOR_USER', 3))
    const originalQuestion = stored.chat!.question
    vi.mocked(api.projectAnswer).mockImplementation(async (_p, question) => {
      const pausing = question === 'basta'
      stored = { ...stored!, version: stored!.version + 1, chat: { ...stored!.chat!,
        paused: pausing, paused_by_user: pausing, question: pausing ? null : originalQuestion } }
      return { conversation_id: 'chat-1', turn_id: stored.version, question,
        answer: pausing ? 'Va bene, metto in pausa la compilazione.' : 'Riprendo la stessa compilazione.',
        compilation: { session_id: 'session-1', action: pausing ? 'paused' : 'resumed' },
        generation_status: 'direct', citations: [], evidence: [], missing_information: [],
        notice: null, model: null, total_tokens: null }
    })
    let view = await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Mi manca Estremi procura. Qual è?')
    submit('basta')
    await screen.findByText('La compilazione è in pausa. Potrai riprenderla quando vuoi.')
    expect(screen.queryByText('Mi manca Estremi procura. Qual è?')).not.toBeInTheDocument()
    expect(screen.queryByText(/Rispondimi qui nella chat/)).not.toBeInTheDocument()
    view.unmount()
    view = await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('La compilazione è in pausa. Potrai riprenderla quando vuoi.')
    expect(screen.queryByText('Mi manca Estremi procura. Qual è?')).not.toBeInTheDocument()
    submit('riprendi')
    await screen.findByText('Mi manca Estremi procura. Qual è?')
    expect(api.startCompilationSession).not.toHaveBeenCalled()
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
    view.unmount()
  })

  it('una negazione della condizione esclude il solo campo chiesto e passa oltre', async () => {
    stored = conversational(session([field('f1', 'Estremi procura', 'AMBIGUOUS'),
      field('f2', 'Data abilitazione', 'MISSING')], 'WAITING_FOR_USER', 3))
    stored.chat!.question = { kind: 'applicability', field_ids: ['f1'],
      message: 'Il sottoscrittore agisce come procuratore?' }
    vi.mocked(api.projectAnswer).mockImplementation(async (_p, question) => {
      const fields = stored!.fields.map((f) => f.id === 'f1'
        ? { ...f, status: 'NOT_APPLICABLE' as const, provenance: 'USER' as const,
          reason: 'Indicazione USER: non sono procuratore' } : f)
      stored = conversational(session(fields, 'WAITING_FOR_USER', 4))
      return { conversation_id: 'chat-1', turn_id: 1, question,
        answer: 'Questa voce non è applicabile. Continuo con il resto.',
        compilation: { session_id: 'session-1', action: 'updated' }, generation_status: 'direct',
        citations: [], evidence: [], missing_information: [], notice: null, model: null, total_tokens: null }
    })
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Il sottoscrittore agisce come procuratore?')
    submit('non sono procuratore')
    await screen.findByText('Mi manca Data abilitazione. Qual è?')
    expect(screen.queryByText('Il sottoscrittore agisce come procuratore?')).not.toBeInTheDocument()
    expect(stored!.fields[0].status).toBe('NOT_APPLICABLE')
    expect(stored!.fields[0].provenance).toBe('USER')
    expect(stored!.fields[0].value).toBeNull()
    expect(stored!.fields[1].status).toBe('MISSING')
    expect(api.finalizeCompilationSession).not.toHaveBeenCalled()
  })

  it('consente di fermare una analisi in corso dal composer', async () => {
    stored = conversational(session())
    vi.mocked(api.resolveCompilationSession).mockImplementation((_p, _s, _v, _fields, signal) =>
      new Promise((_resolve, reject) => signal?.addEventListener('abort', () => reject(new Error('aborted')))))
    vi.mocked(api.projectAnswer).mockImplementation(async (_p, question) => {
      stored = { ...stored!, version: 3, chat: { ...stored!.chat!, auto_continue: false,
        paused: true, paused_by_user: true, question: null } }
      return { conversation_id: 'chat-1', turn_id: 1, question, answer: 'Metto in pausa.',
        compilation: { session_id: 'session-1', action: 'paused' }, generation_status: 'direct',
        citations: [], evidence: [], missing_information: [], notice: null, model: null, total_tokens: null }
    })
    await setup('/projects/alpha/conversations/chat-1')
    await waitFor(() => expect(api.resolveCompilationSession).toHaveBeenCalledTimes(1))
    fireEvent.change(screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' }), { target: { value: 'basta' } })
    expect(screen.getByRole('button', { name: 'Invia' })).toBeEnabled()
    fireEvent.click(screen.getByRole('button', { name: 'Invia' }))
    await screen.findByText('La compilazione è in pausa. Potrai riprenderla quando vuoi.')
    expect(api.projectAnswer).toHaveBeenCalledTimes(1)
    expect(api.resolveCompilationSession).toHaveBeenCalledTimes(1)
  })

})
