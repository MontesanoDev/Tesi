import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { createMemoryRouter, RouterProvider } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { KnowledgeArtifactDetail } from '../types'
import { KnowledgeArtifactsPage } from './KnowledgeArtifactsPage'

vi.mock('../api', () => ({ api: {
  project: vi.fn(), projectArtifacts: vi.fn(), projectArtifact: vi.fn(), callFactsReview: vi.fn(),
  documentCompilations: vi.fn(),
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

function setup(kind = 'template') {
  const router = createMemoryRouter([
    { path: '/projects/:projectId/knowledge', element: <KnowledgeArtifactsPage /> },
  ], { initialEntries: [`/projects/primo/knowledge?artifact=${kind}`] })
  render(<RouterProvider router={router} />)
  return router
}

describe('unified Template navigation', () => {
  afterEach(() => { cleanup(); vi.restoreAllMocks() })
  beforeEach(() => {
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
    vi.mocked(api.callFactsReview).mockReset().mockImplementation(async (id) => ({
      artifact: artifacts(id)[0], facts: [], missing_information: [],
      pending_count: 0, verified_count: 0, discarded_count: 0,
    }))
  })

  it('opens old Draft links in the compilation tab of Template', async () => {
    setup('output_draft')
    expect(await screen.findByRole('heading', { name: 'Compilazione primo' })).toBeVisible()
    expect(screen.getByRole('heading', { name: 'Template' })).toBeVisible()
    expect(screen.getByRole('tab', { name: 'Compilazione' })).toHaveAttribute('aria-selected', 'true')
    const nav = within(screen.getByRole('navigation', { name: 'Preparazione candidatura' }))
    expect(nav.queryByRole('button', { name: /Draft/ })).not.toBeInTheDocument()
    expect(nav.getByRole('button', { name: /Template/ })).toHaveClass('is-active')
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
    fireEvent.click(screen.getByRole('button', { name: /Dati del progetto/ }))
    expect(screen.getByRole('textbox')).toHaveValue('# Non perdere')
    expect(api.callFactsReview).not.toHaveBeenCalled()
    vi.mocked(window.confirm).mockReturnValue(true)
    fireEvent.click(screen.getByRole('button', { name: /Dati del progetto/ }))
    await waitFor(() => expect(api.callFactsReview).toHaveBeenCalled())
    expect(screen.getByRole('tab', { name: 'Dati estratti' })).toBeVisible()
  })

  it('opens legacy Call Facts links in the unified project data view', async () => {
    setup('call_facts')
    expect(await screen.findByRole('heading', { name: 'Dati del progetto' })).toBeVisible()
    expect(screen.getByRole('tab', { name: 'Dati estratti' })).toBeVisible()
    const nav = within(screen.getByRole('navigation', { name: 'Preparazione candidatura' }))
    expect(nav.getAllByRole('button')).toHaveLength(2)
    expect(nav.queryByText('Call Facts')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('tab', { name: 'Dati inseriti' }))
    expect(screen.getByRole('textbox')).toHaveValue('# Dati inseriti primo')
  })

  it('opens Word by default and preserves the existing text compilation', async () => {
    setup()
    expect(await screen.findByRole('button', { name: 'Carica modello' })).toBeVisible()
    fireEvent.change(screen.getByLabelText('Formato template'), { target: { value: 'text' } })
    expect(await screen.findByRole('heading', { name: 'Compilazione primo' })).toBeVisible()
    fireEvent.click(screen.getByRole('tab', { name: 'Modello' }))
    expect(screen.getByRole('heading', { name: 'Modello primo' })).toBeVisible()
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

  it('ignores extracted facts arriving after switching to a different project', async () => {
    let resolve!: (value: Awaited<ReturnType<typeof api.callFactsReview>>) => void
    const data = (id: string) => ({
      artifact: artifacts(id)[0], pending_count: 1, verified_count: 0, discarded_count: 0,
      missing_information: [], facts: [{ id: `cf-${id}`, title: `Dato ${id}`, value: 'Valore',
        status: 'pending' as const, sources: [{ name: `${id}.pdf`, fragment: 1 }] }],
    })
    vi.mocked(api.callFactsReview).mockImplementation(async (id) => id === 'primo'
      ? new Promise((done) => { resolve = done }) : data(id))
    const router = setup('project_facts')
    await waitFor(() => expect(resolve).toBeDefined())
    await act(async () => { await router.navigate('/projects/secondo/knowledge?artifact=project_facts') })
    expect(await screen.findByRole('heading', { name: 'Dato secondo' })).toBeVisible()
    await act(async () => resolve(data('primo')))
    expect(screen.queryByRole('heading', { name: 'Dato primo' })).not.toBeInTheDocument()
    expect(screen.getByText('secondo.pdf, frammento 1')).toBeVisible()
  })
})
