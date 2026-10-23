import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { Link, MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { GroundedAnswer, ProjectDetail } from '../types'
import { ProjectWorkspacePage } from './ProjectWorkspacePage'

vi.mock('../api', () => ({ api: {
  project: vi.fn(), conversation: vi.fn(), projectAnswer: vi.fn(), compilationSessions: vi.fn(),
} }))
vi.mock('../components/ProjectKnowledgePanel', () => ({ ProjectKnowledgePanel: () => null }))
vi.mock('../components/ProjectModelSelector', () => ({ ProjectModelSelector: () => null }))

function result(status: GroundedAnswer['generation_status'] = 'direct'): GroundedAnswer {
  return { conversation_id: 'c1', turn_id: 1, question: '', answer: 'Risposta del sistema',
    citations: [], missing_information: [], evidence: [], generation_status: status,
    model: 'simulated', total_tokens: 1, notice: null }
}

const input = () => screen.getByRole('textbox', { name: 'Messaggio per l’assistente' })
const long = '  Confermo il ramo societario.\n' + 'Contesto da verificare. '.repeat(120) + '\n  '

async function setup(path = '/projects/alfa/conversations/c1') {
  render(<MemoryRouter initialEntries={[path]}>
    <Link to="/projects/beta/conversations/c1">Altro progetto</Link>
    <Link to="/projects/alfa/conversations/c2">Altra chat</Link>
    <Link to="/projects/alfa/conversations/c1">Chat originale</Link>
    <Routes>
      <Route path="/projects/:projectId" element={<ProjectWorkspacePage />} />
      <Route path="/projects/:projectId/conversations/:conversationId" element={<ProjectWorkspacePage />} />
    </Routes>
  </MemoryRouter>)
  await screen.findByRole('heading', { name: path.includes('beta') ? 'beta' : 'alfa' })
  await waitFor(() => expect(input()).not.toBeDisabled())
}

function type(text: string) { fireEvent.change(input(), { target: { value: text } }) }
function send() { fireEvent.click(screen.getByRole('button', { name: 'Invia' })) }

describe('Conservazione e recupero dei messaggi USER', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    sessionStorage.clear()
    vi.stubGlobal('requestAnimationFrame', () => 1)
    vi.stubGlobal('cancelAnimationFrame', vi.fn())
    vi.mocked(api.compilationSessions).mockResolvedValue([])
    vi.mocked(api.project).mockImplementation(async (id) => ({
      id, title: id, description: 'Prova', status: 'Bozza', status_tone: 'info', updated_label: '',
      source_count: 0, model_count: 0, instructions: '', call_fact_count: 0, missing_fact_count: 0,
      files: [], knowledge_sources: [], conversations: [],
    } as ProjectDetail))
    vi.mocked(api.conversation).mockImplementation(async (_project, id) => ({
      id, title: id, project_id: _project, metadata: '', target: null, turns: [],
    }))
  })
  afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals() })

  it('invia la risposta lunga integralmente, compresi spazi e righe originali', async () => {
    vi.mocked(api.projectAnswer).mockResolvedValue(result())
    await setup(); type(long); send()
    await waitFor(() => expect(api.projectAnswer).toHaveBeenCalled())
    expect(vi.mocked(api.projectAnswer).mock.calls[0][1]).toBe(long)
  })

  it('conserva il testo oltre limite senza troncamento e impedisce l’invio', async () => {
    await setup(); type('a'.repeat(4001))
    expect(input()).toHaveValue('a'.repeat(4001))
    expect(input()).not.toHaveAttribute('maxlength')
    expect(screen.getByRole('alert')).toHaveTextContent('4.000')
    expect(screen.getByRole('button', { name: 'Invia' })).toBeDisabled()
    fireEvent.submit(input().closest('form')!)
    expect(api.projectAnswer).not.toHaveBeenCalled()
    cleanup(); await setup()
    fireEvent.click(screen.getByRole('button', { name: 'Recupera messaggio' }))
    expect(input()).toHaveValue('a'.repeat(4001))
  })

  it.each(['rete', 'schema', 'non configurato'])(
    'rende recuperabile integralmente il messaggio dopo errore %s e reload', async (failure) => {
      if (failure === 'rete') vi.mocked(api.projectAnswer).mockRejectedValue(new Error('Connessione interrotta'))
      else vi.mocked(api.projectAnswer).mockResolvedValue(result(failure === 'schema' ? 'failed' : 'not_configured'))
      await setup(); type(long); send()
      await screen.findByRole('button', { name: 'Recupera messaggio' })
      cleanup(); await setup()
      fireEvent.click(screen.getByRole('button', { name: 'Recupera messaggio' }))
      expect(input()).toHaveValue(long)
      expect(api.projectAnswer).toHaveBeenCalledTimes(1)
    },
  )

  it('conserva una risposta in transito durante l’uscita dalla pagina', async () => {
    vi.mocked(api.projectAnswer).mockReturnValue(new Promise(() => {}))
    await setup(); type(long); send()
    await waitFor(() => expect(api.projectAnswer).toHaveBeenCalledTimes(1))
    cleanup(); await setup()
    fireEvent.click(screen.getByRole('button', { name: 'Recupera messaggio' }))
    expect(input()).toHaveValue(long)
    expect(api.projectAnswer).toHaveBeenCalledTimes(1)
  })

  it('non trasferisce il testo fra progetti o conversazioni', async () => {
    vi.mocked(api.projectAnswer).mockRejectedValue(new Error('Connessione interrotta'))
    await setup(); type(long); send()
    await screen.findByRole('button', { name: 'Recupera messaggio' })
    fireEvent.click(screen.getByRole('link', { name: 'Altra chat' }))
    await waitFor(() => expect(screen.queryByRole('button', { name: 'Recupera messaggio' })).not.toBeInTheDocument())
    expect(input()).toHaveValue('')
    fireEvent.click(screen.getByRole('link', { name: 'Altro progetto' }))
    await screen.findByRole('heading', { name: 'beta' })
    expect(screen.queryByRole('button', { name: 'Recupera messaggio' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('link', { name: 'Chat originale' }))
    await screen.findByRole('heading', { name: 'alfa' })
    fireEvent.click(await screen.findByRole('button', { name: 'Recupera messaggio' }))
    expect(input()).toHaveValue(long)
  })

  it('rimuove la copia di recupero soltanto dopo una risposta acquisita', async () => {
    vi.mocked(api.projectAnswer).mockResolvedValue(result())
    await setup(); type(long); send()
    await screen.findByText('Risposta del sistema')
    cleanup(); await setup()
    expect(screen.queryByRole('button', { name: 'Recupera messaggio' })).not.toBeInTheDocument()
    expect(input()).toHaveValue('')
  })

  it('distingue caratteri Unicode da unità UTF16 come il backend', async () => {
    vi.mocked(api.projectAnswer).mockResolvedValue(result())
    const text = '😀'.repeat(2001)
    await setup(); type(text)
    expect(screen.getByRole('button', { name: 'Invia' })).not.toBeDisabled()
    send()
    await waitFor(() => expect(api.projectAnswer).toHaveBeenCalled())
    expect(vi.mocked(api.projectAnswer).mock.calls[0][1]).toBe(text)
  })

  it('non cancella una nuova bozza digitata mentre arriva la risposta precedente', async () => {
    let resolve!: (value: GroundedAnswer) => void
    vi.mocked(api.projectAnswer).mockReturnValue(new Promise((done) => { resolve = done }))
    await setup(); type(long); send()
    type('Messaggio successivo ancora da inviare')
    await act(async () => resolve(result()))
    expect(input()).toHaveValue('Messaggio successivo ancora da inviare')
  })

  it('rende recuperabile anche il messaggio conservato dal server senza copia locale', async () => {
    vi.mocked(api.conversation).mockResolvedValue({
      id: 'c1', title: 'c1', project_id: 'alfa', metadata: '', target: null,
      turns: [{ ...result('failed'), id: 1, question: long, answer: 'Interpretazione non riuscita' }],
    })
    await setup()
    fireEvent.click(await screen.findByRole('button', { name: 'Riutilizza messaggio' }))
    expect(input()).toHaveValue(long)
    expect(api.projectAnswer).not.toHaveBeenCalled()
  })

  it('trasferisce la copia fallita solo nella conversazione appena creata', async () => {
    vi.mocked(api.projectAnswer).mockResolvedValue(result('failed'))
    await setup('/projects/alfa'); type(long); send()
    await screen.findByRole('button', { name: 'Recupera messaggio' })
    cleanup(); await setup()
    fireEvent.click(screen.getByRole('button', { name: 'Recupera messaggio' }))
    expect(input()).toHaveValue(long)
    cleanup(); await setup('/projects/alfa')
    expect(screen.queryByRole('button', { name: 'Recupera messaggio' })).not.toBeInTheDocument()
  })

  it('conserva la nuova bozza anche durante la creazione della conversazione', async () => {
    let resolve!: (value: GroundedAnswer) => void
    vi.mocked(api.projectAnswer).mockReturnValue(new Promise((done) => { resolve = done }))
    await setup('/projects/alfa'); type(long); send()
    type('Nuova bozza durante avvio')
    await act(async () => resolve(result()))
    cleanup(); await setup()
    fireEvent.click(screen.getByRole('button', { name: 'Recupera messaggio' }))
    expect(input()).toHaveValue('Nuova bozza durante avvio')
  })

  it('avverte quando lo storage non funziona e consente il recupero in memoria', async () => {
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new DOMException('Quota') })
    vi.mocked(api.projectAnswer).mockRejectedValue(new Error('Connessione interrotta'))
    await setup(); type(long); send()
    expect(await screen.findByRole('alert')).toHaveTextContent('Copia il messaggio prima di uscire')
    fireEvent.click(await screen.findByRole('button', { name: 'Recupera messaggio' }))
    expect(input()).toHaveValue(long)
  })
})
