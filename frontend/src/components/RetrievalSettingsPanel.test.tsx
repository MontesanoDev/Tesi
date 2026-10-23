import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { RetrievalSettings } from '../types'
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

async function openTechnical() {
  await screen.findByLabelText('Metodo di ricerca')
  for (const summary of screen.getAllByText('Impostazioni avanzate')) fireEvent.click(summary)
  await waitFor(() => expect(screen.getByLabelText('Modello di embedding')).toBeEnabled())
}

beforeEach(() => {
  vi.resetAllMocks()
  vi.mocked(api.embeddingProviders).mockResolvedValue(embeddingProviders as Awaited<ReturnType<typeof api.embeddingProviders>>)
  vi.mocked(api.retrievalSettings).mockResolvedValue(settings)
  vi.mocked(api.embeddingModels).mockResolvedValue({ models: ['bge-m3:latest', 'custom', 'custom-embed:latest', 'other-embed', 'another-model', 'changed'] })
})
afterEach(cleanup)

describe('retrieval settings', () => {
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
    expect(screen.getByRole('button', { name: 'Salva impostazioni' })).toBeVisible()
  })

  it('saves vector retrieval independently and allows indexing only the saved configuration', async () => {
    const configured = { ...settings, query_prefix: 'query:', document_prefix: 'passage:' }
    vi.mocked(api.retrievalSettings).mockResolvedValue(configured)
    vi.mocked(api.saveRetrievalSettings).mockResolvedValue({ ...configured, backend: 'qdrant' })
    vi.mocked(api.updateVectorIndex).mockResolvedValue({ collection: 'test', indexed_chunks: 40,
      updated_chunks: 2, deleted_chunks: 1, dimensions: 768, embedding_digest: 'test' })
    render(<RetrievalSettingsPanel />)
    fireEvent.change(await screen.findByLabelText('Metodo di ricerca'), { target: { value: 'qdrant' } })
    expect(screen.getByLabelText('Tipo di archivio')).not.toBeVisible()
    await openTechnical()
    expect(screen.getByLabelText('Modello di embedding')).toHaveValue('bge-m3')
    expect(screen.queryByLabelText(/Prefisso/)).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Aggiorna indice' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Salva impostazioni' }))
    await waitFor(() => expect(screen.getByRole('button', { name: 'Aggiorna indice' })).toBeEnabled())
    expect(api.saveRetrievalSettings).toHaveBeenCalledWith(expect.objectContaining({
      backend: 'qdrant', embedding_model: 'bge-m3', query_prefix: 'query:', document_prefix: 'passage:',
    }))
    fireEvent.click(screen.getByRole('button', { name: 'Aggiorna indice' }))
    expect(await screen.findByText(/40 frammenti, 2 aggiornati e 1 rimossi/)).toBeVisible()
    fireEvent.change(screen.getByLabelText('Indirizzo Ollama'), { target: { value: 'https://ollama.example' } })
    expect(screen.getByRole('button', { name: 'Aggiorna indice' })).toBeDisabled()
  })

  it('checks remote endpoints without saving and clears keys after saving', async () => {
    vi.mocked(api.retrievalSettings).mockResolvedValue(remoteSettings)
    vi.mocked(api.checkRetrievalConnection).mockResolvedValue({ message: 'Collegamento riuscito', dimensions: 768 })
    vi.mocked(api.saveRetrievalSettings).mockResolvedValue(remoteSettings)
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    const key = await screen.findByLabelText(/Chiave Qdrant/)
    expect(key).toHaveValue('')
    fireEvent.change(key, { target: { value: 'fake-secret' } })
    fireEvent.click(screen.getByRole('button', { name: 'Verifica collegamento' }))
    await screen.findByText('Collegamento riuscito')
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
    expect(api.checkRetrievalConnection).toHaveBeenCalledWith(expect.objectContaining({
      qdrant_url: remoteSettings.qdrant_url, embedding_url: remoteSettings.embedding_url, qdrant_api_key: 'fake-secret',
    }))
    expect(key).toHaveAttribute('type', 'password')
    expect(api.updateVectorIndex).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Salva impostazioni' }))
    await waitFor(() => expect(key).toHaveValue(''))
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
    expect(screen.getByText(/Modello attivo:/)).toHaveTextContent('bge-m3')
    expect(screen.getByLabelText('Tipo di archivio')).not.toBeVisible()
    expect(screen.getByRole('region', { name: 'Manutenzione dell’indice' })).not.toBeVisible()
    await openTechnical()
    const embedding = screen.getByRole('region', { name: 'Modelli di embedding' })
    const storage = screen.getByRole('group', { name: 'Archivio vettoriale' })
    expect(within(embedding).getByLabelText('Modello di embedding')).toBeVisible()
    expect(within(embedding).getByText('Ollama', { exact: true })).toBeVisible()
    expect(within(embedding).queryByLabelText('Tipo di archivio')).not.toBeInTheDocument()
    expect(within(storage).getByLabelText('Tipo di archivio')).toHaveValue('local')
    expect(within(storage).queryByLabelText('Indirizzo Ollama')).not.toBeInTheDocument()
    expect(screen.queryByText(/Qdrant funziona nel backend/)).not.toBeInTheDocument()
    expect(screen.queryByText(/Nome di un modello di embedding già installato/)).not.toBeInTheDocument()
    expect(screen.getByText(/non necessariamente il tuo computer/)).toBeVisible()
    expect(screen.queryByLabelText('Indirizzo Qdrant')).not.toBeInTheDocument()
    expect(screen.queryByLabelText(/Chiave Qdrant/)).not.toBeInTheDocument()
  })

  it('keeps the active model distinct from an unsaved change and never starts indexing on save', async () => {
    const configured = { ...vectorSettings, embedding_model: 'custom-embed:latest' }
    vi.mocked(api.retrievalSettings).mockResolvedValue(configured)
    vi.mocked(api.saveRetrievalSettings).mockResolvedValue({ ...configured, embedding_model: 'other-embed' })
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.change(screen.getByLabelText('Modello di embedding'), { target: { value: 'other-embed' } })
    expect(screen.getByText(/Modello attivo:/)).toHaveTextContent('custom-embed:latest')
    expect(screen.getByText(/Questa modifica può richiedere/)).toBeVisible()
    expect(screen.getByRole('button', { name: 'Aggiorna indice' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Salva impostazioni' }))
    await waitFor(() => expect(screen.getByText(/Modello attivo:/)).toHaveTextContent('other-embed'))
    expect(api.saveRetrievalSettings).toHaveBeenCalledWith(expect.objectContaining({ embedding_model: 'other-embed' }))
    expect(api.updateVectorIndex).not.toHaveBeenCalled()
    expect(api.checkRetrievalConnection).not.toHaveBeenCalled()
  })

  it('retains hidden vector configuration and credentials when changing method or storage', async () => {
    const configured = { ...remoteSettings, query_prefix: 'query:', document_prefix: 'passage:', embedding_model: 'custom' }
    vi.mocked(api.retrievalSettings).mockResolvedValue(configured)
    vi.mocked(api.saveRetrievalSettings).mockResolvedValue({ ...configured, backend: 'fts5', qdrant_mode: 'local' })
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.change(screen.getByLabelText('Tipo di archivio'), { target: { value: 'local' } })
    expect(screen.queryByLabelText('Indirizzo Qdrant')).not.toBeInTheDocument()
    expect(screen.getByLabelText('Indirizzo Ollama')).toHaveValue(configured.embedding_url)
    fireEvent.change(screen.getByLabelText('Metodo di ricerca'), { target: { value: 'fts5' } })
    expect(screen.queryByRole('region', { name: 'Manutenzione dell’indice' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Salva impostazioni' }))
    await screen.findByText(/La ricerca usa le parole chiave/)
    expect(api.saveRetrievalSettings).toHaveBeenCalledWith({
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
    fireEvent.click(screen.getByRole('button', { name: 'Salva impostazioni' }))
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
    fireEvent.click(screen.getByRole('button', { name: 'Verifica collegamento' }))
    expect(api.checkRetrievalConnection).not.toHaveBeenCalled()
    expect(screen.getByLabelText('Indirizzo Ollama')).toBeInvalid()
  })

  it.each(['save', 'check', 'index'] as const)('shows progress and prevents duplicate %s actions', async (action) => {
    vi.mocked(api.retrievalSettings).mockResolvedValue(vectorSettings)
    let finish = () => {}
    const pending = new Promise<never>((_resolve, reject) => { finish = () => reject(new Error('Test concluso')) })
    const method = { save: api.saveRetrievalSettings, check: api.checkRetrievalConnection, index: api.updateVectorIndex }[action]
    vi.mocked(method).mockReturnValue(pending)
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    const label = { save: 'Salva impostazioni', check: 'Verifica collegamento', index: 'Aggiorna indice' }[action]
    fireEvent.click(screen.getByRole('button', { name: label }))
    expect(screen.getByRole('status')).not.toBeEmptyDOMElement()
    expect(screen.getByLabelText('Metodo di ricerca')).toBeDisabled()
    for (const button of screen.getAllByRole('button')) expect(button).toBeDisabled()
    expect(method).toHaveBeenCalledTimes(1)
    finish()
    expect(await screen.findByRole('alert')).toHaveTextContent('Test concluso')
    expect(screen.getByRole('button', { name: label })).toBeEnabled()
  })

  it('reports a failed save without discarding edits or changing the active model', async () => {
    vi.mocked(api.retrievalSettings).mockResolvedValue(vectorSettings)
    vi.mocked(api.saveRetrievalSettings).mockRejectedValue(new Error('Configurazione non valida'))
    render(<RetrievalSettingsPanel />)
    await openTechnical()
    fireEvent.change(screen.getByLabelText('Modello di embedding'), { target: { value: 'another-model' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salva impostazioni' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Salvataggio non riuscito: Configurazione non valida')
    expect(screen.getByLabelText('Modello di embedding')).toHaveValue('another-model')
    expect(screen.getByText(/Modello attivo:/)).toHaveTextContent('bge-m3')
    expect(screen.getByRole('button', { name: 'Aggiorna indice' })).toBeDisabled()
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
    fireEvent.click(screen.getByRole('button', { name: 'Verifica collegamento' }))
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
    fireEvent.change(screen.getByLabelText('Modello di embedding'), { target: { value: 'text-embedding-3-large' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salva impostazioni' }))
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
