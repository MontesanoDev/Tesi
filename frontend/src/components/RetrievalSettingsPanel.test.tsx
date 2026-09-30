import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { RetrievalSettings } from '../types'
import { RetrievalSettingsPanel } from './RetrievalSettingsPanel'

vi.mock('../api', () => ({ api: {
  retrievalSettings: vi.fn(), saveRetrievalSettings: vi.fn(),
  checkRetrievalConnection: vi.fn(), updateVectorIndex: vi.fn(),
} }))

const settings: RetrievalSettings = {
  backend: 'fts5', qdrant_mode: 'local', qdrant_url: 'http://127.0.0.1:6333',
  embedding_url: 'http://127.0.0.1:11434', embedding_model: 'embeddinggemma',
  query_prefix: '', document_prefix: '', has_qdrant_api_key: false, has_embedding_api_key: false,
}

beforeEach(() => {
  vi.resetAllMocks()
  vi.mocked(api.retrievalSettings).mockResolvedValue(settings)
})
afterEach(cleanup)

describe('retrieval settings', () => {
  it('keeps vector connection fields hidden for lexical retrieval', async () => {
    render(<RetrievalSettingsPanel />)
    expect(await screen.findByLabelText('Metodo di ricerca')).toHaveValue('fts5')
    expect(screen.queryByLabelText(/Modello di embedding/)).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Aggiorna indice' })).not.toBeInTheDocument()
  })

  it('saves vector retrieval independently and allows indexing only the saved configuration', async () => {
    vi.mocked(api.saveRetrievalSettings).mockResolvedValue({ ...settings, backend: 'qdrant' })
    vi.mocked(api.updateVectorIndex).mockResolvedValue({ collection: 'test', indexed_chunks: 40,
      updated_chunks: 2, deleted_chunks: 1, dimensions: 768, embedding_digest: 'test' })
    render(<RetrievalSettingsPanel />)
    fireEvent.change(await screen.findByLabelText('Metodo di ricerca'), { target: { value: 'qdrant' } })
    expect(screen.getByRole('button', { name: 'Aggiorna indice' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Salva ricerca' }))
    await waitFor(() => expect(screen.getByRole('button', { name: 'Aggiorna indice' })).toBeEnabled())
    expect(api.saveRetrievalSettings).toHaveBeenCalledWith(expect.objectContaining({ backend: 'qdrant', embedding_model: 'embeddinggemma' }))
    fireEvent.click(screen.getByRole('button', { name: 'Aggiorna indice' }))
    expect(await screen.findByText(/40 frammenti, 2 aggiornati e 1 rimossi/)).toBeVisible()
    fireEvent.change(screen.getByLabelText(/Modello di embedding/), { target: { value: 'other-embedding' } })
    expect(screen.getByRole('button', { name: 'Aggiorna indice' })).toBeDisabled()
  })

  it('checks remote endpoints without saving and clears keys after saving', async () => {
    const remote = { ...settings, backend: 'qdrant' as const, qdrant_mode: 'remote' as const,
      qdrant_url: 'https://qdrant.example', embedding_url: 'https://ollama.example', has_qdrant_api_key: true }
    vi.mocked(api.retrievalSettings).mockResolvedValue(remote)
    vi.mocked(api.checkRetrievalConnection).mockResolvedValue({ message: 'Collegamento riuscito', dimensions: 768 })
    vi.mocked(api.saveRetrievalSettings).mockResolvedValue(remote)
    render(<RetrievalSettingsPanel />)
    const key = await screen.findByLabelText(/Chiave Qdrant/)
    expect(key).toHaveValue('')
    fireEvent.change(key, { target: { value: 'fake-secret' } })
    fireEvent.click(screen.getByRole('button', { name: 'Verifica collegamento' }))
    await screen.findByText('Collegamento riuscito')
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
    expect(api.checkRetrievalConnection).toHaveBeenCalledWith(expect.objectContaining({
      qdrant_url: remote.qdrant_url, embedding_url: remote.embedding_url, qdrant_api_key: 'fake-secret',
    }))
    fireEvent.click(screen.getByRole('button', { name: 'Salva ricerca' }))
    await waitFor(() => expect(key).toHaveValue(''))
    expect(vi.mocked(api.saveRetrievalSettings).mock.calls[0][0]).not.toHaveProperty('has_qdrant_api_key')
  })

  it('keeps the saved configuration and exposes an indexing failure', async () => {
    vi.mocked(api.retrievalSettings).mockResolvedValue({ ...settings, backend: 'qdrant' })
    vi.mocked(api.updateVectorIndex).mockRejectedValue(new Error('Ollama non raggiungibile'))
    render(<RetrievalSettingsPanel />)
    fireEvent.click(await screen.findByRole('button', { name: 'Aggiorna indice' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Ollama non raggiungibile')
    expect(screen.getByLabelText('Metodo di ricerca')).toHaveValue('qdrant')
    expect(screen.getByRole('button', { name: 'Aggiorna indice' })).toBeEnabled()
    expect(api.saveRetrievalSettings).not.toHaveBeenCalled()
  })
})
