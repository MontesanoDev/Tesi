import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { ProjectDetail } from '../types'
import { ProjectKnowledgePanel } from './ProjectKnowledgePanel'

vi.mock('../api', () => ({
  api: {
    uploadProjectFile: vi.fn(),
    projectFileContent: vi.fn(),
    updateProjectFileContent: vi.fn(),
    projectArtifacts: vi.fn(),
  },
}))

const project: ProjectDetail = {
  id: 'progetto-test',
  title: 'Progetto test',
  description: 'Descrizione',
  status: 'In analisi',
  status_tone: 'info',
  updated_label: 'Aggiornato ora',
  source_count: 0,
  model_count: 0,
  instructions: 'Usa soltanto le fonti.',
  call_fact_count: 0,
  missing_fact_count: 0,
  files: [],
  knowledge_sources: [],
  conversations: [],
}

function renderPanel(
  projectValue: ProjectDetail = project,
  onProjectChange = vi.fn().mockResolvedValue(undefined),
) {
  return render(
    <MemoryRouter>
      <ProjectKnowledgePanel project={projectValue} onProjectChange={onProjectChange} />
    </MemoryRouter>,
  )
}

describe('ProjectKnowledgePanel', () => {
  afterEach(cleanup)

  beforeEach(() => {
    vi.mocked(api.uploadProjectFile).mockReset()
    vi.mocked(api.projectFileContent).mockReset()
    vi.mocked(api.updateProjectFileContent).mockReset()
    vi.mocked(api.projectArtifacts).mockReset()
    vi.mocked(api.projectArtifacts).mockResolvedValue([])
  })

  it('uploads a source and refreshes the project', async () => {
    const onProjectChange = vi.fn().mockResolvedValue(undefined)
    vi.mocked(api.uploadProjectFile).mockResolvedValue({
      id: 3,
      name: 'capitolato.txt',
      metadata: 'TXT · 1 KB · 2 frammenti',
      kind: 'source',
      status: 'Indicizzato',
      page_count: 1,
      chunk_count: 2,
    })
    renderPanel(project, onProjectChange)

    const input = screen.getByLabelText('Seleziona un documento da indicizzare')
    const file = new File(['contenuto tecnico'], 'capitolato.txt', {
      type: 'text/plain',
    })
    fireEvent.change(input, { target: { files: [file] } })

    await waitFor(() => {
      expect(api.uploadProjectFile).toHaveBeenCalledWith(project.id, file)
      expect(onProjectChange).toHaveBeenCalledOnce()
    })
    expect(
      screen.getByText('capitolato.txt indicizzato in 2 frammenti.'),
    ).toBeVisible()
  })

  it('adds handwritten Markdown to the project context', async () => {
    const onProjectChange = vi.fn().mockResolvedValue(undefined)
    vi.mocked(api.uploadProjectFile).mockResolvedValue({
      id: 4,
      name: 'nota-tecnica.md',
      metadata: 'MD · 72 B · 1 frammento',
      kind: 'source',
      status: 'Indicizzato',
      mime_type: 'text/markdown',
      byte_size: 72,
      page_count: 1,
      chunk_count: 1,
    })
    renderPanel(project, onProjectChange)

    fireEvent.click(screen.getByRole('button', { name: 'Aggiungi al contesto' }))
    fireEvent.click(screen.getByRole('button', { name: 'Aggiungi contenuto testuale' }))
    fireEvent.change(screen.getByLabelText('Titolo'), { target: { value: 'Nota tecnica' } })
    fireEvent.change(screen.getByLabelText('Contenuto Markdown'), {
      target: { value: 'Vincolo tecnico verificato.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Aggiungi al progetto' }))

    await waitFor(() => {
      expect(api.uploadProjectFile).toHaveBeenCalledWith(
        project.id,
        expect.objectContaining({ name: 'nota-tecnica.md', type: 'text/markdown' }),
      )
      expect(onProjectChange).toHaveBeenCalledOnce()
    })
  })

  it('dismisses the add menu outside the popover and with Escape', () => {
    renderPanel()

    fireEvent.click(screen.getByRole('button', { name: 'Aggiungi al contesto' }))
    expect(screen.getByRole('button', { name: 'Carica dal dispositivo' })).toBeVisible()
    fireEvent.pointerDown(document.body)
    expect(screen.queryByRole('button', { name: 'Carica dal dispositivo' })).toBeNull()

    fireEvent.click(screen.getByRole('button', { name: 'Aggiungi al contesto' }))
    expect(screen.getByRole('button', { name: 'Carica dal dispositivo' })).toBeVisible()
    fireEvent.keyDown(document, { key: 'Escape' })
    expect(screen.queryByRole('button', { name: 'Carica dal dispositivo' })).toBeNull()
  })

  it('explains invalid handwritten content instead of failing silently', async () => {
    renderPanel()

    fireEvent.click(screen.getByRole('button', { name: 'Aggiungi al contesto' }))
    fireEvent.click(screen.getByRole('button', { name: 'Aggiungi contenuto testuale' }))
    fireEvent.change(screen.getByLabelText('Titolo'), { target: { value: 'AB' } })
    fireEvent.change(screen.getByLabelText('Contenuto Markdown'), {
      target: { value: 'Contenuto valido.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Aggiungi al progetto' }))

    expect(screen.getByRole('alert')).toHaveTextContent(
      'Inserisci un titolo di almeno 3 caratteri',
    )
    expect(api.uploadProjectFile).not.toHaveBeenCalled()
  })

  it('keeps the preparation workflow in the context sidebar', () => {
    renderPanel()

    expect(screen.getByRole('heading', { name: 'Preparazione candidatura' })).toBeVisible()
    expect(screen.getByRole('link', { name: /Call Facts/ })).toBeVisible()
    expect(screen.getByRole('link', { name: /Draft/ })).toBeVisible()
    expect(screen.queryByRole('heading', { name: 'Conoscenza utilizzata' })).toBeNull()
  })

  it('edits and reindexes a text source', async () => {
    const onProjectChange = vi.fn().mockResolvedValue(undefined)
    const textFile = {
      id: 5,
      name: 'requisiti.md',
      metadata: 'MD · 60 B · 1 frammento',
      kind: 'source' as const,
      status: 'Indicizzato',
      mime_type: 'text/markdown',
      byte_size: 60,
      page_count: 1,
      chunk_count: 1,
    }
    vi.mocked(api.projectFileContent).mockResolvedValue({
      ...textFile,
      content: '# Requisiti\n\nVersione iniziale.',
    })
    vi.mocked(api.updateProjectFileContent).mockResolvedValue({
      ...textFile,
      content: '# Requisiti\n\nVersione corretta.',
    })
    renderPanel({ ...project, files: [textFile] }, onProjectChange)

    fireEvent.click(screen.getByRole('button', { name: 'Modifica requisiti.md' }))
    const editor = await screen.findByLabelText('Contenuto Markdown')
    fireEvent.change(editor, { target: { value: '# Requisiti\n\nVersione corretta.' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salva modifiche' }))

    await waitFor(() => {
      expect(api.updateProjectFileContent).toHaveBeenCalledWith(
        project.id,
        textFile.id,
        '# Requisiti\n\nVersione corretta.',
      )
      expect(onProjectChange).toHaveBeenCalledOnce()
    })
  })

})
