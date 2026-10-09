import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
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
    fireEvent.click(screen.getByRole('button', { name: 'Prosegui compilazione' }))
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
    expect(screen.getByText('Compilazione in pausa')).toBeInTheDocument()
    expect(api.resolveCompilationSession).toHaveBeenCalledTimes(1)
  })

  it('una sessione ANALYZING riaperta aggiorna solo lo stato, senza avviare nuovi step', async () => {
    stored = { ...session(), status: 'ANALYZING', lease_until: new Date(Date.now() + 240000).toISOString() }
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Elaborazione in corso')
    const input = screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
    fireEvent.change(input, { target: { value: 'Testo scritto dopo il refresh' } })
    expect(screen.getByRole('button', { name: 'Invia' })).toBeDisabled()
    expect(screen.getByRole('region', { name: 'Compilazione domanda.docx' }).querySelector('.compilation-debug')).not.toHaveAttribute('open')
    fireEvent.click(screen.getByText('Dettagli compilazione'))
    expect(await screen.findByRole('button', { name: 'Continua analisi' })).toBeDisabled()
    vi.useFakeTimers()
    // Install the read-only polling timer under the fake clock while still ANALYZING.
    await act(async () => fireEvent.click(screen.getByRole('button', { name: 'Aggiorna stato' })))
    expect(screen.getByText('Elaborazione in corso')).toBeInTheDocument()
    const readsBeforePoll = vi.mocked(api.compilationSession).mock.calls.length
    stored = session([field('f1', 'Denominazione', 'RESOLVED')], 'READY', 3)
    await act(async () => { await vi.advanceTimersByTimeAsync(3000) })
    expect(screen.getByText('Pronta per la generazione')).toBeInTheDocument()
    expect(input).toHaveValue('Testo scritto dopo il refresh')
    expect(screen.getByRole('button', { name: 'Invia' })).toBeEnabled()
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
    expect(screen.getByText('Compilazione in pausa')).toBeInTheDocument()
    expect(api.updateCompilationFields).toHaveBeenCalledTimes(1)
    vi.mocked(api.compilationSessions).mockRejectedValueOnce(new Error('Lettura non disponibile'))
    fireEvent.click(screen.getByRole('button', { name: 'Aggiorna stato' }))
    await screen.findByText('Non riesco a caricare la compilazione. Riprova.')
    expect(screen.getByRole('textbox', { name: 'Valore fornito dall’utente' })).toHaveValue('non-una-email')
    fireEvent.click(screen.getByRole('button', { name: 'Aggiorna stato' }))
    await screen.findByText('In attesa di informazioni')
    expect(screen.getByRole('textbox', { name: 'Valore fornito dall’utente' })).toHaveValue('non-una-email')
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

  it('blocca Invia e Invio durante l’analisi, conserva il draft e lo riabilita al chiarimento USER', async () => {
    stored = conversational(session())
    let complete!: (s: CompilationSession) => void
    vi.mocked(api.resolveCompilationSession).mockReturnValue(new Promise((resolve) => { complete = resolve }))
    await setup('/projects/alpha/conversations/chat-1')
    await waitFor(() => expect(api.resolveCompilationSession).toHaveBeenCalledTimes(1))
    const input = screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
    fireEvent.change(input, { target: { value: '12 giugno 2014' } })
    expect(input).toBeEnabled()
    expect(screen.getByRole('button', { name: 'Invia' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Invia' }))
    fireEvent.keyDown(input, { key: 'Enter' })
    fireEvent.submit(input.closest('form')!)
    expect(api.projectAnswer).not.toHaveBeenCalled()
    expect(input).toHaveValue('12 giugno 2014')
    const card = screen.getByRole('region', { name: 'Compilazione domanda.docx' })
    expect(card.querySelector('.compilation-activity')).toBeInTheDocument()
    expect(card.querySelector('.compilation-debug')).not.toHaveAttribute('open')
    stored = conversational(session([field('f1', 'Data abilitazione', 'MISSING')], 'WAITING_FOR_USER', 3))
    await act(async () => complete(stored!))
    await screen.findByText('Mi manca Data abilitazione. Qual è?')
    expect(screen.getByRole('button', { name: 'Invia' })).toBeEnabled()
    expect(input).toHaveValue('12 giugno 2014')
    expect(card.querySelector('.compilation-activity')).not.toBeInTheDocument()
    expect(api.resolveCompilationSession).toHaveBeenCalledTimes(1)
  })

  it('un doppio avvio crea una sola richiesta e conserva il draft anche nella nuova conversazione', async () => {
    let complete!: (s: CompilationSession) => void
    vi.mocked(api.startCompilationSession).mockReturnValue(new Promise((resolve) => { complete = resolve }))
    await setup()
    selectForm()
    const startButton = screen.getByRole('button', { name: 'Avvia compilazione' })
    fireEvent.click(startButton)
    fireEvent.click(startButton)
    const input = screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
    fireEvent.change(input, { target: { value: 'Testo da conservare durante l’avvio' } })
    fireEvent.submit(input.closest('form')!)
    expect(api.startCompilationSession).toHaveBeenCalledTimes(1)
    expect(api.projectAnswer).not.toHaveBeenCalled()
    stored = conversational(session([field('f1', 'Qualifica', 'MISSING')], 'WAITING_FOR_USER', 2))
    await act(async () => complete(stored!))
    await screen.findByText('Mi manca Qualifica. Qual è?')
    expect(input).toHaveValue('Testo da conservare durante l’avvio')
    expect(screen.getByRole('button', { name: 'Invia' })).toBeEnabled()
    expect(screen.queryByRole('button', { name: 'Avvia compilazione' })).not.toBeInTheDocument()
  })

  it('un doppio invio di chiarimento invia una sola richiesta e conserva il nuovo draft', async () => {
    stored = conversational(session([field('f1', 'Qualifica', 'MISSING')], 'WAITING_FOR_USER', 3))
    let complete!: (answer: GroundedAnswer) => void
    vi.mocked(api.projectAnswer).mockReturnValue(new Promise((resolve) => { complete = resolve }))
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Mi manca Qualifica. Qual è?')
    submit('Ingegnere')
    const input = screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
    fireEvent.change(input, { target: { value: 'Una seconda annotazione' } })
    fireEvent.click(screen.getByRole('button', { name: 'Invia' }))
    fireEvent.keyDown(input, { key: 'Enter' })
    fireEvent.submit(input.closest('form')!)
    expect(api.projectAnswer).toHaveBeenCalledTimes(1)
    expect(screen.getByRole('button', { name: 'Invia' })).toBeDisabled()
    expect(input).toHaveValue('Una seconda annotazione')
    expect(screen.getByRole('region', { name: 'Compilazione domanda.docx' }).querySelector('.compilation-activity')).not.toBeInTheDocument()
    await act(async () => complete({ conversation_id: 'chat-1', turn_id: 1,
      question: 'Ingegnere', answer: 'Indicazione ricevuta.', citations: [], evidence: [],
      missing_information: [], generation_status: 'direct', model: null, total_tokens: null, notice: null }))
    expect(screen.getByRole('button', { name: 'Invia' })).toBeEnabled()
    expect(input).toHaveValue('Una seconda annotazione')
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
  })

  it('una pausa recuperabile ha una sola azione principale, senza animazione né riprese implicite', async () => {
    stored = conversational(session(), true)
    // A pause is authoritative even if a stale snapshot still advertises continuation.
    stored.chat!.auto_continue = true
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Compilazione in pausa')
    const card = screen.getByRole('region', { name: 'Compilazione domanda.docx' })
    expect(card.querySelectorAll('.button--primary')).toHaveLength(1)
    expect(within(card).getByRole('button', { name: 'Prosegui compilazione' })).toBeEnabled()
    expect(screen.queryByRole('button', { name: 'Riprendi compilazione' })).not.toBeInTheDocument()
    expect(card.querySelector('.compilation-activity')).not.toBeInTheDocument()
    expect(card.querySelector('.compilation-debug')).not.toHaveAttribute('open')
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
    fireEvent.change(screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' }), { target: { value: 'riprendi' } })
    expect(screen.getByRole('button', { name: 'Invia' })).toBeEnabled()
  })

  it('una lease scaduta dopo refresh permette una ripresa esplicita senza simulare attività', async () => {
    stored = { ...conversational(session()), status: 'ANALYZING',
      lease_until: new Date(Date.now() - 60000).toISOString() }
    stored.chat!.paused = true
    stored.chat!.auto_continue = false
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByRole('button', { name: 'Prosegui compilazione' })
    expect(screen.getByRole('region', { name: 'Compilazione domanda.docx' }).querySelector('.compilation-activity')).not.toBeInTheDocument()
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
    fireEvent.change(screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' }), { target: { value: 'riprendi' } })
    expect(screen.getByRole('button', { name: 'Invia' })).toBeEnabled()
  })

  it.each([false, true])('dopo refresh la bozza parziale è scaricabile, anche dopo finish=%s', async (finished) => {
    stored = conversational(session([field('f1', 'Qualifica', 'MISSING')], 'GENERATED', 5))
    stored.chat = { ...stored.chat!, paused: finished, paused_by_user: finished,
      finish_requested: finished, question: null }
    stored.last_generation = { id: 'run-1', project_id: 'alpha', template_name: form.name,
      created_at: '', status: 'needs_review', session_version: 4,
      downloads: { docx: '/file', report: '/report', template: '/original' } }
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Bozza disponibile')
    const card = screen.getByRole('region', { name: 'Compilazione domanda.docx' })
    expect(within(card).getByText(/È disponibile una bozza parziale/)).toBeInTheDocument()
    expect(card.querySelectorAll('.button--primary')).toHaveLength(1)
    expect(within(card).getByRole('button', { name: 'Scarica DOCX' })).toBeEnabled()
    expect(screen.queryByRole('button', { name: 'Genera DOCX' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Scarica report' })).not.toBeInTheDocument()
    expect(screen.queryByText(/Ho terminato la compilazione/)).not.toBeInTheDocument()
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
    expect(api.finalizeCompilationSession).not.toHaveBeenCalled()
  })

  it('mostra il chiarimento una sola volta nella chat anche dopo refresh, ma mostra una nuova domanda nella card', async () => {
    stored = conversational(session([field('f1', 'Recapito', 'MISSING')], 'WAITING_FOR_USER', 5))
    const question = stored.chat!.question!.message
    const answer = `Ho registrato la tua risposta. ${question}`
    vi.mocked(api.conversation).mockResolvedValue({ id: 'chat-1', project_id: 'alpha',
      title: 'Chat', metadata: '', target: 'chat', form_reference: reference, turns: [{
        id: 1, question: 'Il ramo non si applica', answer,
        compilation: { session_id: 'session-1', action: 'updated' },
        citations: [], evidence: [], missing_information: [], generation_status: 'direct',
        notice: null, model: null, total_tokens: null,
      }] })
    const view = await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText(/Ho registrato la tua risposta/)
    let card = screen.getByRole('region', { name: 'Compilazione domanda.docx' })
    expect(within(card).queryByText(question)).not.toBeInTheDocument()
    expect(screen.getAllByText((_, el) => el?.tagName === 'P' && el.textContent === answer)).toHaveLength(1)
    view.unmount()
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText(/Ho registrato la tua risposta/)
    card = screen.getByRole('region', { name: 'Compilazione domanda.docx' })
    expect(within(card).queryByText(question)).not.toBeInTheDocument()
    stored.chat!.question = { kind: 'value', field_ids: ['f1'], message: 'Quale recapito devo usare?' }
    stored.version += 1
    fireEvent.click(screen.getByText('Dettagli compilazione'))
    fireEvent.click(await screen.findByRole('button', { name: 'Aggiorna stato' }))
    await waitFor(() => expect(within(card).getByText('Quale recapito devo usare?')).toBeInTheDocument())
  })

  it('attende il ripristino della sessione e conserva il draft quando la prima lettura fallisce', async () => {
    let fail!: (reason: Error) => void
    vi.mocked(api.compilationSessions).mockReturnValue(new Promise((_resolve, reject) => { fail = reject }))
    await setup('/projects/alpha/conversations/chat-1')
    const input = screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
    fireEvent.change(input, { target: { value: 'Una risposta pronta' } })
    expect(screen.getByRole('button', { name: 'Invia' })).toBeDisabled()
    fireEvent.submit(input.closest('form')!)
    expect(api.projectAnswer).not.toHaveBeenCalled()
    await act(async () => fail(new Error('Rete non disponibile')))
    await screen.findByText('Non riesco a caricare la compilazione. Riprova.')
    expect(screen.getByRole('button', { name: 'Invia' })).toBeDisabled()
    fireEvent.submit(input.closest('form')!)
    expect(api.projectAnswer).not.toHaveBeenCalled()
    expect(input).toHaveValue('Una risposta pronta')
    stored = conversational(session([field('f1', 'Qualifica', 'MISSING')], 'WAITING_FOR_USER', 3))
    vi.mocked(api.compilationSessions).mockResolvedValue([stored])
    fireEvent.click(screen.getByRole('button', { name: 'Riprova caricamento sessione' }))
    await screen.findByText('Mi manca Qualifica. Qual è?')
    expect(input).toHaveValue('Una risposta pronta')
    expect(screen.getByRole('button', { name: 'Invia' })).toBeEnabled()
    expect(api.startCompilationSession).not.toHaveBeenCalled()
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
  })

  it('una lettura di polling fallita non sblocca la lease e riprova soltanto la lettura', async () => {
    stored = { ...session(), status: 'ANALYZING', lease_until: new Date(Date.now() + 240000).toISOString() }
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Elaborazione in corso')
    const input = screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
    fireEvent.change(input, { target: { value: 'Risposta conservata' } })
    fireEvent.click(screen.getByText('Dettagli compilazione'))
    await screen.findByRole('button', { name: 'Aggiorna stato' })
    vi.useFakeTimers()
    await act(async () => fireEvent.click(screen.getByRole('button', { name: 'Aggiorna stato' })))
    vi.mocked(api.compilationSession).mockRejectedValueOnce(new Error('Rete non disponibile'))
    await act(async () => { await vi.advanceTimersByTimeAsync(3000) })
    expect(screen.getByText('Impossibile aggiornare la compilazione. I dati sono conservati.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Invia' })).toBeDisabled()
    stored = conversational(session([field('f1', 'Qualifica', 'MISSING')], 'WAITING_FOR_USER', 3))
    await act(async () => { await vi.advanceTimersByTimeAsync(3000) })
    expect(screen.getByText('Mi manca Qualifica. Qual è?')).toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Invia' })).toBeEnabled()
    expect(input).toHaveValue('Risposta conservata')
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
    expect(api.projectAnswer).not.toHaveBeenCalled()
  })

  it.each(['chat', 'analisi'])('blocca richieste incrociate nello stesso tick, iniziando da %s', async (first) => {
    stored = session()
    vi.mocked(api.projectAnswer).mockReturnValue(new Promise(() => {}))
    vi.mocked(api.resolveCompilationSession).mockReturnValue(new Promise(() => {}))
    await setup('/projects/alpha/conversations/chat-1')
    fireEvent.click(await screen.findByText('Dettagli compilazione'))
    const analyze = await screen.findByRole('button', { name: 'Continua analisi' })
    const input = screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
    fireEvent.change(input, { target: { value: 'Messaggio pronto' } })
    const send = () => input.closest('form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))
    // Native events inside one React batch exercise the refs before disabled re-renders.
    act(() => {
      if (first === 'chat') { send(); analyze.click() }
      else { analyze.click(); send() }
    })
    expect(api.projectAnswer).toHaveBeenCalledTimes(first === 'chat' ? 1 : 0)
    expect(api.resolveCompilationSession).toHaveBeenCalledTimes(first === 'analisi' ? 1 : 0)
    if (first === 'analisi') expect(input).toHaveValue('Messaggio pronto')
  })

})
