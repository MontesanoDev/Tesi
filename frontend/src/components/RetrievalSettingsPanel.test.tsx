import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { RetrievalInput, RetrievalSettings } from '../types'
import { RetrievalSettingsPanel } from './RetrievalSettingsPanel'
import embeddingProviders from '../../e2e/embedding-providers.fixture.json'

vi.mock('../api', () => ({ api: {
  retrievalSettings: vi.fn(), saveRetrievalSettings: vi.fn(),
  checkRetrievalConnection: vi.fn(), updateVectorIndex: vi.fn(), embeddingModels: vi.fn(), embeddingProviders: vi.fn(),
} }))

const settings: RetrievalSettings = {
  backend: 'fts5', qdrant_mode: 'local', qdrant_url: 'http://127.0.0.1:6333',
  embedding_url: 'http://127.0.0.1:11434', embedding_model: 'bge-m3',
  query_prefix: '', document_prefix: '', has_qdrant_api_key: false, has_embedding_api_key: false,
}
const vectorSettings: RetrievalSettings = { ...settings, backend: 'qdrant' }
const remoteSettings: RetrievalSettings = { ...vectorSettings, qdrant_mode: 'remote',
  qdrant_url: 'https://qdrant.example', embedding_url: 'https://ollama.example', has_qdrant_api_key: true }

// The backend stores the configuration and returns it without secrets.
function stored(input: RetrievalInput): RetrievalSettings {
  const { qdrant_api_key, embedding_api_key, clear_qdrant_api_key, clear_embedding_api_key, ...config } = input
  return { ...config, has_qdrant_api_key: !clear_qdrant_api_key && !!qdrant_api_key,
    has_embedding_api_key: !clear_embedding_api_key && !!embedding_api_key }
}

// Removed idle hint: the line below the cards stays silent until something happens.
const autosaveHint = 'Le modifiche si salvano automaticamente.'

async function openTechnical() {
  await screen.findByLabelText('Metodo di ricerca')
  for (const summary of screen.getAllByText('Impostazioni avanzate')) fireEvent.click(summary)
  await waitFor(() => expect(screen.getByLabelText('Modello di embedding')).toBeEnabled())
}

beforeEach(() => {
  vi.resetAllMocks()
  vi.mocked(api.embeddingProviders).mockResolvedValue(embeddingProviders as Awaited<ReturnType<typeof api.embeddingProviders>>)
  vi.mocked(api.retrievalSettings).mockResolvedValue(settings)
  vi.mocked(api.saveRetrievalSettings).mockImplementation(async (input) => stored(input))
  vi.mocked(api.embeddingModels).mockResolvedValue({ models: ['bge-m3:latest', 'custom', 'custom-embed:latest', 'other-embed', 'another-model', 'changed'] })
})
afterEach(cleanup)

describe('retrieval settings', () => {
  it('keeps embedding and Qdrant addresses independent when checking an unsaved port', async () => {
    vi.mocked(api.retrievalSettings).mockResolvedValue({ ...vectorSettings,
      qdrant_mode: 'remote', qdrant_url: 'http://127.0.0.1:6333' })
    vi.mocked(api.checkRetrievalConnection).mockResolvedValue({ message: 'Collegamento riuscito', dimensions: 1024 })
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    const search = screen.getByRole('region', { name: 'Ricerca nelle fonti' })
    const embedding = screen.getByRole('region', { name: 'Modelli di embedding' })
    expect(within(search).getByLabelText('Indirizzo Qdrant')).toHaveValue('127.0.0.1')
    expect(within(search).getByLabelText('Porta (opzionale)')).toHaveValue('6333')
    expect(within(embedding).getByLabelText('Porta (opzionale)')).toHaveValue('11434')
    const addressHelp = screen.getAllByLabelText('Porta (opzionale)').map((input) => input.getAttribute('aria-describedby'))
    expect(new Set(addressHelp).size).toBe(2)
    fireEvent.change(within(search).getByLabelText('Indirizzo Qdrant'), { target: { value: 'https://qdrant.example:8443/proxy' } })
    fireEvent.change(within(search).getByLabelText('Porta (opzionale)'), { target: { value: '6334' } })
    fireEvent.click(within(search).getByRole('button', { name: 'Verifica ricerca semantica' }))
    await within(search).findByText('Collegamento riuscito')
    expect(api.checkRetrievalConnection).toHaveBeenCalledWith(expect.objectContaining({
      qdrant_url: 'https://qdrant.example:6334/proxy', embedding_url: settings.embedding_url,
    }))
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
    expect(api.updateVectorIndex).not.toHaveBeenCalled()
  })

  it('rejects an invalid Qdrant port without blocking the independent embedding check', async () => {
    vi.mocked(api.retrievalSettings).mockResolvedValue({ ...vectorSettings, qdrant_mode: 'remote' })
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    const search = screen.getByRole('region', { name: 'Ricerca nelle fonti' })
    fireEvent.change(within(search).getByLabelText('Porta (opzionale)'), { target: { value: '65536' } })
    fireEvent.click(within(search).getByRole('button', { name: 'Verifica ricerca semantica' }))
    expect(api.checkRetrievalConnection).not.toHaveBeenCalled()
    expect(within(search).getByLabelText('Porta (opzionale)')).toBeInvalid()
    const embedding = screen.getByRole('region', { name: 'Modelli di embedding' })
    fireEvent.click(within(embedding).getByRole('button', { name: 'Verifica collegamento' }))
    await within(embedding).findByText(/Collegamento riuscito/)
    expect(api.embeddingModels).toHaveBeenCalledTimes(2)
  })

  it('saves a model change at once, even while advanced settings are collapsed, and explains the index', async () => {
    vi.mocked(api.retrievalSettings).mockResolvedValue(vectorSettings)
    vi.mocked(api.embeddingModels).mockResolvedValue({ models: ['bge-m3', 'changed'] })
    render(<RetrievalSettingsPanel />)
    await screen.findByLabelText('Metodo di ricerca')
    await waitFor(() => expect(screen.getByLabelText('Modello di embedding')).toBeEnabled())
    expect(screen.queryByText(autosaveHint)).not.toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('Modello di embedding'), { target: { value: 'changed' } })
    expect(await screen.findByText(/L’indice si aggiornerà alla prossima ricerca semantica/)).toBeVisible()
    expect(api.saveRetrievalSettings).toHaveBeenCalledWith(expect.objectContaining({ embedding_model: 'changed' }))
    expect(screen.queryByText(/Questa modifica può richiedere/)).not.toBeInTheDocument()
    expect(api.updateVectorIndex).not.toHaveBeenCalled()
  })

  it('separates the stored Ollama address and port without changing the saved URL', async () => {
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    expect(screen.getByLabelText('Indirizzo Ollama')).toHaveValue('127.0.0.1')
    expect(screen.getByLabelText('Porta (opzionale)')).toHaveValue('11434')
    fireEvent.blur(screen.getByLabelText('Porta (opzionale)'))
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
    fireEvent.change(screen.getByLabelText('Metodo di ricerca'), { target: { value: 'qdrant' } })
    await waitFor(() => expect(api.saveRetrievalSettings).toHaveBeenCalledWith(expect.objectContaining({
      backend: 'qdrant', embedding_url: settings.embedding_url,
    })))
  })

  it('saves a text field only when leaving it, never while typing', async () => {
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    const port = screen.getByLabelText('Porta (opzionale)')
    fireEvent.change(port, { target: { value: '114' } })
    fireEvent.change(port, { target: { value: '11435' } })
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
    fireEvent.blur(port)
    await waitFor(() => expect(api.saveRetrievalSettings).toHaveBeenCalledTimes(1))
    expect(api.saveRetrievalSettings).toHaveBeenCalledWith(expect.objectContaining({ embedding_url: 'http://127.0.0.1:11435' }))
    expect(await screen.findByText(/Impostazioni salvate/)).toBeVisible()
  })

  it('does not save incomplete or invalid fields and says what is missing', async () => {
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.change(screen.getByLabelText('Indirizzo Ollama'), { target: { value: '' } })
    fireEvent.blur(screen.getByLabelText('Indirizzo Ollama'))
    expect(await screen.findByText('Modifiche non salvate: completa i campi indicati.')).toBeVisible()
    fireEvent.change(screen.getByLabelText('Porta (opzionale)'), { target: { value: '0' } })
    fireEvent.submit(screen.getByLabelText('Porta (opzionale)'))
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
    fireEvent.change(screen.getByLabelText('Indirizzo Ollama'), { target: { value: '192.168.1.20' } })
    fireEvent.change(screen.getByLabelText('Porta (opzionale)'), { target: { value: '11434' } })
    fireEvent.submit(screen.getByLabelText('Porta (opzionale)'))
    await waitFor(() => expect(api.saveRetrievalSettings).toHaveBeenCalledWith(expect.objectContaining({
      embedding_url: 'http://192.168.1.20:11434',
    })))
  })

  it('checks an unsaved address and port even in keyword mode without generating embeddings', async () => {
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.change(screen.getByLabelText('Indirizzo Ollama'), { target: { value: '192.168.1.20' } })
    fireEvent.change(screen.getByLabelText('Porta (opzionale)'), { target: { value: '11435' } })
    const embedding = screen.getByRole('region', { name: 'Modelli di embedding' })
    fireEvent.click(within(embedding).getByRole('button', { name: 'Verifica collegamento' }))
    expect(await within(embedding).findByRole('status')).toHaveTextContent('Collegamento riuscito')
    expect(api.embeddingModels).toHaveBeenLastCalledWith(expect.objectContaining({
      embedding_url: 'http://192.168.1.20:11435',
    }), expect.any(AbortSignal))
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
    expect(api.checkRetrievalConnection).not.toHaveBeenCalled()
    expect(api.updateVectorIndex).not.toHaveBeenCalled()
    fireEvent.change(screen.getByLabelText('Porta (opzionale)'), { target: { value: '11436' } })
    expect(within(embedding).queryByText(/Collegamento riuscito/)).not.toBeInTheDocument()
  })

  it.each(['https://ollama.example:8443/proxy/v1', 'http://[::1]:11434'])('round-trips the saved service %s', async (url) => {
    const configured = { ...settings, embedding_url: url }
    vi.mocked(api.retrievalSettings).mockResolvedValue(configured)
    vi.mocked(api.saveRetrievalSettings).mockResolvedValue(configured)
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    expect(screen.getByLabelText('Porta (opzionale)')).toHaveValue(url.includes('8443') ? '8443' : '11434')
    fireEvent.change(screen.getByLabelText('Metodo di ricerca'), { target: { value: 'qdrant' } })
    await waitFor(() => expect(api.saveRetrievalSettings).toHaveBeenCalledWith(expect.objectContaining({ embedding_url: url })))
  })

  it('keeps HTTPS and the path when clearing the optional port and accepts a pasted full URL', async () => {
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.change(screen.getByLabelText('Indirizzo Ollama'), { target: { value: 'https://server.example:8443/proxy/v1' } })
    expect(screen.getByLabelText('Indirizzo Ollama')).toHaveValue('https://server.example/proxy/v1')
    expect(screen.getByLabelText('Porta (opzionale)')).toHaveValue('8443')
    fireEvent.change(screen.getByLabelText('Porta (opzionale)'), { target: { value: '' } })
    fireEvent.click(screen.getByRole('button', { name: 'Ricarica modelli' }))
    await waitFor(() => expect(api.embeddingModels).toHaveBeenLastCalledWith(expect.objectContaining({
      embedding_url: 'https://server.example/proxy/v1',
    }), expect.any(AbortSignal)))
  })

  it.each(['0', '65536', 'abc', '-1', '1.5'])('blocks an invalid port %s before a service request', async (port) => {
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.change(screen.getByLabelText('Porta (opzionale)'), { target: { value: port } })
    fireEvent.click(within(screen.getByRole('region', { name: 'Modelli di embedding' })).getByRole('button', { name: 'Verifica collegamento' }))
    expect(screen.getByLabelText('Porta (opzionale)')).toBeInvalid()
    expect(api.embeddingModels).toHaveBeenCalledTimes(1)
  })

  it('reports an unreachable service without saving or losing the entered port', async () => {
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    vi.mocked(api.embeddingModels).mockRejectedValueOnce(new Error('Servizio non raggiungibile'))
    fireEvent.change(screen.getByLabelText('Porta (opzionale)'), { target: { value: '11435' } })
    const embedding = screen.getByRole('region', { name: 'Modelli di embedding' })
    fireEvent.click(within(embedding).getByRole('button', { name: 'Verifica collegamento' }))
    expect(await within(embedding).findByRole('alert')).toHaveTextContent('Servizio non raggiungibile')
    expect(screen.getByLabelText('Porta (opzionale)')).toHaveValue('11435')
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
  })

  it('distinguishes a reachable service from an unlisted model', async () => {
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    vi.mocked(api.embeddingModels).mockResolvedValueOnce({ models: ['other-model'] })
    const embedding = screen.getByRole('region', { name: 'Modelli di embedding' })
    fireEvent.click(within(embedding).getByRole('button', { name: 'Verifica collegamento' }))
    expect(await within(embedding).findByRole('status')).toHaveTextContent('Servizio raggiungibile')
    expect(within(embedding).getByRole('status')).toHaveTextContent('resta da verificare')
  })

  it('does not report a late verification as successful after the address changes', async () => {
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    let finish = (_value: { models: string[] }) => {}
    vi.mocked(api.embeddingModels).mockReturnValueOnce(new Promise((resolve) => { finish = resolve }))
    const embedding = screen.getByRole('region', { name: 'Modelli di embedding' })
    fireEvent.click(within(embedding).getByRole('button', { name: 'Verifica collegamento' }))
    expect(within(embedding).getByRole('button', { name: 'Verifica…' })).toBeDisabled()
    const signal = vi.mocked(api.embeddingModels).mock.calls.at(-1)?.[1]
    fireEvent.change(screen.getByLabelText('Porta (opzionale)'), { target: { value: '11435' } })
    expect(signal?.aborted).toBe(true)
    finish({ models: ['bge-m3'] })
    await waitFor(() => expect(within(embedding).queryByRole('status')).not.toBeInTheDocument())
    expect(screen.getByLabelText('Porta (opzionale)')).toHaveValue('11435')
  })

  it.each(['ftp://server.example', 'https://user:password@server.example', 'https://server.example?token=test'])('blocks unsupported address %s', async (address) => {
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.change(screen.getByLabelText('Indirizzo Ollama'), { target: { value: address } })
    fireEvent.click(within(screen.getByRole('region', { name: 'Modelli di embedding' })).getByRole('button', { name: 'Verifica collegamento' }))
    expect(screen.getByLabelText('Indirizzo Ollama')).toBeInvalid()
    expect(api.embeddingModels).toHaveBeenCalledTimes(1)
  })

  it('replaces the old port when pasting a full address with no custom port', async () => {
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.paste(screen.getByLabelText('Indirizzo Ollama'), { clipboardData: { getData: () => 'http://server.example/proxy' } })
    expect(screen.getByLabelText('Indirizzo Ollama')).toHaveValue('server.example/proxy')
    expect(screen.getByLabelText('Porta (opzionale)')).toHaveValue('')
    fireEvent.click(screen.getByRole('button', { name: 'Ricarica modelli' }))
    await waitFor(() => expect(api.embeddingModels).toHaveBeenLastCalledWith(expect.objectContaining({
      embedding_url: 'http://server.example/proxy',
    }), expect.any(AbortSignal)))
  })

  it('shows two cards and hides storage options for keyword search', async () => {
    render(<RetrievalSettingsPanel />)
    expect(await screen.findByLabelText('Metodo di ricerca')).toHaveValue('fts5')
    const search = screen.getByRole('region', { name: 'Ricerca nelle fonti' })
    expect(search).toBeVisible()
    expect(screen.getByRole('region', { name: 'Modelli di embedding' })).toBeVisible()
    expect(within(search).getAllByRole('option').map((option) => option.getAttribute('value'))).toEqual(['fts5', 'qdrant'])
    expect(within(search).getByRole('option', { name: 'Semantica' })).toBeInTheDocument()
    expect(screen.queryByText(/Trova passaggi con un significato/)).not.toBeInTheDocument()
    expect(screen.queryByText(/Modello attivo/)).not.toBeInTheDocument()
    expect(within(search).queryByText('Impostazioni avanzate')).not.toBeInTheDocument()
    expect(screen.getByLabelText('Modello di embedding')).toBeVisible()
    expect(screen.queryByRole('button', { name: 'Aggiorna indice' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Salva impostazioni' })).not.toBeInTheDocument()
    expect(screen.queryByText(autosaveHint)).not.toBeInTheDocument()
  })

  it('saves vector retrieval independently and allows indexing only the saved configuration', async () => {
    const configured = { ...settings, query_prefix: 'query:', document_prefix: 'passage:' }
    vi.mocked(api.retrievalSettings).mockResolvedValue(configured)
    vi.mocked(api.saveRetrievalSettings).mockResolvedValue({ ...configured, backend: 'qdrant' })
    vi.mocked(api.updateVectorIndex).mockResolvedValue({ collection: 'test', indexed_chunks: 40,
      updated_chunks: 2, deleted_chunks: 1, dimensions: 768, embedding_digest: 'test' })
    render(<RetrievalSettingsPanel />)
    fireEvent.change(await screen.findByLabelText('Metodo di ricerca'), { target: { value: 'qdrant' } })
    expect(screen.queryByText(/Modello previsto/)).not.toBeInTheDocument()
    expect(screen.getByLabelText('Tipo di archivio')).not.toBeVisible()
    expect(screen.getByRole('button', { name: 'Aggiorna indice' })).toBeDisabled()
    await openTechnical()
    expect(screen.getByLabelText('Modello di embedding')).toHaveValue('bge-m3')
    expect(screen.queryByLabelText(/Prefisso/)).not.toBeInTheDocument()
    await waitFor(() => expect(screen.getByRole('button', { name: 'Aggiorna indice' })).toBeEnabled())
    expect(api.saveRetrievalSettings).toHaveBeenCalledTimes(1)
    expect(api.saveRetrievalSettings).toHaveBeenCalledWith(expect.objectContaining({
      backend: 'qdrant', embedding_model: 'bge-m3', query_prefix: 'query:', document_prefix: 'passage:',
    }))
    fireEvent.click(screen.getByRole('button', { name: 'Aggiorna indice' }))
    expect(await screen.findByText(/40 frammenti, 2 aggiornati e 1 rimossi/)).toBeVisible()
    fireEvent.change(screen.getByLabelText('Indirizzo Ollama'), { target: { value: 'https://ollama.example' } })
    expect(screen.getByRole('button', { name: 'Aggiorna indice' })).toBeDisabled()
    expect(screen.getByText('L’indice si può aggiornare quando le modifiche sono salvate.')).toBeVisible()
  })

  it('checks remote endpoints without saving and clears keys once the key field is saved', async () => {
    vi.mocked(api.retrievalSettings).mockResolvedValue(remoteSettings)
    vi.mocked(api.checkRetrievalConnection).mockResolvedValue({ message: 'Collegamento riuscito', dimensions: 768 })
    vi.mocked(api.saveRetrievalSettings).mockResolvedValue(remoteSettings)
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    const key = await screen.findByLabelText(/Chiave Qdrant/)
    expect(key).toHaveValue('')
    fireEvent.change(key, { target: { value: 'fake-secret' } })
    fireEvent.click(screen.getByRole('button', { name: 'Verifica ricerca semantica' }))
    await screen.findByText('Collegamento riuscito')
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
    expect(api.checkRetrievalConnection).toHaveBeenCalledWith(expect.objectContaining({
      qdrant_url: remoteSettings.qdrant_url, embedding_url: remoteSettings.embedding_url, qdrant_api_key: 'fake-secret',
    }))
    expect(key).toHaveAttribute('type', 'password')
    expect(api.updateVectorIndex).not.toHaveBeenCalled()
    fireEvent.blur(key)
    await waitFor(() => expect(key).toHaveValue(''))
    expect(api.saveRetrievalSettings).toHaveBeenCalledWith(expect.objectContaining({ qdrant_api_key: 'fake-secret' }))
    expect(vi.mocked(api.saveRetrievalSettings).mock.calls[0][0]).not.toHaveProperty('has_qdrant_api_key')
  })

  it('keeps the saved configuration and exposes an indexing failure', async () => {
    vi.mocked(api.retrievalSettings).mockResolvedValue({ ...settings, backend: 'qdrant' })
    vi.mocked(api.updateVectorIndex).mockRejectedValue(new Error('Ollama non raggiungibile'))
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.click(screen.getByRole('button', { name: 'Aggiorna indice' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Ollama non raggiungibile')
    expect(screen.getByLabelText('Metodo di ricerca')).toHaveValue('qdrant')
    expect(screen.getByRole('button', { name: 'Aggiorna indice' })).toBeEnabled()
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
  })

  it('separates embedding generation, storage and index maintenance', async () => {
    vi.mocked(api.retrievalSettings).mockResolvedValue(vectorSettings)
    render(<RetrievalSettingsPanel />)
    await screen.findByLabelText('Metodo di ricerca')
    expect(screen.queryByText(/Modello attivo/)).not.toBeInTheDocument()
    expect(screen.getByLabelText('Tipo di archivio')).not.toBeVisible()
    expect(screen.getByRole('region', { name: 'Manutenzione dell’indice' })).not.toBeVisible()
    await openTechnical()
    const embedding = screen.getByRole('region', { name: 'Modelli di embedding' })
    const storage = screen.getByRole('group', { name: 'Configurazione archivio' })
    expect(within(embedding).getByLabelText('Modello di embedding')).toBeVisible()
    expect(within(embedding).getByText('Ollama', { exact: true })).toBeVisible()
    expect(within(embedding).queryByLabelText('Tipo di archivio')).not.toBeInTheDocument()
    expect(within(storage).getByLabelText('Tipo di archivio')).toHaveValue('local')
    expect(within(storage).queryByLabelText('Indirizzo Ollama')).not.toBeInTheDocument()
    expect(screen.queryByText(/Qdrant funziona nel backend/)).not.toBeInTheDocument()
    expect(screen.queryByText(/Nome di un modello di embedding già installato/)).not.toBeInTheDocument()
    expect(screen.queryByText(/non necessariamente il tuo computer/)).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Indirizzo Qdrant')).not.toBeInTheDocument()
    expect(screen.queryByLabelText(/Chiave Qdrant/)).not.toBeInTheDocument()
  })

  it('never checks the connection or starts indexing when a model change is saved', async () => {
    const configured = { ...vectorSettings, embedding_model: 'custom-embed:latest' }
    vi.mocked(api.retrievalSettings).mockResolvedValue(configured)
    vi.mocked(api.saveRetrievalSettings).mockResolvedValue({ ...configured, embedding_model: 'other-embed' })
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.change(screen.getByLabelText('Modello di embedding'), { target: { value: 'other-embed' } })
    expect(screen.getByRole('button', { name: 'Aggiorna indice' })).toBeDisabled()
    await waitFor(() => expect(screen.getByRole('button', { name: 'Aggiorna indice' })).toBeEnabled())
    expect(api.saveRetrievalSettings).toHaveBeenCalledWith(expect.objectContaining({ embedding_model: 'other-embed' }))
    expect(screen.getByLabelText('Modello di embedding')).toHaveValue('other-embed')
    expect(api.updateVectorIndex).not.toHaveBeenCalled()
    expect(api.checkRetrievalConnection).not.toHaveBeenCalled()
  })

  it('retains hidden vector configuration and credentials when changing method or storage', async () => {
    const configured = { ...remoteSettings, query_prefix: 'query:', document_prefix: 'passage:', embedding_model: 'custom' }
    vi.mocked(api.retrievalSettings).mockResolvedValue(configured)
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.change(screen.getByLabelText('Tipo di archivio'), { target: { value: 'local' } })
    expect(screen.queryByLabelText('Indirizzo Qdrant')).not.toBeInTheDocument()
    expect(screen.getByLabelText('Indirizzo Ollama')).toHaveValue(configured.embedding_url)
    fireEvent.change(screen.getByLabelText('Metodo di ricerca'), { target: { value: 'fts5' } })
    expect(screen.queryByRole('region', { name: 'Manutenzione dell’indice' })).not.toBeInTheDocument()
    await screen.findByText(/La ricerca usa le parole chiave/)
    expect(api.saveRetrievalSettings).toHaveBeenCalledTimes(2)
    expect(api.saveRetrievalSettings).toHaveBeenLastCalledWith({
      backend: 'fts5', embedding_provider: 'ollama', qdrant_mode: 'local', qdrant_url: configured.qdrant_url,
      embedding_url: configured.embedding_url, embedding_model: 'custom', query_prefix: 'query:', document_prefix: 'passage:',
      qdrant_api_key: '', embedding_api_key: '', clear_qdrant_api_key: false, clear_embedding_api_key: false,
    })
    expect(api.updateVectorIndex).not.toHaveBeenCalled()
  })

  it('preserves and explicitly removes saved keys without displaying them', async () => {
    vi.mocked(api.retrievalSettings).mockResolvedValue({ ...remoteSettings, has_embedding_api_key: true })
    vi.mocked(api.saveRetrievalSettings).mockResolvedValue({ ...remoteSettings, has_qdrant_api_key: false })
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    const key = screen.getByLabelText('Chiave Qdrant (facoltativa)')
    expect(key).toHaveValue('')
    fireEvent.change(key, { target: { value: 'unused-secret' } })
    fireEvent.click(screen.getByLabelText('Rimuovi chiave Qdrant'))
    expect(key).toHaveValue('')
    expect(key).toBeDisabled()
    await screen.findByText(/Impostazioni salvate/)
    expect(api.saveRetrievalSettings).toHaveBeenCalledWith(expect.objectContaining({
      qdrant_api_key: '', clear_qdrant_api_key: true, embedding_api_key: '', clear_embedding_api_key: false,
    }))
    expect(screen.queryByLabelText('Rimuovi chiave Qdrant')).not.toBeInTheDocument()
  })

  it.each(['embedding', 'qdrant'] as const)('explains key re-entry when changing the %s endpoint', async (service) => {
    vi.mocked(api.retrievalSettings).mockResolvedValue({ ...remoteSettings, has_embedding_api_key: true })
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.change(screen.getByLabelText(service === 'embedding' ? 'Indirizzo Ollama' : 'Indirizzo Qdrant'),
      { target: { value: 'https://different.example' } })
    expect(screen.getByText(new RegExp(`reinserisci o rimuovi la chiave ${service === 'embedding' ? 'embedding' : 'Qdrant'} salvata`))).toBeVisible()
    fireEvent.change(screen.getByLabelText(service === 'embedding' ? 'Chiave del servizio embedding (facoltativa)' : 'Chiave Qdrant (facoltativa)'),
      { target: { value: 'replacement-key' } })
    expect(screen.queryByText(new RegExp(`reinserisci o rimuovi la chiave ${service === 'embedding' ? 'embedding' : 'Qdrant'} salvata`))).not.toBeInTheDocument()
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
  })

  it('blocks a connection check with invalid input', async () => {
    vi.mocked(api.retrievalSettings).mockResolvedValue(vectorSettings)
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.change(screen.getByLabelText('Indirizzo Ollama'), { target: { value: '' } })
    fireEvent.click(screen.getByRole('button', { name: 'Verifica ricerca semantica' }))
    expect(api.checkRetrievalConnection).not.toHaveBeenCalled()
    expect(screen.getByLabelText('Indirizzo Ollama')).toBeInvalid()
  })

  it.each(['check', 'index'] as const)('shows progress and prevents duplicate %s actions', async (action) => {
    vi.mocked(api.retrievalSettings).mockResolvedValue(vectorSettings)
    let finish = () => {}
    const pending = new Promise<never>((_resolve, reject) => { finish = () => reject(new Error('Test concluso')) })
    const method = { check: api.checkRetrievalConnection, index: api.updateVectorIndex }[action]
    vi.mocked(method).mockReturnValue(pending)
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    const label = { check: 'Verifica ricerca semantica', index: 'Aggiorna indice' }[action]
    fireEvent.click(screen.getByRole('button', { name: label }))
    expect(screen.getByRole('status')).not.toBeEmptyDOMElement()
    expect(screen.getByLabelText('Metodo di ricerca')).toBeDisabled()
    for (const button of screen.getAllByRole('button')) expect(button).toBeDisabled()
    expect(method).toHaveBeenCalledTimes(1)
    finish()
    expect(await screen.findByRole('alert')).toHaveTextContent('Test concluso')
    expect(screen.getByRole('button', { name: label })).toBeEnabled()
  })

  it('reports a failed save without discarding edits', async () => {
    vi.mocked(api.retrievalSettings).mockResolvedValue(vectorSettings)
    vi.mocked(api.saveRetrievalSettings).mockRejectedValue(new Error('Configurazione non valida'))
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.change(screen.getByLabelText('Modello di embedding'), { target: { value: 'another-model' } })
    expect(await screen.findByRole('alert')).toHaveTextContent('Salvataggio non riuscito: Configurazione non valida')
    expect(screen.getByLabelText('Modello di embedding')).toHaveValue('another-model')
    expect(screen.getByRole('button', { name: 'Aggiorna indice' })).toBeDisabled()
    vi.mocked(api.saveRetrievalSettings).mockImplementation(async (input) => stored(input))
    fireEvent.click(screen.getByRole('button', { name: 'Riprova' }))
    expect(await screen.findByText(/Impostazioni salvate/)).toBeVisible()
    expect(api.saveRetrievalSettings).toHaveBeenLastCalledWith(expect.objectContaining({ embedding_model: 'another-model' }))
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('shows save progress and queues a change made while saving without losing it', async () => {
    vi.mocked(api.retrievalSettings).mockResolvedValue(vectorSettings)
    let finish = () => {}
    vi.mocked(api.saveRetrievalSettings).mockImplementationOnce((input) =>
      new Promise((resolve) => { finish = () => resolve(stored(input)) }))
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.change(screen.getByLabelText('Modello di embedding'), { target: { value: 'custom' } })
    expect(await screen.findByText('Salvataggio…')).toBeVisible()
    expect(screen.getByLabelText('Metodo di ricerca')).toBeEnabled()
    fireEvent.change(screen.getByLabelText('Modello di embedding'), { target: { value: 'other-embed' } })
    expect(api.saveRetrievalSettings).toHaveBeenCalledTimes(1)
    finish()
    await waitFor(() => expect(api.saveRetrievalSettings).toHaveBeenCalledTimes(2))
    expect(api.saveRetrievalSettings).toHaveBeenLastCalledWith(expect.objectContaining({ embedding_model: 'other-embed' }))
    await screen.findByText(/Impostazioni salvate/)
    expect(screen.getByLabelText('Modello di embedding')).toHaveValue('other-embed')
  })

  it('waits for a decision on a saved key before saving a changed address', async () => {
    vi.mocked(api.retrievalSettings).mockResolvedValue({ ...remoteSettings, has_embedding_api_key: true })
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    const address = screen.getByLabelText('Indirizzo Ollama')
    fireEvent.change(address, { target: { value: 'https://different.example' } })
    fireEvent.blur(address)
    expect(await screen.findByText('Modifiche non salvate: completa i campi indicati.')).toBeVisible()
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
    fireEvent.click(screen.getByLabelText('Rimuovi chiave embedding'))
    await waitFor(() => expect(api.saveRetrievalSettings).toHaveBeenCalledWith(expect.objectContaining({
      embedding_url: 'https://different.example', clear_embedding_api_key: true, embedding_api_key: '',
    })))
  })

  it('retries loading and clears an obsolete notice when settings change', async () => {
    vi.mocked(api.retrievalSettings).mockRejectedValueOnce(new Error('Rete non disponibile'))
      .mockResolvedValueOnce(vectorSettings)
    vi.mocked(api.checkRetrievalConnection).mockResolvedValue({ message: 'Collegamento riuscito', dimensions: 1024 })
    render(<RetrievalSettingsPanel />)
    expect(screen.getByRole('status')).toHaveTextContent('Caricamento impostazioni')
    expect(await screen.findByRole('alert')).toHaveTextContent('Rete non disponibile')
    fireEvent.click(screen.getByRole('button', { name: 'Riprova' }))
    await openTechnical()
    fireEvent.click(screen.getByRole('button', { name: 'Verifica ricerca semantica' }))
    await screen.findByText('Collegamento riuscito')
    fireEvent.change(screen.getByLabelText('Modello di embedding'), { target: { value: 'changed' } })
    expect(screen.queryByText('Collegamento riuscito')).not.toBeInTheDocument()
  })

  it('offers installed embedding models and treats latest as an alias without changing the saved value', async () => {
    vi.mocked(api.embeddingModels).mockResolvedValue({ models: ['bge-m3:latest', 'nomic-embed-text:latest'] })
    render(<RetrievalSettingsPanel />)
    const select = await screen.findByLabelText('Modello di embedding')
    await waitFor(() => expect(select).toBeEnabled())
    expect(within(select).getAllByRole('option').map((option) => option.getAttribute('value')))
      .toEqual(['bge-m3', 'nomic-embed-text:latest'])
    expect(select).toHaveValue('bge-m3')
    expect(api.embeddingModels).toHaveBeenCalledTimes(1)
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
    expect(api.updateVectorIndex).not.toHaveBeenCalled()
  })

  it('keeps an unavailable configured model instead of silently choosing another', async () => {
    vi.mocked(api.embeddingModels).mockResolvedValue({ models: ['different-embed'] })
    render(<RetrievalSettingsPanel />)
    await waitFor(() => expect(screen.getByRole('option', { name: 'bge-m3 (non verificato)' })).toBeDisabled())
    expect(screen.getByLabelText('Modello di embedding')).toHaveValue('bge-m3')
    fireEvent.change(screen.getByLabelText('Modello di embedding'), { target: { value: 'different-embed' } })
    expect(screen.getByLabelText('Modello di embedding')).toHaveValue('different-embed')
  })

  it('shows an empty server inventory without erasing the configured model', async () => {
    vi.mocked(api.embeddingModels).mockResolvedValue({ models: [] })
    render(<RetrievalSettingsPanel />)
    expect(await screen.findByText('Nessun modello di embedding rilevato su questo server.')).toBeVisible()
    expect(screen.getByLabelText('Modello di embedding')).toHaveValue('bge-m3')
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
  })

  it('reports unavailable Ollama and retries inventory without a save or index update', async () => {
    vi.mocked(api.embeddingModels).mockRejectedValueOnce(new Error('Ollama non raggiungibile'))
      .mockResolvedValueOnce({ models: ['bge-m3'] })
    render(<RetrievalSettingsPanel />)
    expect(await screen.findByRole('alert')).toHaveTextContent('Ollama non raggiungibile')
    fireEvent.click(screen.getByRole('button', { name: 'Ricarica modelli' }))
    await waitFor(() => expect(screen.queryByRole('alert')).not.toBeInTheDocument())
    expect(api.embeddingModels).toHaveBeenCalledTimes(2)
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
    expect(api.updateVectorIndex).not.toHaveBeenCalled()
  })

  it('invalidates inventory on service edits and discards a late response from the previous server', async () => {
    let finish = (_value: { models: string[] }) => {}
    vi.mocked(api.embeddingModels).mockReturnValueOnce(new Promise((resolve) => { finish = resolve }))
      .mockResolvedValueOnce({ models: ['new-server-embed'] })
    render(<RetrievalSettingsPanel />)
    await screen.findByLabelText('Indirizzo Ollama')
    const embedding = screen.getByRole('region', { name: 'Modelli di embedding' })
    fireEvent.click(within(embedding).getByText('Impostazioni avanzate'))
    fireEvent.change(screen.getByLabelText('Indirizzo Ollama'), { target: { value: 'https://new-server.example' } })
    finish({ models: ['stale-embed'] })
    expect(await screen.findByText(/Ricarica i modelli dopo/)).toBeVisible()
    expect(screen.queryByRole('option', { name: 'stale-embed' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Ricarica modelli' }))
    expect(await screen.findByRole('option', { name: 'new-server-embed' })).toBeInTheDocument()
    expect(api.embeddingModels).toHaveBeenLastCalledWith(expect.objectContaining({ embedding_url: 'https://new-server.example' }), expect.any(AbortSignal))
  })

  it('places embeddings before search and reads provider choices from the backend', async () => {
    render(<RetrievalSettingsPanel />)
    await screen.findByLabelText('Metodo di ricerca')
    expect(screen.getAllByRole('heading', { level: 2 }).map((heading) => heading.textContent))
      .toEqual(['Modelli di embedding', 'Ricerca nelle fonti'])
    expect(screen.getByLabelText('Provider di embedding')).toHaveValue('ollama')
    expect(within(screen.getByLabelText('Provider di embedding')).getAllByRole('option').map((option) => option.textContent))
      .toEqual(['Ollama', 'OpenAI', 'Mistral', 'Compatibile con OpenAI'])
  })

  it('does not carry a saved credential across providers and allows entering the new required key', async () => {
    vi.mocked(api.retrievalSettings).mockResolvedValue({ ...vectorSettings, has_embedding_api_key: true })
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.change(screen.getByLabelText('Provider di embedding'), { target: { value: 'openai' } })
    expect(screen.getByLabelText('Indirizzo del servizio embedding')).toHaveValue('https://api.openai.com/v1')
    const key = screen.getByLabelText('Chiave del servizio embedding')
    expect(key).toHaveValue('')
    expect(key).toBeEnabled()
    expect(key).toBeRequired()
    fireEvent.change(key, { target: { value: 'new-provider-key' } })
    expect(screen.getByLabelText('Rimuovi chiave embedding')).not.toBeChecked()
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
    expect(api.embeddingModels).toHaveBeenCalledTimes(1)
    expect(api.updateVectorIndex).not.toHaveBeenCalled()
  })

  it('discovers and saves a cloud embedding model with its own provider and key', async () => {
    vi.mocked(api.retrievalSettings).mockResolvedValue(vectorSettings)
    vi.mocked(api.embeddingModels).mockResolvedValue({ models: ['text-embedding-3-small', 'text-embedding-3-large'] })
    vi.mocked(api.saveRetrievalSettings).mockResolvedValue({ ...vectorSettings, embedding_provider: 'openai',
      embedding_url: 'https://api.openai.com/v1', embedding_model: 'text-embedding-3-large', has_embedding_api_key: true })
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.change(screen.getByLabelText('Provider di embedding'), { target: { value: 'openai' } })
    fireEvent.change(screen.getByLabelText('Chiave del servizio embedding'), { target: { value: 'cloud-embedding-key' } })
    fireEvent.click(screen.getByRole('button', { name: 'Ricarica modelli' }))
    await screen.findByRole('option', { name: 'text-embedding-3-large' })
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
    fireEvent.change(screen.getByLabelText('Modello di embedding'), { target: { value: 'text-embedding-3-large' } })
    await screen.findByText(/Impostazioni salvate/)
    expect(api.saveRetrievalSettings).toHaveBeenCalledWith(expect.objectContaining({
      embedding_provider: 'openai', embedding_api_key: 'cloud-embedding-key', embedding_model: 'text-embedding-3-large',
    }))
    expect(screen.getByLabelText('Chiave del servizio embedding')).toHaveValue('')
    expect(api.updateVectorIndex).not.toHaveBeenCalled()
  })

  it('allows a custom embedding model when a compatible server does not advertise capabilities', async () => {
    vi.mocked(api.embeddingModels).mockResolvedValue({ models: [] })
    render(<RetrievalSettingsPanel />)
    await screen.findByLabelText('Provider di embedding')
    fireEvent.change(screen.getByLabelText('Provider di embedding'), { target: { value: 'compatible' } })
    expect(screen.getByLabelText('Modello di embedding')).toHaveAttribute('type', 'text')
    expect(screen.getByLabelText('Modello di embedding')).toBeRequired()
    fireEvent.change(screen.getByLabelText('Indirizzo del servizio embedding'), { target: { value: 'https://local-embed.example/v1' } })
    fireEvent.change(screen.getByLabelText('Modello di embedding'), { target: { value: 'custom-model' } })
    fireEvent.click(screen.getByRole('button', { name: 'Ricarica modelli' }))
    expect(await screen.findByText(/Nessun modello identificato automaticamente/)).toBeVisible()
    expect(screen.getByLabelText('Modello di embedding')).toHaveValue('custom-model')
    expect(api.embeddingModels).toHaveBeenLastCalledWith(expect.objectContaining({ embedding_provider: 'compatible' }), expect.any(AbortSignal))
  })
})
