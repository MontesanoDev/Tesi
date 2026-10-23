import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { Link, MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { GroundedAnswer, ProjectDetail } from '../types'
import { ProjectWorkspacePage } from './ProjectWorkspacePage'

vi.mock('../api', () => ({ api: {
  project: vi.fn(), conversation: vi.fn(), projectAnswer: vi.fn(),
  compilationSessions: vi.fn(),
} }))
vi.mock('../components/ProjectKnowledgePanel', () => ({ ProjectKnowledgePanel: () => null }))
vi.mock('../components/ProjectModelSelector', () => ({ ProjectModelSelector: () => null }))

function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (reason: Error) => void
  const promise = new Promise<T>((res, rej) => { resolve = res; reject = rej })
  return { promise, resolve, reject }
}

function answer(conversation: string, question = 'Prima domanda'): GroundedAnswer {
  return {
    conversation_id: conversation, turn_id: 1, question, answer: 'Risposta precedente',
    citations: [], missing_information: [], evidence: [], generation_status: 'direct',
    model: 'test', total_tokens: 10, notice: null,
  }
}

function Navigation() {
  const location = useLocation()
  return <>
    <Link to="/projects/beta">Vai a Beta</Link>
    <Link to="/projects/alfa/conversations/altra">Altra conversazione</Link>
    <output aria-label="Percorso attuale">{location.pathname}</output>
  </>
}

async function setup() {
  render(<MemoryRouter initialEntries={['/projects/alfa']}>
    <Navigation />
    <Routes>
      <Route path="/projects/:projectId" element={<ProjectWorkspacePage />} />
      <Route path="/projects/:projectId/conversations/:conversationId" element={<ProjectWorkspacePage />} />
    </Routes>
  </MemoryRouter>)
  await screen.findByRole('heading', { name: 'alfa' })
}

function submit(question: string) {
  fireEvent.change(screen.getByRole('textbox', { name: 'Messaggio per l’assistente' }), {
    target: { value: question },
  })
  fireEvent.click(screen.getByRole('button', { name: 'Invia' }))
}

describe('ProjectWorkspacePage pending requests', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    vi.mocked(api.compilationSessions).mockResolvedValue([])
    vi.stubGlobal('requestAnimationFrame', () => 1)
    vi.stubGlobal('cancelAnimationFrame', vi.fn())
    vi.mocked(api.project).mockImplementation(async (id) => ({
      id, title: id, description: 'Progetto di prova', status: 'Bozza', status_tone: 'info',
      updated_label: '', source_count: 0, model_count: 0, instructions: '',
      call_fact_count: 0, missing_fact_count: 0, files: [], knowledge_sources: [], conversations: [],
    } as ProjectDetail))
    vi.mocked(api.conversation).mockResolvedValue({
      id: 'altra', title: 'Altra', metadata: '', target: null, project_id: 'alfa', turns: [],
    })
  })
  afterEach(() => { cleanup(); vi.unstubAllGlobals() })

  it('uses the assistant response and its animation while waiting for a normal RAG answer', async () => {
    const request = deferred<GroundedAnswer>()
    vi.mocked(api.projectAnswer).mockReturnValue(request.promise)
    await setup()
    submit('Prima domanda')
    const reply = screen.getByRole('region', { name: 'Risposta' })
    expect(reply.querySelector('.assistant-activity')).toBeInTheDocument()
    expect(reply.querySelector('details, dl')).not.toBeInTheDocument()
    await act(async () => request.resolve(answer('nuova')))
    expect(await screen.findByText('Risposta precedente')).toBeInTheDocument()
    expect(screen.queryByRole('status', { name: 'Elaborazione in corso' })).not.toBeInTheDocument()
  })

  it('keeps a successful answer and opens its conversation when the user stays', async () => {
    vi.mocked(api.projectAnswer).mockResolvedValue(answer('nuova'))
    await setup()
    submit('Prima domanda')
    await screen.findByText('Risposta precedente')
    await waitFor(() => expect(screen.getByLabelText('Percorso attuale')).toHaveTextContent('/projects/alfa/conversations/nuova'))
  })

  it('shows the role of form evidence and supports legacy source evidence', async () => {
    vi.mocked(api.projectAnswer).mockResolvedValue({
      ...answer('nuova'), generation_status: 'completed', citations: [1],
      evidence: [
        { chunk_id: 1, file_id: 1, source_name: 'domanda.docx', chunk_index: 0,
          excerpt: 'Dichiarazioni richieste', relevance: 1, role: 'form', project_id: 'alfa' },
        { chunk_id: -1, file_id: -1, source_name: 'azienda.txt', chunk_index: 0,
          excerpt: 'Dati documentati', relevance: 1 },
      ],
    })
    await setup()
    submit('Prima domanda')
    await screen.findByText('domanda.docx')
    expect(screen.getByText('Modulo')).toBeInTheDocument()
    expect(screen.getByText('Fonte')).toBeInTheDocument()
  })

  it.each(['form', 'source'] as const)(
    'keeps limitations in the answer without a separate missing-information checklist (%s)',
    async (role) => {
      const text = role === 'form'
        ? 'Il modulo raccoglie i dati del partecipante. Il riepilogo riguarda le parti consultate [1].'
        : 'Non ho trovato nelle fonti la data richiesta [1].'
      vi.mocked(api.projectAnswer).mockResolvedValue({
        ...answer('nuova'), answer: text, generation_status: 'completed', citations: [1],
        missing_information: ['Dichiarazione non recuperata'],
        evidence: [{ chunk_id: 1, file_id: 1, source_name: 'documento.txt', chunk_index: 0,
          excerpt: 'Testo consultato', relevance: 1, role, project_id: 'alfa' }],
      })
      await setup()
      submit('Prima domanda')
      expect(await screen.findByText(text)).toBeInTheDocument()
      expect(screen.queryByText('Informazioni mancanti')).not.toBeInTheDocument()
      expect(screen.queryByText('Dichiarazione non recuperata')).not.toBeInTheDocument()
      expect(screen.getByText('Evidenze recuperate')).toBeInTheDocument()
    },
  )

  it('does not restore the checklist when reopening an existing conversation', async () => {
    vi.mocked(api.conversation).mockResolvedValue({
      id: 'altra', project_id: 'alfa', title: 'Altra', metadata: '', target: null,
      turns: [{ ...answer('altra'), id: 2, answer: 'Riepilogo del modulo conservato [1].',
        missing_information: ['Sezioni non recuperate nel vecchio turno'] }],
    })
    await setup()
    fireEvent.click(screen.getByRole('link', { name: 'Altra conversazione' }))
    expect(await screen.findByText('Riepilogo del modulo conservato [1].')).toBeInTheDocument()
    expect(screen.queryByText('Informazioni mancanti')).not.toBeInTheDocument()
    expect(screen.queryByText('Sezioni non recuperate nel vecchio turno')).not.toBeInTheDocument()
  })

  it.each(['success', 'failure'] as const)(
    'ignores a late %s from another project without releasing the current request', async (outcome) => {
      const old = deferred<GroundedAnswer>()
      const current = deferred<GroundedAnswer>()
      vi.mocked(api.projectAnswer).mockReturnValueOnce(old.promise).mockReturnValueOnce(current.promise)
      await setup()
      submit('Prima domanda')
      fireEvent.click(screen.getByRole('link', { name: 'Vai a Beta' }))
      await screen.findByRole('heading', { name: 'beta' })
      submit('Domanda Beta')
      await act(async () => {
        if (outcome === 'success') old.resolve(answer('vecchia'))
        else old.reject(new Error('Errore del vecchio progetto'))
      })
      expect(screen.getByLabelText('Percorso attuale')).toHaveTextContent('/projects/beta')
      expect(screen.queryByText('Risposta precedente')).not.toBeInTheDocument()
      expect(screen.queryByText('Errore del vecchio progetto')).not.toBeInTheDocument()
      fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Altra domanda Beta' } })
      expect(screen.getByRole('button', { name: 'Invia' })).toBeDisabled()
      await act(async () => current.resolve({ ...answer('beta-chat'), answer: 'Risposta Beta' }))
      await screen.findByText('Risposta Beta')
      await waitFor(() => expect(screen.getByLabelText('Percorso attuale')).toHaveTextContent('/projects/beta/conversations/beta-chat'))
    },
  )

  it('does not reopen the previous conversation after navigation within a project', async () => {
    const old = deferred<GroundedAnswer>()
    vi.mocked(api.projectAnswer).mockReturnValue(old.promise)
    await setup()
    submit('Prima domanda')
    fireEvent.click(screen.getByRole('link', { name: 'Altra conversazione' }))
    await waitFor(() => expect(api.conversation).toHaveBeenCalled())
    await act(async () => old.resolve(answer('vecchia')))
    expect(screen.getByLabelText('Percorso attuale')).toHaveTextContent('/projects/alfa/conversations/altra')
    expect(screen.queryByText('Risposta precedente')).not.toBeInTheDocument()
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Nuova domanda' } })
    expect(screen.getByRole('button', { name: 'Invia' })).toBeEnabled()
  })
})
