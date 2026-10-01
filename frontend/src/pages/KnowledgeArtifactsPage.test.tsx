import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { createMemoryRouter, RouterProvider } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { KnowledgeArtifactDetail } from '../types'
import { KnowledgeArtifactsPage } from './KnowledgeArtifactsPage'

vi.mock('../api', () => ({ api: {
  project: vi.fn(), projectArtifacts: vi.fn(), projectArtifact: vi.fn(),
  documentCompilations: vi.fn(),
  aiSettings: vi.fn(), projectAiModel: vi.fn(), setProjectAiModel: vi.fn(),
} }))

function artifacts(id: string): KnowledgeArtifactDetail[] {
  return [
    { kind: 'call_facts', title: 'Call Facts', content: '# Fatti verificati' },
    { kind: 'template', title: 'Template', content: `# Modello ${id}` },
    { kind: 'output_draft', title: 'Draft', content: `# Compilazione ${id}` },
    { kind: 'project_facts', title: 'Project Facts', content: `# Dati inseriti ${id}` },
  ].map((item) => ({ ...item, id: `${id}--${item.kind}`, filename: `${item.kind}.md`,
    scope: 'project', status: 'Da verificare', version: 2, byte_size: 100,
    chunk_count: 1, editable: true, updated_at: '',
  }))
}

function setup(kind: string | null = 'template') {
  const router = createMemoryRouter([
    { path: '/projects/:projectId/knowledge', element: <KnowledgeArtifactsPage /> },
    { path: '/projects/:projectId', element: <div>Vista progetto</div> },
  ], { initialEntries: [`/projects/primo/knowledge${kind ? `?artifact=${kind}` : ''}`] })
  render(<RouterProvider router={router} />)
  return router
}

describe('unified Template navigation', () => {
  afterEach(() => { cleanup(); vi.restoreAllMocks() })
  beforeEach(() => {
    vi.mocked(api.aiSettings).mockReset().mockResolvedValue({ profiles: [], default_profile_id: null })
    vi.mocked(api.projectAiModel).mockReset().mockResolvedValue({ profile_id: null, effective_profile: null })
    vi.mocked(api.documentCompilations).mockReset().mockResolvedValue([])
    vi.mocked(api.project).mockReset().mockImplementation(async (id) => ({
      id, title: `Progetto ${id}`, description: '', status: 'In analisi', status_tone: 'info',
      updated_label: '', source_count: 0, model_count: 0, instructions: '',
      call_fact_count: 0, missing_fact_count: 0, files: [], knowledge_sources: [], conversations: [],
    }))
    vi.mocked(api.projectArtifacts).mockReset().mockImplementation(async (id) => artifacts(id))
    vi.mocked(api.projectArtifact).mockReset().mockImplementation(async (id, artifactId) => (
      artifacts(id).find((item) => item.id === artifactId)!
    ))
  })

  it('opens old Draft links in the compilation tab of Template', async () => {
    setup('output_draft')
    expect(await screen.findByRole('heading', { name: 'Compilazione primo' })).toBeVisible()
    expect(screen.getByRole('heading', { name: 'Template' })).toBeVisible()
    expect(screen.getByRole('tab', { name: 'Compilazione' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.queryByRole('navigation', { name: 'Preparazione candidatura' })).not.toBeInTheDocument()
  })

  it('allows cancelling navigation with unsaved changes, without altering project data', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(false)
    setup()
    fireEvent.change(await screen.findByLabelText('Formato template'), { target: { value: 'text' } })
    await screen.findByRole('heading', { name: 'Compilazione primo' })
    fireEvent.click(screen.getByRole('tab', { name: 'Modello' }))
    await screen.findByRole('heading', { name: 'Modello primo' })
    fireEvent.click(screen.getByRole('button', { name: 'Modifica testo' }))
    fireEvent.change(screen.getByRole('textbox'), { target: { value: '# Non perdere' } })
    fireEvent.click(screen.getByRole('button', { name: /Progetto primo/ }))
    expect(screen.getByRole('textbox')).toHaveValue('# Non perdere')
    vi.mocked(window.confirm).mockReturnValue(true)
    fireEvent.click(screen.getByRole('button', { name: /Progetto primo/ }))
    expect(await screen.findByText('Vista progetto')).toBeVisible()
  })

  it.each([null, 'call_facts', 'project_facts'])('opens %s links directly in Template', async (kind) => {
    setup(kind)
    expect(await screen.findByRole('button', { name: 'Carica modello' })).toBeVisible()
    expect(screen.getByRole('heading', { name: 'Template' })).toBeVisible()
    expect(screen.queryByRole('tab', { name: 'Dati estratti' })).not.toBeInTheDocument()
    expect(screen.queryByRole('tab', { name: 'Dati inseriti' })).not.toBeInTheDocument()
    expect(api.projectArtifact).toHaveBeenCalledWith('primo', 'primo--template', expect.any(AbortSignal))
  })

  it('opens Word by default and preserves the existing text compilation', async () => {
    setup()
    expect(await screen.findByRole('button', { name: 'Carica modello' })).toBeVisible()
    fireEvent.change(screen.getByLabelText('Formato template'), { target: { value: 'text' } })
    expect(await screen.findByRole('heading', { name: 'Compilazione primo' })).toBeVisible()
    fireEvent.click(screen.getByRole('tab', { name: 'Modello' }))
    expect(screen.getByRole('heading', { name: 'Modello primo' })).toBeVisible()
  })

  it('keeps Word upload and instructions without another AI model selector', async () => {
    setup()
    await screen.findByRole('button', { name: 'Carica modello' })
    fireEvent.change(screen.getByLabelText('Carica modello DOCX'), { target: {
      files: [new File(['document'], 'domanda.docx', { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })],
    } })
    fireEvent.change(screen.getByLabelText(/Indicazioni per la compilazione/), { target: { value: 'Mantieni queste indicazioni' } })
    expect(screen.queryByRole('combobox', { name: 'Modello AI' })).not.toBeInTheDocument()
    expect(api.projectAiModel).not.toHaveBeenCalled()
    expect(api.aiSettings).not.toHaveBeenCalled()
    expect(screen.getByText('domanda.docx', { exact: true })).toBeVisible()
    expect(screen.getByLabelText(/Indicazioni per la compilazione/)).toHaveValue('Mantieni queste indicazioni')
    expect(screen.getByRole('button', { name: 'Compila Word' })).toBeEnabled()
  })

  it('never shows a late compilation from a different project', async () => {
    let resolve!: (item: KnowledgeArtifactDetail) => void
    vi.mocked(api.projectArtifact).mockImplementation(async (id, artifactId) => {
      if (id === 'primo' && artifactId.endsWith('--output_draft')) {
        return new Promise((done) => { resolve = done })
      }
      return artifacts(id).find((item) => item.id === artifactId)!
    })
    const router = setup('output_draft')
    await waitFor(() => expect(resolve).toBeDefined())
    await act(async () => { await router.navigate('/projects/secondo/knowledge?artifact=output_draft') })
    await screen.findByRole('heading', { name: 'Compilazione secondo' })
    await act(async () => resolve(artifacts('primo')[2]))
    expect(screen.queryByRole('heading', { name: 'Compilazione primo' })).not.toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Compilazione secondo' })).toBeVisible()
  })

  it('ignores a template arriving after switching to another project', async () => {
    let resolve!: (item: KnowledgeArtifactDetail) => void
    vi.mocked(api.projectArtifact).mockImplementation(async (id, artifactId) => {
      if (id === 'primo') return new Promise((done) => { resolve = done })
      return artifacts(id).find((item) => item.id === artifactId)!
    })
    const router = setup()
    await waitFor(() => expect(resolve).toBeDefined())
    await act(async () => { await router.navigate('/projects/secondo/knowledge') })
    fireEvent.change(await screen.findByLabelText('Formato template'), { target: { value: 'text' } })
    await screen.findByRole('heading', { name: 'Compilazione secondo' })
    fireEvent.click(screen.getByRole('tab', { name: 'Modello' }))
    await screen.findByRole('heading', { name: 'Modello secondo' })
    await act(async () => resolve(artifacts('primo')[1]))
    expect(screen.queryByRole('heading', { name: 'Modello primo' })).not.toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Modello secondo' })).toBeVisible()
  })

  it('reports a missing template instead of loading indefinitely', async () => {
    vi.mocked(api.projectArtifacts).mockResolvedValue(artifacts('primo').filter((item) => item.kind !== 'template'))
    setup()
    expect(await screen.findByRole('alert')).toHaveTextContent('Template non disponibile')
    expect(screen.queryByText('Caricamento template')).not.toBeInTheDocument()
  })
})
