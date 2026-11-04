import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { Link, MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { GroundedAnswer, ProjectDetail } from '../types'
import { ProjectWorkspacePage } from './ProjectWorkspacePage'

vi.mock('../api', () => ({ api: {
  project: vi.fn(), conversation: vi.fn(), projectAnswer: vi.fn(), compilationSessions: vi.fn(),
  answerSubmission: vi.fn(),
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
    vi.mocked(api.answerSubmission).mockRejectedValue(new Error('Invio non ricevuto'))
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
    // Typed and never sent: it is simply back in the composer, no recovery to confirm.
    expect(input()).toHaveValue('a'.repeat(4001))
    expect(screen.queryByRole('button', { name: 'Recupera messaggio' })).not.toBeInTheDocument()
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
    expect(screen.queryByRole('button', { name: /Riutilizza messaggio|Recupera messaggio/ })).not.toBeInTheDocument()
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

  it.each(['failed', 'not_configured', 'direct'] as const)(
    'offre il recupero dallo storico solo dopo un errore: %s', async (status) => {
    vi.mocked(api.conversation).mockResolvedValue({
      id: 'c1', title: 'c1', project_id: 'alfa', metadata: '', target: null,
      turns: [{ ...result(status), id: 1, question: long, answer: 'Risposta registrata' }],
    })
    await setup()
    await screen.findByText('Risposta registrata')
    expect(screen.queryByRole('button', { name: 'Riutilizza messaggio' })).not.toBeInTheDocument()
    if (status === 'direct') {
      expect(screen.queryByRole('button', { name: 'Recupera messaggio' })).not.toBeInTheDocument()
    } else {
      fireEvent.click(screen.getByRole('button', { name: 'Recupera messaggio' }))
      expect(input()).toHaveValue(long)
    }
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
    await waitFor(() => expect(input()).toHaveValue('Nuova bozza durante avvio'))
    expect(screen.queryByRole('button', { name: 'Recupera messaggio' })).not.toBeInTheDocument()
  })

  function history(...turns: [string, GroundedAnswer['generation_status']][]) {
    vi.mocked(api.conversation).mockResolvedValue({
      id: 'c1', title: 'c1', project_id: 'alfa', metadata: '', target: null,
      turns: turns.map(([question, status], index) => (
        { ...result(status), id: index + 1, question, answer: `Risposta ${index + 1}` })),
    })
  }
  const recoveries = () => screen.queryAllByRole('button', { name: 'Recupera messaggio' })

  // Prova manuale Minervino: due invii falliti dello stesso testo, poi la conversazione prosegue.
  it('non offre il recupero di turni falliti già superati da turni successivi', async () => {
    history([long, 'failed'], [long, 'failed'], ['lo riesci a leggere?', 'direct'])
    await setup()
    await screen.findByText('Risposta 3')
    expect(recoveries()).toHaveLength(0)
  })

  it('offre il recupero solo per l’ultimo turno fallito, una volta', async () => {
    history(['ciao', 'not_configured'], ['ciao', 'not_configured'])
    await setup()
    await screen.findByText('Risposta 2')
    expect(recoveries()).toHaveLength(1)
    fireEvent.click(recoveries()[0])
    expect(input()).toHaveValue('ciao')
    expect(api.projectAnswer).not.toHaveBeenCalled()
  })

  it('rimuove la copia di un invio che il server ha già registrato con risposta', async () => {
    vi.mocked(api.projectAnswer).mockReturnValue(new Promise(() => {}))
    await setup(); type(long); send()
    await waitFor(() => expect(api.projectAnswer).toHaveBeenCalledTimes(1))
    cleanup()
    const requestId = vi.mocked(api.projectAnswer).mock.calls[0][6]
    vi.mocked(api.conversation).mockResolvedValue({
      id: 'c1', title: 'c1', project_id: 'alfa', metadata: '', target: null,
      turns: [{ ...result(), id: 1, request_id: requestId, question: long, answer: 'Risposta 1' }],
    })
    await setup()
    await screen.findByText('Risposta 1')
    await waitFor(() => expect(recoveries()).toHaveLength(0))
    expect(sessionStorage.getItem('mapi:chat-draft:alfa:c1')).toBeNull()
    expect(input()).toHaveValue('')
  })

  it('recupera la risposta persistita dopo perdita HTTP senza mostrare un falso fallimento', async () => {
    vi.mocked(api.projectAnswer).mockRejectedValue(new Error('Connessione interrotta'))
    vi.mocked(api.answerSubmission).mockImplementation(async (_project, requestId) => ({
      state: 'completed', response: { ...result(), question: '4', request_id: requestId },
      request: { conversation_id: 'c1' },
    }))
    await setup(); type('4'); send()
    await screen.findByText('Risposta del sistema')
    expect(api.projectAnswer).toHaveBeenCalledTimes(1)
    expect(screen.queryByText('Connessione interrotta')).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Recupera messaggio' })).not.toBeInTheDocument()
  })

  it('riusa lo stesso identificativo dopo errore, refresh e recupero, senza duplicare il turno UI', async () => {
    vi.mocked(api.projectAnswer).mockRejectedValueOnce(new Error('Connessione interrotta'))
    await setup(); type('4'); send()
    await screen.findByRole('button', { name: 'Recupera messaggio' })
    const first = vi.mocked(api.projectAnswer).mock.calls[0]
    cleanup(); await setup()
    vi.mocked(api.projectAnswer).mockResolvedValue({ ...result(), question: '4', request_id: first[6] })
    fireEvent.click(screen.getByRole('button', { name: 'Recupera messaggio' })); send()
    await screen.findByText('Risposta del sistema')
    const second = vi.mocked(api.projectAnswer).mock.calls[1]
    expect(second[6]).toBe(first[6])
    expect(second[5]).toEqual(first[5])
    expect(screen.getAllByText('4')).toHaveLength(1)
  })

  it('non confonde un invio pendente con un vecchio turno dallo stesso testo', async () => {
    vi.mocked(api.projectAnswer).mockReturnValue(new Promise(() => {}))
    await setup(); type('4'); send()
    await waitFor(() => expect(api.projectAnswer).toHaveBeenCalled())
    cleanup()
    vi.mocked(api.conversation).mockResolvedValue({
      id: 'c1', title: 'c1', project_id: 'alfa', metadata: '', target: null,
      turns: [{ ...result(), id: 1, request_id: 'older-submission', question: '4' }],
    })
    await setup()
    expect(await screen.findByRole('button', { name: 'Recupera messaggio' })).toBeInTheDocument()
  })

  it('conserva la copia se il turno registrato con lo stesso testo è fallito', async () => {
    vi.mocked(api.projectAnswer).mockReturnValue(new Promise(() => {}))
    await setup(); type(long); send()
    await waitFor(() => expect(api.projectAnswer).toHaveBeenCalledTimes(1))
    cleanup()
    history([long, 'failed'])
    await setup()
    await screen.findByText('Risposta 1')
    expect(recoveries()).toHaveLength(1)
    fireEvent.click(recoveries()[0])
    expect(input()).toHaveValue(long)
    expect(api.projectAnswer).toHaveBeenCalledTimes(1)
  })

  it('conserva una bozza diversa dall’ultimo messaggio registrato', async () => {
    await setup(); type('Bozza non ancora inviata')
    cleanup()
    history([long, 'direct'])
    await setup()
    await screen.findByText('Risposta 1')
    await waitFor(() => expect(input()).toHaveValue('Bozza non ancora inviata'))
    expect(recoveries()).toHaveLength(0)
  })

  // Prova manuale (29 ottobre): testo digitato, «Aggiungi un modello nelle impostazioni» e
  // ritorno al progetto mostravano «Un messaggio è conservato…» invece del testo.
  it('riporta nel composer il testo digitato dopo le impostazioni AI, senza inviarlo', async () => {
    await setup('/projects/alfa'); type('compila il modulo')
    cleanup()  // The settings page replaces the workspace.
    await setup('/projects/alfa')
    await waitFor(() => expect(input()).toHaveValue('compila il modulo'))
    expect(recoveries()).toHaveLength(0)
    expect(api.projectAnswer).not.toHaveBeenCalled()
  })

  it('non scarta una bozza digitata uguale all’ultimo messaggio registrato', async () => {
    await setup(); type(long)
    cleanup()
    history([long, 'direct'])
    await setup()
    await screen.findByText('Risposta 1')
    await waitFor(() => expect(input()).toHaveValue(long))
    expect(sessionStorage.getItem('mapi:chat-draft:alfa:c1')).not.toBeNull()
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
