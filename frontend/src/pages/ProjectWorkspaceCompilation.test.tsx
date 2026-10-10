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
function submit(text: string) {
  fireEvent.change(screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' }), { target: { value: text } })
  fireEvent.click(screen.getByRole('button', { name: 'Invia' }))
}

describe('CompilationSession nella chat', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    vi.stubGlobal('URL', { createObjectURL: vi.fn(() => 'blob:docx'), revokeObjectURL: vi.fn() })
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
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

  it('raggruppa fonti e moduli del progetto e seleziona una mention anche da tastiera', async () => {
    await setup()
    const input = screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
    fireEvent.change(input, { target: { value: '@' } })
    expect(screen.getAllByRole('option')).toHaveLength(3)
    expect(screen.getByRole('option', { name: 'fonte.txt' })).toBeInTheDocument()
    expect(screen.getByRole('group', { name: 'Bandi e fonti' })).toBeInTheDocument()
    expect(screen.getByRole('group', { name: 'Moduli da compilare' })).toBeInTheDocument()
    expect(screen.queryByRole('option', { name: 'privato-beta.docx' })).not.toBeInTheDocument()
    fireEvent.keyDown(input, { key: 'ArrowDown' })
    fireEvent.keyDown(input, { key: 'Enter' })
    expect(screen.getByText('@istruzioni.txt')).toBeInTheDocument()
    expect(input).toHaveValue('')
    expect(screen.queryByRole('button', { name: 'Avvia compilazione' })).not.toBeInTheDocument()
    expect(api.startCompilationSession).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Rimuovi riferimento al documento' }))
    selectForm()
    expect(screen.getByText('@domanda.docx')).toBeInTheDocument()
  })

  it('il picker aperto con + conserva il messaggio anche dopo la selezione o Escape', async () => {
    await setup()
    const input = screen.getByRole<HTMLTextAreaElement>('textbox', { name: 'Messaggio per Mapi RAG' })
    const draft = 'Puoi spiegarmi quali requisiti richiede questo modulo?'
    fireEvent.change(input, { target: { value: draft } })
    input.setSelectionRange(5, 12)
    fireEvent.click(screen.getByRole('button', { name: 'Aggiungi un documento' }))
    expect(input).toHaveValue(draft)
    fireEvent.keyDown(input, { key: 'Escape' })
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument()
    expect(input).toHaveValue(draft)
    fireEvent.click(screen.getByRole('button', { name: 'Aggiungi un documento' }))
    fireEvent.click(screen.getByRole('option', { name: form.name }))
    expect(screen.getByText('@domanda.docx')).toBeInTheDocument()
    expect(input).toHaveValue(draft)
    expect(api.projectAnswer).not.toHaveBeenCalled()
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

  it('consulta una fonte conservando la compilazione e la sua versione in attesa', async () => {
    stored = conversational(session([field('f1', 'Data abilitazione', 'MISSING')], 'WAITING_FOR_USER', 7))
    const before = structuredClone(stored)
    vi.mocked(api.projectAnswer).mockResolvedValue({ conversation_id: 'chat-1', turn_id: 2,
      question: 'spiegami la fonte', answer: 'La fonte descrive i requisiti del bando.', citations: [], evidence: [],
      missing_information: [], generation_status: 'completed', model: 'test', total_tokens: 1,
      notice: null, document_reference: { document_id: 12, name: 'fonte.txt', role: 'source' } })
    await setup('/projects/alpha/conversations/chat-1')
    await waitFor(() => expect(screen.getByRole('button', { name: 'Aggiungi un documento' })).toBeEnabled())
    selectForm('fonte.txt')
    await waitFor(() => expect(screen.getByRole('button', { name: 'Aggiungi un documento' })).toBeEnabled())
    submit('spiegami la fonte')
    await screen.findByText('La fonte descrive i requisiti del bando.')
    expect(api.projectAnswer).toHaveBeenCalledWith('alpha', 'spiegami la fonte', 'chat-1',
      expect.any(AbortSignal), 12, { session_id: before.id, version: 7 })
    expect(stored).toEqual(before)
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
    expect(api.startCompilationSession).not.toHaveBeenCalled()
    expect(screen.getAllByText('@fonte.txt')).toHaveLength(2)
  })

  it('abilita il picker anche quando il progetto contiene soltanto fonti', async () => {
    const getProject = vi.mocked(api.project).getMockImplementation()!
    vi.mocked(api.project).mockImplementation(async (...args) => {
      const project = await getProject(...args)
      return { ...project, files: project.files.filter((file) => file.kind === 'source') }
    })
    await setup()
    fireEvent.click(screen.getByRole('button', { name: 'Aggiungi un documento' }))
    expect(screen.getAllByRole('option')).toHaveLength(1)
    fireEvent.click(screen.getByRole('option', { name: 'fonte.txt' }))
    expect(screen.getByText('@fonte.txt')).toBeInTheDocument()
    expect(api.startCompilationSession).not.toHaveBeenCalled()
  })

  it('ignora una creazione tardiva dopo il cambio di progetto', async () => {
    let complete!: (answer: GroundedAnswer) => void
    vi.mocked(api.projectAnswer).mockReturnValue(new Promise((resolve) => { complete = resolve }))
    await setup()
    selectForm()
    submit('me lo compili?')
    fireEvent.click(screen.getByRole('link', { name: 'Vai a Beta' }))
    await screen.findByRole('heading', { name: 'beta' })
    await act(async () => complete({ conversation_id: 'chat-1', turn_id: 1, question: 'me lo compili?',
      answer: 'Certo. Analizzo il modulo e verifico le informazioni disponibili.',
      compilation: { session_id: 'session-1', action: 'start' }, generation_status: 'direct',
      citations: [], evidence: [], missing_information: [], notice: null, model: null,
      total_tokens: null, form_reference: reference }))
    expect(screen.queryByText('Mi manca Data abilitazione. Qual è?')).not.toBeInTheDocument()
    expect(screen.queryByText('@domanda.docx')).not.toBeInTheDocument()
    fireEvent.change(screen.getByRole('textbox'), { target: { value: '@' } })
    expect(screen.getAllByRole('option')).toHaveLength(1)
    expect(screen.getByRole('option', { name: 'privato-beta.docx' })).toBeInTheDocument()
  })

  it('una sessione in elaborazione riaperta legge lo stato senza avviare nuovi passi', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
    stored = { ...session(), status: 'ANALYZING', lease_until: new Date(Date.now() + 240000).toISOString() }
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Sto lavorando…')
    const input = screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
    fireEvent.change(input, { target: { value: 'Testo conservato' } })
    expect(screen.getByRole('button', { name: 'Invia' })).toBeDisabled()
    stored = conversational(session([field('f1', 'Denominazione', 'RESOLVED')], 'READY', 3))
    await act(async () => { await vi.advanceTimersByTimeAsync(3000) })
    expect(screen.getByText('Vuoi che generi il DOCX?')).toBeInTheDocument()
    expect(input).toHaveValue('Testo conservato')
    expect(screen.getByRole('button', { name: 'Invia' })).toBeEnabled()
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
  })

  it('ignora un risultato di analisi tardivo dopo il cambio di progetto', async () => {
    stored = conversational(session())
    let complete!: (s: CompilationSession) => void
    vi.mocked(api.resolveCompilationSession).mockReturnValue(new Promise((resolve) => { complete = resolve }))
    await setup('/projects/alpha/conversations/chat-1')
    await waitFor(() => expect(api.resolveCompilationSession).toHaveBeenCalledTimes(1))
    fireEvent.click(screen.getByRole('link', { name: 'Vai a Beta' }))
    await screen.findByRole('heading', { name: 'beta' })
    await act(async () => complete(conversational(session([field('f1', 'Dato privato', 'MISSING')], 'WAITING_FOR_USER', 3))))
    expect(screen.queryByText(/Dato privato/)).not.toBeInTheDocument()
  })

  it('spiega un errore nella risposta senza esporre dettagli interni o perdere i dati', async () => {
    stored = conversational(session([field('f1', 'Denominazione', 'RESOLVED'), field('f2', 'Altro')], 'CREATED', 5), true)
    stored.last_error = 'Traceback: sqlite3.OperationalError: database is locked'
    await setup('/projects/alpha/conversations/chat-1')
    expect(await screen.findByRole('alert')).toHaveTextContent('Ho conservato il lavoro fatto finora')
    expect(screen.queryByText(/Traceback|OperationalError|database is locked/)).not.toBeInTheDocument()
    expect(screen.queryByText(/Ho verificato|Dettagli compilazione|Dati e fonti/)).not.toBeInTheDocument()
    expect(stored.fields[0].value).toBe('Mapi S.r.l.')
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
  })

  it('me lo compili avvia il workflow senza risposta RAG, avanza da solo e riceve la data in chat', async () => {
    vi.mocked(api.projectAnswer).mockImplementation(async (_p, question, _c, _signal, formId, context) => {
      const creating = !stored
      if (creating) stored = conversational(session())
      else if (question === 'sì, genera la bozza') {
        stored = { ...stored!, status: 'GENERATED', version: stored!.version + 1, last_generation: {
          id: 'run-1', project_id: 'alpha', template_name: form.name, created_at: '', status: 'needs_review',
          session_version: stored!.version, downloads: { docx: '/file', report: '/report', template: '/original' },
        }, chat: { ...stored!.chat!, question: null, auto_continue: false } }
      } else {
        expect(context).toEqual({ session_id: stored!.id, version: stored!.version })
        const fields = stored!.fields.map((f) => f.status === 'MISSING'
          ? { ...f, status: 'USER_PROVIDED' as const, value: '12/06/2014', provenance: 'USER' as const } : f)
        stored = conversational(session(fields, 'READY', stored!.version + 1))
      }
      expect(formId).toBe(10)
      return { conversation_id: 'chat-1', turn_id: creating ? 1 : 2, question,
        answer: creating ? 'Certo. Analizzo il modulo e verifico le informazioni disponibili.' : 'Ho registrato la tua indicazione.',
        compilation: { session_id: 'session-1', action: creating ? 'start' : question === 'sì, genera la bozza' ? 'generated' : 'updated' },
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
    submit('sì, genera la bozza')
    fireEvent.click(await screen.findByRole('button', { name: 'Scarica DOCX' }))
    await waitFor(() => expect(api.downloadCompilation).toHaveBeenCalledWith('alpha', 'run-1', 'docx', expect.any(AbortSignal)))
    expect(api.finalizeCompilationSession).not.toHaveBeenCalled()
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
    await screen.findByText('Ho conservato il lavoro fatto finora. Chiedimi di riprendere quando vuoi proseguire.')
    expect(api.resolveCompilationSession).toHaveBeenCalledTimes(3)
    expect(screen.queryByRole('button', { name: 'Genera DOCX' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Genera bozza con campi irrisolti' })).not.toBeInTheDocument()
    expect(api.finalizeCompilationSession).not.toHaveBeenCalled()
    view.unmount()
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Ho conservato il lavoro fatto finora. Chiedimi di riprendere quando vuoi proseguire.')
    expect(api.resolveCompilationSession).toHaveBeenCalledTimes(3)
  })

  it.each(['basta', 'Roma', 'spiegati meglio'])('conserva la domanda precedente durante e dopo «%s»', async (message) => {
    stored = conversational(session([field('f1', 'Sede', 'MISSING')], 'WAITING_FOR_USER', 3))
    const previousQuestion = stored.chat!.question!.message
    vi.mocked(api.conversation).mockResolvedValue({ id: 'chat-1', project_id: 'alpha', title: 'Chat',
      metadata: '', target: 'chat', form_reference: reference, turns: [{ id: 1, question: 'compila',
        answer: 'Certo. Analizzo il modulo e verifico le informazioni disponibili.',
        compilation: { session_id: 'session-1', action: 'start' }, generation_status: 'direct',
        citations: [], evidence: [], missing_information: [], notice: null, model: 'test', total_tokens: 1,
      }] })
    let complete!: (answer: GroundedAnswer) => void
    vi.mocked(api.projectAnswer).mockReturnValue(new Promise((resolve) => { complete = resolve }))
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText(previousQuestion)
    submit(message)
    const previousReply = screen.getAllByRole('region', { name: 'Risposta Mapi' })[0]
    expect(previousReply).toHaveTextContent(previousQuestion)
    expect(previousReply).not.toHaveTextContent('Certo. Analizzo')
    if (message === 'basta') stored.chat = { ...stored.chat!, paused: true, paused_by_user: true, question: null }
    else if (message === 'Roma') stored.chat!.question = { kind: 'generate', field_ids: [], message: 'Vuoi che generi il DOCX?' }
    await act(async () => complete({ conversation_id: 'chat-1', turn_id: 2, question: message,
      answer: 'Risposta successiva.', citations: [], evidence: [], missing_information: [],
      generation_status: 'direct', model: 'test', total_tokens: 1, notice: null,
      compilation: message === 'spiegati meglio' ? null : { session_id: 'session-1',
        action: message === 'basta' ? 'paused' : 'updated' },
    }))
    await screen.findByText('Risposta successiva.')
    expect(previousReply).toHaveTextContent(previousQuestion)
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
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
    await screen.findByText('Va bene, metto in pausa la compilazione.')
    expect(screen.queryByText('Mi manca Estremi procura. Qual è?')).not.toBeInTheDocument()
    expect(screen.queryByText(/Rispondimi qui nella chat/)).not.toBeInTheDocument()
    view.unmount()
    view = await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Va bene, mi fermo qui. Quando vuoi, chiedimi di riprendere.')
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
    const card = screen.getAllByRole('region', { name: 'Risposta Mapi' }).at(-1)!
    expect(card.querySelector('.assistant-activity')).toBeInTheDocument()
    expect(card.querySelector('details')).not.toBeInTheDocument()
    stored = conversational(session([field('f1', 'Data abilitazione', 'MISSING')], 'WAITING_FOR_USER', 3))
    await act(async () => complete(stored!))
    await screen.findByText('Mi manca Data abilitazione. Qual è?')
    expect(screen.getByRole('button', { name: 'Invia' })).toBeEnabled()
    expect(input).toHaveValue('12 giugno 2014')
    expect(card.querySelector('.assistant-activity')).not.toBeInTheDocument()
    expect(api.resolveCompilationSession).toHaveBeenCalledTimes(1)
  })

  it('un doppio invio di avvio crea una sola richiesta e conserva il draft anche nella nuova conversazione', async () => {
    let complete!: (answer: GroundedAnswer) => void
    vi.mocked(api.projectAnswer).mockReturnValue(new Promise((resolve) => { complete = resolve }))
    await setup()
    selectForm()
    const input = screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
    fireEvent.change(input, { target: { value: 'me lo compili?' } })
    fireEvent.click(screen.getByRole('button', { name: 'Invia' }))
    const draftInput = screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
    fireEvent.change(draftInput, { target: { value: 'Testo da conservare durante l’avvio' } })
    fireEvent.submit(draftInput.closest('form')!)
    expect(api.projectAnswer).toHaveBeenCalledTimes(1)
    stored = conversational(session([field('f1', 'Qualifica', 'MISSING')], 'WAITING_FOR_USER', 2))
    await act(async () => complete({ conversation_id: 'chat-1', turn_id: 1, question: 'me lo compili?',
      answer: 'Certo. Analizzo il modulo e verifico le informazioni disponibili.',
      compilation: { session_id: 'session-1', action: 'start' }, generation_status: 'direct',
      citations: [], evidence: [], missing_information: [], notice: null, model: 'simulato',
      total_tokens: 1, form_reference: reference }))
    await screen.findByText('Mi manca Qualifica. Qual è?')
    expect(screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' }))
      .toHaveValue('Testo da conservare durante l’avvio')
    await waitFor(() => expect(screen.getByRole('button', { name: 'Invia' })).toBeEnabled())
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
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
    expect(screen.getAllByRole('region', { name: 'Risposta Mapi' }).at(-1)!.querySelector('.assistant-activity')).toBeInTheDocument()
    await act(async () => complete({ conversation_id: 'chat-1', turn_id: 1,
      question: 'Ingegnere', answer: 'Indicazione ricevuta.', citations: [], evidence: [],
      missing_information: [], generation_status: 'direct', model: null, total_tokens: null, notice: null }))
    expect(screen.getByRole('button', { name: 'Invia' })).toBeEnabled()
    expect(input).toHaveValue('Una seconda annotazione')
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
  })

  it('una pausa recuperabile è una risposta normale senza pannelli o riprese implicite', async () => {
    stored = conversational(session(), true)
    stored.chat!.auto_continue = true
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Ho conservato il lavoro fatto finora. Chiedimi di riprendere quando vuoi proseguire.')
    const reply = screen.getByRole('region', { name: 'Risposta Mapi' })
    expect(reply.querySelector('details, dl, .assistant-activity')).not.toBeInTheDocument()
    expect(within(reply).queryByRole('button')).not.toBeInTheDocument()
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
    await screen.findByText('Ho conservato il lavoro fatto finora. Chiedimi di riprendere quando vuoi proseguire.')
    expect(screen.getAllByRole('region', { name: 'Risposta Mapi' }).at(-1)!.querySelector('.assistant-activity')).not.toBeInTheDocument()
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
    await screen.findByRole('button', { name: 'Scarica DOCX' })
    const card = screen.getAllByRole('region', { name: 'Risposta Mapi' }).at(-1)!
    expect(within(card).getByText(/Ho preparato una bozza parziale/)).toBeInTheDocument()
    expect(within(card).getAllByRole('button')).toHaveLength(1)
    expect(within(card).getByRole('button', { name: 'Scarica DOCX' })).toBeEnabled()
    expect(screen.queryByRole('button', { name: 'Genera DOCX' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Scarica report' })).not.toBeInTheDocument()
    expect(screen.queryByText(/Ho terminato la compilazione/)).not.toBeInTheDocument()
    expect(api.resolveCompilationSession).not.toHaveBeenCalled()
    expect(api.finalizeCompilationSession).not.toHaveBeenCalled()
  })

  it('mostra la domanda una sola volta nella risposta anche dopo refresh', async () => {
    stored = conversational(session([field('f1', 'Recapito', 'MISSING')], 'WAITING_FOR_USER', 5))
    const question = stored.chat!.question!.message
    const answer = `Ho registrato la tua risposta. ${question}`
    vi.mocked(api.conversation).mockResolvedValue({ id: 'chat-1', project_id: 'alpha',
      title: 'Chat', metadata: '', target: 'chat', form_reference: reference, turns: [{
        id: 1, question: 'Il ramo non si applica', answer,
        compilation: { session_id: 'session-1', action: 'updated' }, citations: [], evidence: [],
        missing_information: [], generation_status: 'direct', notice: null, model: null, total_tokens: null,
      }] })
    const view = await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText(answer)
    expect(screen.getAllByRole('heading', { name: 'Risposta Mapi' })).toHaveLength(1)
    expect(screen.queryByText(question, { exact: true })).not.toBeInTheDocument()
    view.unmount()
    await setup('/projects/alpha/conversations/chat-1')
    expect(await screen.findAllByText(answer)).toHaveLength(1)
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

  it('una lettura fallita non sblocca l’elaborazione e riprova soltanto la lettura', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
    stored = { ...session(), status: 'ANALYZING', lease_until: new Date(Date.now() + 240000).toISOString() }
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText('Sto lavorando…')
    const input = screen.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
    fireEvent.change(input, { target: { value: 'Risposta conservata' } })
    vi.mocked(api.compilationSession).mockRejectedValueOnce(new Error('Rete non disponibile'))
    await act(async () => { await vi.advanceTimersByTimeAsync(3000) })
    expect(screen.getByRole('alert')).toHaveTextContent('Impossibile aggiornare la compilazione. I dati sono conservati.')
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


  it('non mostra pannelli o conteggi e risponde a spiegati meglio senza ripetere la domanda', async () => {
    stored = conversational(session([field('f1', 'Qualifica', 'MISSING')], 'WAITING_FOR_USER', 3))
    stored.chat!.notice = '11 campi richiedono revisione per problemi di interpretazione o verifica.'
    const question = stored.chat!.question!.message
    const explanation = 'Mi riferisco alla qualifica professionale con cui partecipi, ad esempio ingegnere o architetto.'
    vi.mocked(api.projectAnswer).mockResolvedValue({ conversation_id: 'chat-1', turn_id: 1,
      question: 'spiegati meglio', answer: explanation, citations: [], evidence: [],
      missing_information: [], generation_status: 'direct', model: 'simulato', total_tokens: 1,
      notice: null, form_reference: reference })
    await setup('/projects/alpha/conversations/chat-1')
    await screen.findByText(question)
    expect(screen.queryByText(stored.chat!.notice)).not.toBeInTheDocument()
    expect(screen.queryByText(/Dettagli compilazione|Dati e fonti|Candidate totali/)).not.toBeInTheDocument()
    submit('spiegati meglio')
    const reply = await screen.findByText(explanation)
    const message = reply.closest('.grounded-answer')! as HTMLElement
    expect(within(message).getAllByRole('heading', { name: 'Risposta Mapi' })).toHaveLength(1)
    expect(message.querySelector('details, dl, .compilation-message')).not.toBeInTheDocument()
    expect(within(message).queryByText(question)).not.toBeInTheDocument()
    expect(stored.version).toBe(3)
    expect(stored.fields[0].value).toBeNull()
    expect(api.updateCompilationFields).not.toHaveBeenCalled()
  })

})
