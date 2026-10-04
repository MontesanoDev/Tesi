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
    deleteProjectFile: vi.fn(),
    projectArtifacts: vi.fn(),
    documentCompilations: vi.fn(),
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
    vi.mocked(api.documentCompilations).mockReset().mockResolvedValue([])
    vi.mocked(api.uploadProjectFile).mockReset()
    vi.mocked(api.projectFileContent).mockReset()
    vi.mocked(api.updateProjectFileContent).mockReset()
    vi.mocked(api.deleteProjectFile).mockReset()
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
    fireEvent.change(screen.getByLabelText('Contenuto testuale'), {
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
    fireEvent.change(screen.getByLabelText('Contenuto testuale'), {
      target: { value: 'Contenuto valido.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Aggiungi al progetto' }))

    expect(screen.getByRole('alert')).toHaveTextContent(
      'Inserisci un titolo di almeno 3 caratteri',
    )
    expect(api.uploadProjectFile).not.toHaveBeenCalled()
  })

  it('keeps only source management in the context sidebar', () => {
    renderPanel()

    expect(screen.queryByRole('heading', { name: 'Preparazione candidatura' })).not.toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /Call Facts/ })).not.toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /Moduli e bozze/ })).not.toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /Draft/ })).not.toBeInTheDocument()
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
    const editor = await screen.findByLabelText('Contenuto testuale')
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

  const source = {
    id: 7, name: 'bando.pdf', metadata: 'PDF', kind: 'source' as const,
    status: 'Indicizzato', mime_type: 'application/pdf', page_count: 1, chunk_count: 2,
  }

  it.each(['bando.pdf', 'nota.txt', 'contenuto.md'])('deletes %s only after confirmation', async (name) => {
    const onProjectChange = vi.fn().mockResolvedValue(undefined)
    vi.mocked(api.deleteProjectFile).mockResolvedValue(undefined)
    renderPanel({ ...project, files: [{ ...source, name }] }, onProjectChange)
    fireEvent.click(screen.getByRole('button', { name: `Elimina ${name}` }))
    expect(screen.getByRole('dialog', { name: 'Elimina fonte' })).toBeVisible()
    expect(api.deleteProjectFile).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Elimina fonte' }))
    await waitFor(() => expect(onProjectChange).toHaveBeenCalledOnce())
    expect(api.deleteProjectFile).toHaveBeenCalledWith(project.id, source.id)
    expect(screen.queryByRole('dialog')).toBeNull()
    expect(screen.getByText(`${name} eliminato dal progetto e dall'indice.`)).toBeVisible()
  })

  it.each(['cancel', 'escape', 'outside'])('cancels deletion through %s without a request', (action) => {
    renderPanel({ ...project, files: [source] })
    const trigger = screen.getByRole('button', { name: 'Elimina bando.pdf' })
    fireEvent.click(trigger)
    if (action === 'cancel') fireEvent.click(screen.getByRole('button', { name: 'Annulla' }))
    else if (action === 'escape') fireEvent.keyDown(screen.getByRole('button', { name: 'Annulla' }), { key: 'Escape' })
    else fireEvent.click(screen.getByRole('button', { name: 'Chiudi conferma eliminazione fonte' }))
    expect(screen.queryByRole('dialog')).toBeNull()
    expect(api.deleteProjectFile).not.toHaveBeenCalled()
    expect(trigger).toHaveFocus()
  })

  it('keeps the file visible and lets the user retry after an error', async () => {
    const onProjectChange = vi.fn().mockResolvedValue(undefined)
    vi.mocked(api.deleteProjectFile).mockRejectedValueOnce(new Error('Eliminazione non riuscita'))
      .mockResolvedValueOnce(undefined)
    renderPanel({ ...project, files: [source] }, onProjectChange)
    fireEvent.click(screen.getByRole('button', { name: 'Elimina bando.pdf' }))
    fireEvent.click(screen.getByRole('button', { name: 'Elimina fonte' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Eliminazione non riuscita')
    expect(screen.getByRole('dialog')).toBeVisible()
    expect(onProjectChange).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Elimina fonte' }))
    await waitFor(() => expect(onProjectChange).toHaveBeenCalledOnce())
  })

  it('disables repeated deletion and other source changes while deleting', async () => {
    let resolveDeletion!: () => void
    vi.mocked(api.deleteProjectFile).mockImplementation(() => new Promise<void>((resolve) => {
      resolveDeletion = resolve
    }))
    renderPanel({ ...project, files: [{ ...source, mime_type: 'text/plain' }] })
    fireEvent.click(screen.getByRole('button', { name: 'Elimina bando.pdf' }))
    fireEvent.click(screen.getByRole('button', { name: 'Elimina fonte' }))
    expect(screen.getByRole('button', { name: 'Eliminazione' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Annulla' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Aggiungi al contesto' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Modifica bando.pdf' })).toBeDisabled()
    expect(api.deleteProjectFile).toHaveBeenCalledOnce()
    resolveDeletion()
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull())
  })

  it('distinguishes a refresh error from a failed deletion', async () => {
    vi.mocked(api.deleteProjectFile).mockResolvedValue(undefined)
    renderPanel({ ...project, files: [source] }, vi.fn().mockRejectedValue(new Error('Offline')))
    fireEvent.click(screen.getByRole('button', { name: 'Elimina bando.pdf' }))
    fireEvent.click(screen.getByRole('button', { name: 'Elimina fonte' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Fonte eliminata, ma la lista non si aggiorna')
    expect(screen.queryByRole('dialog')).toBeNull()
  })

  it('does not offer deletion for a workflow template', () => {
    renderPanel({ ...project, files: [{ ...source, kind: 'template' }] })
    expect(screen.queryByRole('button', { name: 'Elimina bando.pdf' })).toBeNull()
  })

})
